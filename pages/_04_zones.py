"""Step 04 — Divide each sector into 3 equal-area zones."""
from __future__ import annotations

import math
from datetime import datetime, timezone

import numpy as np
import streamlit as st
from shapely.geometry import Polygon, LineString, mapping
from shapely.validation import make_valid

from core.geometry import fall_direction, clean_polygon
from db import queries, repository
from db.connection import get_db

import yaml
import os


def render():
    st.header("Step 04 — Zones")
    st.caption("Split each sector into 3 equal-area zones with cut lines "
               "perpendicular to the fall line.")

    project_id = st.session_state.get("project_id", "dhar_v1")

    cfg_path = "configs/04_zones.yaml"
    cfg = {}
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

    n_parts = st.number_input("Zones per sector", 2, 10,
                              value=cfg.get("n_per_sector", 3))
    offset = st.number_input("Inward offset (m)", 0.0, 20.0,
                             value=float(cfg.get("offset_inward_m", 0.0)))

    if st.button("Build zones", type="primary"):
        _build(project_id, int(n_parts), float(offset))


def _build(project_id: str, n_parts: int, offset: float) -> None:
    sectors = queries.get_sectors(project_id)
    if not sectors:
        st.error("No sectors. Run Step 01 first.")
        return

    db = get_db()
    revision = repository.new_revision(project_id, "04_zones",
                                       f"Build {n_parts} zones/sector")

    # wipe existing zones for this project
    repository.clear_step(project_id, "zones")

    now = datetime.now(timezone.utc)
    total_zones = 0

    progress = st.progress(0.0)
    status = st.empty()

    for i, s in enumerate(sectors):
        code = s.get("sector_code") or s["name"]
        ring = s["geom"]["coordinates"][0]
        pts_ll = [(x, y, 0.0) for x, y in ring]

        # local projection
        lon0 = sum(p[0] for p in pts_ll) / len(pts_ll)
        lat0 = sum(p[1] for p in pts_ll) / len(pts_ll)

        R = 6371000.0
        def to_local(lon, lat):
            x = math.radians(lon - lon0) * R * math.cos(math.radians(lat0))
            y = math.radians(lat - lat0) * R
            return x, y

        pts_xy = [to_local(p[0], p[1]) for p in pts_ll]
        poly = clean_polygon(Polygon(pts_xy))

        # fall direction: needs elevations — use 0 (auto falls back to east)
        # If sectors carry elevations later, replace here.
        elevs = [0.0] * len(pts_xy)
        ux, uy = fall_direction(poly, elevs)

        theta = -math.pi / 2 - math.atan2(uy, ux)
        c, s = math.cos(theta), math.sin(theta)

        def rot(p):
            return (c * p[0] - s * p[1], s * p[0] + c * p[1])

        def rot_inv(p):
            return (c * p[0] + s * p[1], -s * p[0] + c * p[1])

        rot_poly = Polygon([rot(p) for p in poly.exterior.coords])
        if not rot_poly.is_valid:
            rot_poly = make_valid(rot_poly)
        if offset > 0:
            rot_poly = rot_poly.buffer(-offset, join_style=2)
            if rot_poly.is_empty:
                st.warning(f"{code}: offset too large, skipping")
                continue
            if rot_poly.geom_type == "MultiPolygon":
                rot_poly = max(rot_poly.geoms, key=lambda g: g.area)

        minx, miny, maxx, maxy = rot_poly.bounds
        target = rot_poly.area / n_parts

        def area_below(ycut):
            from shapely.geometry import Polygon as P
            box = P([(minx - 50, miny - 50), (maxx + 50, miny - 50),
                     (maxx + 50, ycut), (minx - 50, ycut)])
            return rot_poly.intersection(box).area

        cuts = []
        for k in range(1, n_parts):
            lo, hi = miny, maxy
            tgt = target * k
            for _ in range(60):
                mid = (lo + hi) / 2
                if area_below(mid) < tgt:
                    lo = mid
                else:
                    hi = mid
            cuts.append((lo + hi) / 2)
        cuts.sort()

        edges = [miny - 50] + cuts + [maxy + 50]
        for j in range(n_parts):
            y_lo = edges[n_parts - j - 1]
            y_hi = edges[n_parts - j]
            from shapely.geometry import Polygon as P
            box = P([(minx - 50, y_lo), (maxx + 50, y_lo),
                     (maxx + 50, y_hi), (minx - 50, y_hi)])
            zone = rot_poly.intersection(box)
            if zone.is_empty:
                continue
            if zone.geom_type == "MultiPolygon":
                zone = max(zone.geoms, key=lambda g: g.area)
            if zone.geom_type != "Polygon":
                continue

            back_pts = [rot_inv(p) for p in zone.exterior.coords]

            def to_lonlat(x, y):
                lon = lon0 + math.degrees(x / (R * math.cos(math.radians(lat0))))
                lat = lat0 + math.degrees(y / R)
                return lon, lat

            ring_ll = [list(to_lonlat(x, y)) for x, y in back_pts]
            if ring_ll[0] != ring_ll[-1]:
                ring_ll.append(ring_ll[0])

            geom = {"type": "Polygon", "coordinates": [ring_ll]}
            zname = f"{code}-Z{j + 1}"
            repository.upsert("zones",
                {"project_id": project_id, "name": zname},
                {
                    "project_id": project_id,
                    "name": zname,
                    "sector_code": code,
                    "zone_index": j + 1,
                    "geom": geom,
                    "area_m2": zone.area,
                    "fall_dir_deg": math.degrees(math.atan2(uy, ux)),
                    "revision_id": revision,
                    "created_at": now,
                    "updated_at": now,
                })
            total_zones += 1

        progress.progress((i + 1) / len(sectors))
        status.text(f"Processed {code}")

    st.success(f"Built {total_zones} zones (revision {revision})")