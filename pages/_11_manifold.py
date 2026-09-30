"""Step 11 — Manifold pipe at the top of each zone."""
from __future__ import annotations

import math
from datetime import datetime, timezone

import streamlit as st

from db import queries, repository
from db.connection import get_db


def render():
    st.header("Step 11 — Manifolds")
    st.caption("One manifold per zone, connecting all row start points.")

    project_id = st.session_state.get("project_id", "dhar_v1")

    if st.button("Build manifolds", type="primary"):
        _build(project_id)


def _build(project_id: str) -> None:
    zones = queries.get_zones(project_id)
    if not zones:
        st.error("No zones. Run Step 04 first.")
        return

    revision = repository.new_revision(project_id, "11_manifold", "Build manifolds")
    repository.clear_step(project_id, "manifolds")

    now = datetime.now(timezone.utc)
    n = 0

    for z in zones:
        rows = queries.get_rows(project_id, z["name"])
        if not rows:
            continue

        # Uphill endpoints: pick the row endpoint closest to the zone's uphill edge.
        # We don't have elevations, so we use the rows' first point (built that way in 08).
        starts = []
        for r in rows:
            line = r["geom"]["coordinates"]
            starts.append((line[0][0], line[0][1]))

        if len(starts) < 2:
            continue

        # manifold joins the starts, sorted by longitude
        starts_sorted = sorted(starts, key=lambda p: p[0])
        manifold_ll = [list(starts_sorted[0]), list(starts_sorted[-1])]

        name = f"MANIFOLD {z['name']}"
        length = math.hypot(manifold_ll[1][0] - manifold_ll[0][0],
                            manifold_ll[1][1] - manifold_ll[0][1]) * 111000.0 * 0.85

        repository.upsert("manifolds",
            {"project_id": project_id, "name": name},
            {
                "project_id": project_id,
                "name": name,
                "zone_name": z["name"],
                "geom": {"type": "LineString", "coordinates": manifold_ll},
                "length_m": length,
                "revision_id": revision,
                "created_at": now,
                "updated_at": now,
            })
        n += 1

    st.success(f"Created {n} manifolds (revision {revision})")