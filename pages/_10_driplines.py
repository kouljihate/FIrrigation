"""Step 10 — Driplines along each row."""
from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from core.driplines import dripline_from_row
from db import queries, repository
from db.connection import get_db


def render():
    st.header("Step 10 — Driplines")
    st.caption("One dripline per row, along the tree line.")

    project_id = st.session_state.get("project_id", "dhar_v1")
    emitter_spacing = st.number_input("Emitter spacing (m)", 0.1, 2.0, 0.5)

    if st.button("Build driplines", type="primary"):
        _build(project_id, float(emitter_spacing))


def _build(project_id: str, emitter_spacing: float) -> None:
    rows = queries.get_rows(project_id)
    if not rows:
        st.error("No rows. Run Step 08 first.")
        return

    revision = repository.new_revision(project_id, "10_driplines", "Build driplines")
    repository.clear_step(project_id, "driplines")

    now = datetime.now(timezone.utc)
    n = 0
    for r in rows:
        line = r["geom"]["coordinates"]
        start = (line[0][0], line[0][1])
        end = (line[-1][0], line[-1][1])
        dl = dripline_from_row(start, end, emitter_spacing)
        name = f"DL {r['name']}"
        repository.upsert("driplines",
            {"project_id": project_id, "name": name},
            {
                "project_id": project_id,
                "name": name,
                "row_name": r["name"],
                "zone_name": r["zone_name"],
                "geom": {"type": "LineString",
                         "coordinates": [list(p) for p in dl["geometry"]]},
                "length_m": dl["length_m"],
                "emitter_count": dl["emitter_count"],
                "revision_id": revision,
                "created_at": now,
                "updated_at": now,
            })
        n += 1

    st.success(f"Created {n} driplines (revision {revision})")