"""Step 01 — Initial KML upload + import into MongoDB."""
from __future__ import annotations

import os
from datetime import datetime, timezone

import streamlit as st

from core import kml_io
from db import repository
from db.connection import get_db

IMPORT_DIR = "imports"


def render():
    st.header("Step 01 — Initialize Project")
    st.caption("Upload the initial KML containing the property boundary (P1) "
               "and the water point. Sectors may also be present.")

    project_id = st.text_input(
        "Project ID",
        value=st.session_state.get("project_id", "dhar_v1"),
        key="init_project_id",
    )
    project_name = st.text_input("Project name", value=project_id)

    uploaded = st.file_uploader("Initial KML", type=["kml"])

    col1, col2 = st.columns(2)
    with col1:
        import_btn = st.button("Import to database", type="primary",
                               disabled=uploaded is None)
    with col2:
        preview_btn = st.button("Preview only", disabled=uploaded is None)

    if uploaded is None:
        st.info("Waiting for a KML file.")
        return

    os.makedirs(IMPORT_DIR, exist_ok=True)
    saved_path = os.path.join(IMPORT_DIR, uploaded.name)
    with open(saved_path, "wb") as f:
        f.write(uploaded.getbuffer())
    st.success(f"Saved upload → {saved_path}")

    if preview_btn:
        _preview(saved_path)
        return

    if import_btn:
        _import(project_id, project_name, saved_path)


def _preview(path: str) -> None:
    data = kml_io.read_kml(path)
    st.subheader("Preview")
    st.write(f"Total placemarks: **{len(data)}**")

    rows = []
    for name, item in data.items():
        rows.append({
            "name": name,
            "kind": item["kind"],
            "vertices": len(item["coords"]),
        })
    st.dataframe(rows, width='stretch')


def _import(project_id: str, project_name: str, path: str) -> None:
    db = get_db()
    revision = repository.new_revision(project_id, "01_initial", "Initial import")

    repository.create_project(project_id, project_name, description="")

    # wipe existing entities for this project (fresh start)
    for coll in ["property", "water_points", "basins", "sectors"]:
        repository.clear_step(project_id, coll)

    data = kml_io.read_kml(path)
    now = datetime.now(timezone.utc)
    counts = {"property": 0, "water_points": 0, "basins": 0, "sectors": 0}

    for name, item in data.items():
        kind = item["kind"]
        coords = item["coords"]

        # P1 → property
        if name == "P1" and kind == "polygon":
            geom = kml_io.to_geojson_polygon(coords)
            repository.upsert("property",
                {"project_id": project_id, "name": name},
                {
                    "project_id": project_id,
                    "name": name,
                    "geom": geom,
                    "revision_id": revision,
                    "created_at": now,
                    "updated_at": now,
                })
            counts["property"] += 1

        # Water point (Point named "Point D'eau ...")
        elif kind == "point" and ("eau" in name.lower() or "water" in name.lower()):
            lon, lat, ele = coords[0]
            repository.upsert("water_points",
                {"project_id": project_id, "name": name},
                {
                    "project_id": project_id,
                    "name": name,
                    "location": kml_io.to_geojson_point(lon, lat),
                    "elev_m": ele,
                    "revision_id": revision,
                    "created_at": now,
                    "updated_at": now,
                })
            counts["water_points"] += 1

        # Basin
        elif kind == "polygon" and "basin" in name.lower():
            geom = kml_io.to_geojson_polygon(coords)
            ele = max(c[2] for c in coords) if coords else 0.0
            repository.upsert("basins",
                {"project_id": project_id, "name": name},
                {
                    "project_id": project_id,
                    "name": name,
                    "geom": geom,
                    "elev_m": ele,
                    "revision_id": revision,
                    "created_at": now,
                    "updated_at": now,
                })
            counts["basins"] += 1

        # Sector
        elif kind == "polygon" and name.upper().startswith("S") and "-" not in name:
            geom = kml_io.to_geojson_polygon(coords)
            from shapely.geometry import shape as shp_shape
            try:
                area = shp_shape(geom).area
            except Exception:
                area = 0.0
            repository.upsert("sectors",
                {"project_id": project_id, "sector_code": name},
                {
                    "project_id": project_id,
                    "name": name,
                    "sector_code": name,
                    "geom": geom,
                    "area_m2": area,
                    "revision_id": revision,
                    "created_at": now,
                    "updated_at": now,
                })
            counts["sectors"] += 1

    st.session_state["project_id"] = project_id
    st.success(
        f"Imported to project **{project_id}**: "
        f"property={counts['property']}, "
        f"water={counts['water_points']}, "
        f"basins={counts['basins']}, "
        f"sectors={counts['sectors']}  (revision {revision})"
    )