"""Step 07 — Sub-mains: MV → each zone valve."""
from __future__ import annotations

import math
from datetime import datetime, timezone

import streamlit as st
from shapely.geometry import Polygon

from core.geometry import clean_polygon, inward_offset
from core.piping import direct_or_detour
from core.valve_rules import MV_OF_SECTOR
from db import queries, repository
from db.connection import get_db


def render():
    st.header("Step 07 — Sub-mains")
    st.caption("Route one pipe from each MV to each of its zone valves.")

    project_id = st.session_state.get("project_id", "dhar_v1")
    offset = st.number_input("Inward offset from P1 (m)", 1.0, 30.0, 5.0)
    diameter = st.number_input("Diameter (mm)", 16, 100, 32)

    if st.button("Build sub-mains", type="primary"):
        _build(project_id, float(offset), int(diameter))


def _build(project_id: str, offset: float, diameter: int) -> None:
    db = get_db()
    prop = db.property.find_one({"project_id": project_id})
    mvs = {v["name"]: v for v in queries.get_valves(project_id, "MV")}
    zvs = queries.get_valves(project_id, "ZV")

    if not prop or not mvs or not zvs:
        st.error("Need P1, MV valves, and ZV valves.")
        return

    p1_ring = prop["geom"]["coordinates"][0]
    lon0 = sum(p[0] for p in p1_ring) / len(p1_ring)
    lat0 = sum(p[1] for p in p1_ring) / len(p1_ring)
    R = 6371000.0

    def to_local(lon, lat):
        x = math.radians(lon - lon0) * R * math.cos(math.radians(lat0))
        y = math.radians(lat - lat0) * R
        return x, y

    def to_lonlat(x, y):
        return (lon0 + math.degrees(x / (R * math.cos(math.radians(lat0)))),
                lat0 + math.degrees(y / R))

    p1_xy = clean_polygon(Polygon([to_local(p[0], p[1]) for p in p1_ring]))
    inner = inward_offset(p1_xy, offset)

    revision = repository.new_revision(project_id, "07_submains",
                                       f"Sub-mains Ø{diameter}")
    repository.delete_where("pipes", {"project_id": project_id, "pipe_type": "submain"})

    now = datetime.now(timezone.utc)
    n = 0
    for zv in zvs:
        code = zv["sector_code"]
        mv_name = MV_OF_SECTOR.get(code)
        if mv_name not in mvs:
            continue
        mv = mvs[mv_name]
        mv_lon, mv_lat = mv["location"]["coordinates"]
        zv_lon, zv_lat = zv["location"]["coordinates"]
        start = to_local(mv_lon, mv_lat)
        end = to_local(zv_lon, zv_lat)
        path = direct_or_detour(p1_xy, inner, start, end)
        path_ll = [list(to_lonlat(x, y)) for x, y in path]

        length = sum(
            math.hypot(path_ll[i+1][0] - path_ll[i][0],
                       path_ll[i+1][1] - path_ll[i][1]) * 111000.0 * 0.85
            for i in range(len(path_ll) - 1)
        )

        name = f"{mv_name}-{zv['name']}"
        repository.upsert("pipes",
            {"project_id": project_id, "name": name},
            {
                "project_id": project_id,
                "name": name,
                "pipe_type": "submain",
                "parent_pipe": mv_name,
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

    st.success(f"Created {n} sub-main pipes (revision {revision})")