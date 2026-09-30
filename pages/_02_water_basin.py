"""Step 02 — Water point and basin review / edit."""
from __future__ import annotations

import streamlit as st

from db import queries, repository
from db.connection import get_db


def render():
    st.header("Step 02 — Water Point & Basin")
    st.caption("Review and adjust the water source location and the basin footprint.")

    project_id = st.session_state.get("project_id", "dhar_v1")
    db = get_db()

    wp = list(db.water_points.find({"project_id": project_id}, {"_id": 0}))
    basins = list(db.basins.find({"project_id": project_id}, {"_id": 0}))

    st.subheader("Water points")
    if wp:
        for p in wp:
            lon, lat = p["location"]["coordinates"]
            st.write(f"- **{p['name']}** — lon={lon:.6f}, lat={lat:.6f}, elev={p.get('elev_m', 0):.0f} m")
    else:
        st.warning("No water point found. Run Step 01 first.")

    st.subheader("Basins")
    if basins:
        for b in basins:
            st.write(f"- **{b['name']}** — elev={b.get('elev_m', 0):.0f} m, "
                     f"vertices={len(b['geom']['coordinates'][0])}")
    else:
        st.info("No basin yet. You can add one below.")

    st.divider()
    st.subheader("Add / edit a basin")
    with st.form("basin_form"):
        name = st.text_input("Basin name", value="NEW BASIN — 967m")
        col1, col2, col3, col4 = st.columns(4)
        with col1: lon = st.number_input("lon", value=-4.5856651, format="%.7f")
        with col2: lat = st.number_input("lat", value=33.8455339, format="%.7f")
        with col3: elev = st.number_input("elev (m)", value=967.0)
        with col4: size = st.number_input("side (m)", value=30.0)

        submitted = st.form_submit_button("Save basin")
        if submitted:
            dlon = size / 111000.0 / (1 / 1)  # approx
            dlat = size / 111000.0
            ring = [
                [lon - dlon, lat - dlat],
                [lon + dlon, lat - dlat],
                [lon + dlon, lat + dlat],
                [lon - dlon, lat + dlat],
                [lon - dlon, lat - dlat],
            ]
            revision = repository.new_revision(project_id, "02_water_basin", f"Basin {name}")
            repository.upsert("basins",
                {"project_id": project_id, "name": name},
                {
                    "project_id": project_id,
                    "name": name,
                    "geom": {"type": "Polygon", "coordinates": [ring]},
                    "elev_m": elev,
                    "revision_id": revision,
                })
            st.success(f"Basin {name} saved (revision {revision})")