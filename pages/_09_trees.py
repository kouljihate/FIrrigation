"""Step 09 — Trees along each row."""
from __future__ import annotations

import math
from datetime import datetime, timezone

import streamlit as st

from core.trees import place_trees_on_row
from db import queries, repository
from db.connection import get_db


def render():
    st.header("Step 09 — Trees")
    st.caption("Place trees at 4 m spacing along each row.")

    project_id = st.session_state.get("project_id", "dhar_v1")
    spacing = st.number_input("Tree spacing (m)", 1.0, 20.0, 4.0)
    fig_pct = st.slider("Fig percentage", 0, 100, 20)

    if st.button("Place trees", type="primary"):
        _build(project_id, float(spacing), int(fig_pct))


def _build(project_id: str, spacing: float, fig_pct: int) -> None:
    rows = queries.get_rows(project_id)
    if not rows:
        st.error("No rows. Run Step 08 first.")
        return

    db = get_db()
    revision = repository.new_revision(project_id, "09_trees", "Place trees")
    repository.clear_step(project_id, "trees")

    now = datetime.now(timezone.utc)
    total = 0
    fig_counter = 0

    for r in rows:
        line = r["geom"]["coordinates"]
        start = (line[0][0], line[0][1])
        end = (line[-1][0], line[-1][1])
        pts = place_trees_on_row(start, end, spacing, center=True)

        for i, (lon, lat) in enumerate(pts):
            fig_counter += 1
            species = "fig" if (fig_counter % 100) < fig_pct else "olive"
            name = f"T {r['name']}-T{i+1:02d}"
            repository.upsert("trees",
                {"project_id": project_id, "name": name},
                {
                    "project_id": project_id,
                    "name": name,
                    "row_name": r["name"],
                    "zone_name": r["zone_name"],
                    "tree_index": i + 1,
                    "location": {"type": "Point",
                                 "coordinates": [lon, lat]},
                    "species": species,
                    "revision_id": revision,
                    "created_at": now,
                    "updated_at": now,
                })
            total += 1

    st.success(f"Placed {total} trees (revision {revision})")