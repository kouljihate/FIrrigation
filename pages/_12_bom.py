"""Step 12 — Bill of materials."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core.bom import compute_bom
from db import queries


def render():
    st.header("Step 12 — Bill of Materials")
    st.caption("Aggregated from the database. Edit unit prices below.")

    project_id = st.session_state.get("project_id", "dhar_v1")

    if st.button("Recompute BOM", type="primary"):
        st.session_state["bom_rows"] = compute_bom(project_id)

    rows = st.session_state.get("bom_rows") or compute_bom(project_id)
    if not rows:
        st.info("Nothing to compute yet. Run the previous steps.")
        return

    df = pd.DataFrame(rows)
    edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    total = (edited["quantity"] * edited["unit_price"]).sum()
    st.metric("Estimated total", f"{total:,.0f}")

    st.download_button(
        "Download BOM CSV",
        edited.to_csv(index=False).encode("utf-8"),
        file_name=f"bom_{project_id}.csv",
        mime="text/csv",
    )