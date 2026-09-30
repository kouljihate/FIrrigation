"""Settings tab — connection info, danger zone."""
from __future__ import annotations

import streamlit as st

from db.connection import ping
from db import queries, repository


def render():
    st.header("Settings")

    project_id = st.session_state.get("project_id", "farm_v1")

    st.subheader("MongoDB")
    ok = ping()
    st.write("Connection:", "🟢 OK" if ok else "🔴 FAILED")

    if ok:
        summary = queries.project_summary(project_id)
        st.json(summary)

    st.divider()
    st.subheader("Revisions")
    revs = queries.get_revisions(project_id)
    if revs:
        st.dataframe(revs, width='stretch')
    else:
        st.info("No revisions yet.")

    st.divider()
    st.subheader("Danger zone")
    st.caption("These actions cannot be undone.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Wipe rows + trees", type="secondary"):
            repository.clear_step(project_id, "rows")
            repository.clear_step(project_id, "trees")
            st.success("Wiped rows and trees.")
    with col2:
        if st.button("Wipe everything for this project", type="secondary"):
            for coll in ["property", "water_points", "basins",
                         "sectors", "zones", "valves", "pipes",
                         "rows", "trees", "driplines", "manifolds",
                         "bom_items", "revisions"]:
                repository.clear_step(project_id, coll)
            st.success(f"Wiped project {project_id}.")