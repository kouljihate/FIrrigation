"""Geometry section: Sectors, Zones, Valves."""
from __future__ import annotations

import math
from datetime import datetime, timezone

import numpy as np
from flask import (
    Blueprint, current_app, flash, redirect, render_template,
    request, session, url_for,
)
from shapely.geometry import Polygon
from shapely.validation import make_valid

from core.geometry import clean_polygon, fall_direction
from core.valve_rules import MV_GROUPS, zv_name
from db import queries, repository
from db.connection import get_db


bp = Blueprint("geometry", __name__, url_prefix="/geometry")


# ---------------------------------------------------------------- sectors
@bp.route("/sectors")
def sectors():
    pid = session.get("project_id", "farm_v1")
    rows = queries.get_sectors(pid)
    table = []
    for s in rows:
        ring = s["geom"]["coordinates"][0]
        table.append({
            "code": s.get("sector_code") or s["name"],
            "vertices": len(ring),
            "area_m2": round(s.get("area_m2", 0), 1),
        })
    return render_template("geometry/sectors.html", sectors=table)


# ---------------------------------------------------------------- zones
@bp.route("/zones", methods=["GET", "POST"])
def zones():
    pid = session.get("project_id", "farm_v1")

    if request.method == "POST":
        try:
            n_parts = int(request.form.get("n_parts", 3))
            offset = float(request.form.get("offset", 0))
        except ValueError:
            flash("Invalid numeric input.", "error")
            return redirect(url_for("geometry.zones"))

        _build_zones(pid, n_parts, offset)
        flash("Zones built.", "success")
        return redirect(url_for("geometry.zones"))

    rows = queries.get_zones(pid)
    table = []
    for z in rows:
        table.append({
            "name": z["name"],
            "sector": z.get("sector_code", ""),
            "area_m2": round(z.get("area_m2", 0), 1),
        })
    return render_template("geometry/zones.html", zones=table)


def _build_zones(project_id: str, n_parts: int, offset: float) -> None:
    sectors = queries.get_sectors(project_id)
    if not sectors:
        flash("No sectors found. Run Step 01 first.", "error")
        return

    db = get_db()
    revision = repository.new_revision(project_id, "04_zones",
                                       f"Build {n_parts} zones/sector")
    repository.clear_step(project_id, "zones")

    now = datetime.now(timezone.utc)
    R = 6371000.0
    total = 0

    for s in sectors:
        code = s.get("sector_code") or s["name"]
        ring = s["geom"]["coordinates"][0]
        pts_ll = [(x, y, 0.0) for x, y in ring]

        lon0 = sum(p[0] for p in pts_ll) / len(pts_ll)
        lat0 = sum(p[1] for p in pts_ll) / len(pts_ll)

        def to_local(lon, lat):
            x = math.radians(lon - lon0) * R * math.cos(math.radians(lat0))
            y = math.radians(lat - lat0) * R
            return x, y

        pts_xy = [to_local(p[0], p[1]) for p in pts_ll]
        poly = clean_polygon(Polygon(pts_xy))

        ux, uy = fall_direction(poly, [0.0] * len(pts_xy))

        theta = -math.pi / 2 - math.atan2(uy, ux)
        c, s_ = math.cos(theta), math.sin(theta)

        def rot(p):
            return (c * p[0] - s_ * p[1], s_ * p[0] + c * p[1])

        def rot_inv(p):
            return (c * p[0] + s_ * p[1], -s_ * p[0] + c * p[1])

        rot_poly = Polygon([rot(p) for p in poly.exterior.coords])
        if not rot_poly.is_valid:
            rot_poly = make_valid(rot_poly)
        if offset > 0:
            rot_poly = rot_poly.buffer(-offset, join_style=2)
            if rot_poly.is_empty:
                continue
            if rot_poly.geom_type == "MultiPolygon":
                rot_poly = max(rot_poly.geoms, key=lambda g: g.area)

        minx, miny, maxx, maxy = rot_poly.bounds
        target = rot_poly.area / n_parts

        def area_below(ycut):
            box = Polygon([(minx - 50, miny - 50),
                           (maxx + 50, miny - 50),
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
            box = Polygon([(minx - 50, y_lo), (maxx + 50, y_lo),
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
                {"project_id": project_id, "name": zname,
                 "sector_code": code, "zone_index": j + 1,
                 "geom": geom, "area_m2": zone.area,
                 "fall_dir_deg": math.degrees(math.atan2(uy, ux)),
                 "revision_id": revision,
                 "created_at": now, "updated_at": now})
            total += 1

    current_app.logger.info("Built %d zones for %s", total, project_id)


# ---------------------------------------------------------------- valves
@bp.route("/valves", methods=["GET", "POST"])
def valves():
    pid = session.get("project_id", "farm_v1")

    if request.method == "POST":
        _build_valves(pid)
        flash("Valves built.", "success")
        return redirect(url_for("geometry.valves"))

    mvs = queries.get_valves(pid, "MV")
    zvs = queries.get_valves(pid, "ZV")
    return render_template("geometry/valves.html", mvs=mvs, zvs=zvs)


def _build_valves(project_id: str) -> None:
    sectors = queries.get_sectors(project_id)
    zones = queries.get_zones(project_id)
    if not sectors or not zones:
        flash("Need sectors and zones first.", "error")
        return

    revision = repository.new_revision(project_id, "05_valves", "Generate valves")
    repository.clear_step(project_id, "valves")

    now = datetime.now(timezone.utc)

    for mv, sector_codes in MV_GROUPS.items():
        first = sector_codes[0]
        sdoc = next((s for s in sectors
                     if (s.get("sector_code") or s["name"]) == first), None)
        if not sdoc:
            continue
        ring = sdoc["geom"]["coordinates"][0]
        lon = sum(p[0] for p in ring) / len(ring)
        lat = sum(p[1] for p in ring) / len(ring)
        repository.upsert("valves",
            {"project_id": project_id, "name": mv},
            {"project_id": project_id, "name": mv, "valve_type": "MV",
             "sector_code": first,
             "location": {"type": "Point", "coordinates": [lon, lat]},
             "diameter_mm": 50, "revision_id": revision,
             "created_at": now, "updated_at": now})

    for z in zones:
        code = z["sector_code"]
        zi = z["zone_index"]
        ring = z["geom"]["coordinates"][0]
        lon = sum(p[0] for p in ring) / len(ring)
        lat = sum(p[1] for p in ring) / len(ring)
        name = zv_name(code, zi)
        repository.upsert("valves",
            {"project_id": project_id, "name": name},
            {"project_id": project_id, "name": name, "valve_type": "ZV",
             "sector_code": code, "zone_name": z["name"],
             "location": {"type": "Point", "coordinates": [lon, lat]},
             "diameter_mm": 32, "revision_id": revision,
             "created_at": now, "updated_at": now})