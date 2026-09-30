"""Step 03 — Sector outlines."""
from __future__ import annotations

import streamlit as st

from db import queries


def render():
    st.header("Step 03 — Sectors")
    st.caption("Review the imported sectors. To change them, re-run Step 01 with a new KML.")

    project_id = st.session_state.get("project_id", "dhar_v1")
    sectors = queries.get_sectors(project_id)

    if not sectors:
        st.warning("No sectors found. Run Step 01 first.")
        return

    rows = []
    for s in sectors:
        ring = s["geom"]["coordinates"][0]
        rows.append({
            "code": s.get("sector_code") or s["name"],
            "vertices": len(ring),
            "area_m2": round(s.get("area_m2", 0), 1),
        })
    st.dataframe(rows, width='stretch')

    st.info(f"Total sectors: {len(sectors)}")