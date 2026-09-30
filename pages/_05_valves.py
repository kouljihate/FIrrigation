"""Step 05 — Valves: 3 main valves + 24 zone valves."""
from __future__ import annotations

import math
from datetime import datetime, timezone

import streamlit as st

from core.valve_rules import MV_GROUPS, MV_OF_SECTOR, mv_name, zv_name
from db import queries, repository
from db.connection import get_db


def render():
    st.header("Step 05 — Valves")
    st.caption("Create the 3 main valves (MV1, MV2, MV3) and 24 zone valves "
               "(one per zone).")

    project_id = st.session_state.get("project_id", "dhar_v1")

    if st.button("Generate valves", type="primary"):
        _build(project_id)


def _build(project_id: str) -> None:
    sectors = queries.get_sectors(project_id)
    zones = queries.get_zones(project_id)
    if not sectors or not zones:
        st.error("Need sectors and zones. Run Steps 01 and 04 first.")
        return

    db = get_db()
    revision = repository.new_revision(project_id, "05_valves", "Generate valves")

    repository.clear_step(project_id, "valves")

    now = datetime.now(timezone.utc)
    n_mv = n_zv = 0

    # --- main valves (one per MV group, placed at first sector of group) ---
    for mv, sector_codes in MV_GROUPS.items():
        first = sector_codes[0]
        sdoc = next((s for s in sectors
                     if (s.get("sector_code") or s["name"]) == first), None)
        if not sdoc:
            continue
        ring = sdoc["geom"]["coordinates"][0]
        # pick the highest vertex (max 3rd coordinate in original KML — not stored,
        # so use centroid as fallback)
        lons = [p[0] for p in ring]
        lats = [p[1] for p in ring]
        lon = sum(lons) / len(lons)
        lat = sum(lats) / len(lats)
        name = mv
        repository.upsert("valves",
            {"project_id": project_id, "name": name},
            {
                "project_id": project_id,
                "name": name,
                "valve_type": "MV",
                "sector_code": first,
                "location": {"type": "Point", "coordinates": [lon, lat]},
                "diameter_mm": 50,
                "revision_id": revision,
                "created_at": now,
                "updated_at": now,
            })
        n_mv += 1

    # --- zone valves (one per zone) ---
    for z in zones:
        code = z["sector_code"]
        zi = z["zone_index"]
        ring = z["geom"]["coordinates"][0]
        lons = [p[0] for p in ring]
        lats = [p[1] for p in ring]
        lon = sum(lons) / len(lons)
        lat = sum(lats) / len(lats)
        name = zv_name(code, zi)
        repository.upsert("valves",
            {"project_id": project_id, "name": name},
            {
                "project_id": project_id,
                "name": name,
                "valve_type": "ZV",
                "sector_code": code,
                "zone_name": z["name"],
                "location": {"type": "Point", "coordinates": [lon, lat]},
                "diameter_mm": 32,
                "revision_id": revision,
                "created_at": now,
                "updated_at": now,
            })
        n_zv += 1

    st.success(f"Created {n_mv} main valves and {n_zv} zone valves "
               f"(revision {revision})")