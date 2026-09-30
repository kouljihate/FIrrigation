"""Step 06 — Mainline pipe from basin to MV1, MV2, MV3."""
from __future__ import annotations

import math
from datetime import datetime, timezone

import streamlit as st
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import nearest_points

from core.geometry import clean_polygon, inward_offset
from core.piping import direct_or_detour
from db import queries, repository
from db.connection import get_db


def render():
    st.header("Step 06 — Mainline")
    st.caption("Route the mainline from the basin to MV1, MV2, MV3, staying "
               "inside P1.")

    project_id = st.session_state.get("project_id", "dhar_v1")
    offset = st.number_input("Inward offset from P1 (m)", 1.0, 30.0, 5.0)
    diameter = st.number_input("Diameter (mm)", 32, 200, 75)

    if st.button("Build mainline", type="primary"):
        _build(project_id, float(offset), int(diameter))


def _build(project_id: str, offset: float, diameter: int) -> None:
    db = get_db()

    prop = db.property.find_one({"project_id": project_id})
    basin = db.basins.find_one({"project_id": project_id})
    mvs = {v["name"]: v for v in queries.get_valves(project_id, "MV")}

    if not prop or not basin or not mvs:
        st.error("Need P1, a basin, and MV valves. Run earlier steps first.")
        return

    # project P1 to local xy
    p1_ring = prop["geom"]["coordinates"][0]
    lon0 = sum(p[0] for p in p1_ring) / len(p1_ring)
    lat0 = sum(p[1] for p in p1_ring) / len(p1_ring)
    R = 6371000.0

    def to_local(lon, lat):
        x = math.radians(lon - lon0) * R * math.cos(math.radians(lat0))
        y = math.radians(lat - lat0) * R
        return x, y

    def to_lonlat(x, y):
        lon = lon0 + math.degrees(x / (R * math.cos(math.radians(lat0))))
        lat = lat0 + math.degrees(y / R)
        return lon, lat

    p1_xy = clean_polygon(Polygon([to_local(p[0], p[1]) for p in p1_ring]))
    inner = inward_offset(p1_xy, offset)

    basin_ring = basin["geom"]["coordinates"][0]
    b_lon = sum(p[0] for p in basin_ring) / len(basin_ring)
    b_lat = sum(p[1] for p in basin_ring) / len(basin_ring)
    basin_xy = to_local(b_lon, b_lat)

    revision = repository.new_revision(project_id, "06_mainline",
                                       f"Mainline offset={offset}m Ø{diameter}")
    repository.delete_where("pipes", {"project_id": project_id, "pipe_type": "mainline"})

    now = datetime.now(timezone.utc)
    n = 0
    for mv_name, mv in mvs.items():
        mv_lon, mv_lat = mv["location"]["coordinates"]
        mv_xy = to_local(mv_lon, mv_lat)
        path = direct_or_detour(p1_xy, inner, basin_xy, mv_xy)
        path_ll = [list(to_lonlat(x, y)) for x, y in path]

        length = sum(
            math.hypot(path_ll[i+1][0] - path_ll[i][0],
                       path_ll[i+1][1] - path_ll[i][1]) * 111000.0 * 0.85
            for i in range(len(path_ll) - 1)
        )

        name = f"MAIN-BASIN-{mv_name}"
        repository.upsert("pipes",
            {"project_id": project_id, "name": name},
            {
                "project_id": project_id,
                "name": name,
                "pipe_type": "mainline",
                "geom": {"type": "LineString",
                         "coordinates": [list(p) for p in path_ll]},
                "length_m": length,
                "diameter_mm": diameter,
                "material": "HDPE PE100 PN10",
                "revision_id": revision,
                "created_at": now,
                "updated_at": now,
            })
        n += 1

    st.success(f"Created {n} mainline pipes (revision {revision})")