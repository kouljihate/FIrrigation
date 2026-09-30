"""Step 08 — Rows inside each zone."""
from __future__ import annotations

import math
from datetime import datetime, timezone

import numpy as np
import streamlit as st
from shapely.geometry import Polygon

from core.geometry import clean_polygon, fall_direction
from core.rows import build_rows
from db import queries, repository
from db.connection import get_db


def render():
    st.header("Step 08 — Rows")
    st.caption("Trace rows inside each zone, perpendicular to the fall line.")

    project_id = st.session_state.get("project_id", "dhar_v1")
    spacing = st.number_input("Row spacing (m)", 1.0, 20.0, 4.0)
    offset = st.number_input("First row offset from top (m)", 0.0, 20.0, 2.0)

    if st.button("Build rows", type="primary"):
        _build(project_id, float(spacing), float(offset))


def _build(project_id: str, spacing: float, offset: float) -> None:
    zones = queries.get_zones(project_id)
    if not zones:
        st.error("No zones. Run Step 04 first.")
        return

    db = get_db()
    revision = repository.new_revision(project_id, "08_rows", "Build rows")
    repository.clear_step(project_id, "rows")

    now = datetime.now(timezone.utc)
    R = 6371000.0
    total_rows = 0

    for z in zones:
        ring = z["geom"]["coordinates"][0]
        lon0 = sum(p[0] for p in ring) / len(ring)
        lat0 = sum(p[1] for p in ring) / len(ring)

        def to_local(lon, lat):
            x = math.radians(lon - lon0) * R * math.cos(math.radians(lat0))
            y = math.radians(lat - lat0) * R
            return x, y

        def to_lonlat(x, y):
            return (lon0 + math.degrees(x / (R * math.cos(math.radians(lat0)))),
                    lat0 + math.degrees(y / R))

        pts_xy = [to_local(p[0], p[1]) for p in ring]
        poly = clean_polygon(Polygon(pts_xy))
        elevs = [0.0] * len(pts_xy)
        ux, uy = fall_direction(poly, elevs)

        rows = build_rows(poly, ux, uy, spacing, offset)
        for (ri, seg) in rows:
            seg_ll = [list(to_lonlat(x, y)) for x, y in seg]
            name = f"{z['name']}-R{ri+1:02d}"
            length = math.hypot(seg_ll[1][0] - seg_ll[0][0],
                                seg_ll[1][1] - seg_ll[0][1]) * 111000.0 * 0.85
            repository.upsert("rows",
                {"project_id": project_id, "name": name},
                {
                    "project_id": project_id,
                    "name": name,
                    "zone_name": z["name"],
                    "row_index": ri + 1,
                    "geom": {"type": "LineString",
                             "coordinates": [list(p) for p in seg_ll]},
                    "length_m": length,
                    "row_direction_deg": math.degrees(math.atan2(uy, ux)),
                    "revision_id": revision,
                    "created_at": now,
                    "updated_at": now,
                })
            total_rows += 1

    st.success(f"Created {total_rows} rows (revision {revision})")