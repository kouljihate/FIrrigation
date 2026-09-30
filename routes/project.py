"""Project section: Initialize, Water & Basin, Settings."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from flask import (
    Blueprint, flash, redirect, render_template, request,
    session, url_for, current_app,
)

from core import kml_io
from db import repository, queries
from db.connection import get_db


bp = Blueprint("project", __name__)


# ---------------------------------------------------------------- overview
@bp.route("/overview")
def index():
    pid = session.get("project_id", "farm_v1")
    summary = queries.project_summary(pid)
    return render_template("index.html", summary=summary)


# ---------------------------------------------------------------- initialize
@bp.route("/project/initial", methods=["GET", "POST"])
def initial():
    pid = session.get("project_id", "farm_v1")

    if request.method == "POST":
        f = request.files.get("kml")
        if not f or not f.filename:
            flash("No file uploaded.", "error")
            return redirect(url_for("project.initial"))

        os.makedirs(current_app.config["IMPORT_DIR"], exist_ok=True)
        save_path = os.path.join(current_app.config["IMPORT_DIR"], f.filename)
        f.save(save_path)
        current_app.logger.info("Saved upload: %s", save_path)

        if request.form.get("action") == "preview":
            data = kml_io.read_kml(save_path)
            rows = [{"name": n, "kind": v["kind"], "vertices": len(v["coords"])}
                    for n, v in data.items()]
            return render_template("project/initial.html", preview=rows,
                                   preview_count=len(rows))

        _import_project(pid, save_path, f.filename)
        flash(f"Imported {f.filename} to project {pid}.", "success")
        return redirect(url_for("project.initial"))

    return render_template("project/initial.html")


def _import_project(project_id: str, kml_path: str, source_name: str) -> None:
    db = get_db()
    revision = repository.new_revision(project_id, "01_initial",
                                       f"Import {source_name}")
    repository.create_project(project_id, project_id, description="")

    for coll in ("property", "water_points", "basins", "sectors"):
        repository.clear_step(project_id, coll)

    data = kml_io.read_kml(kml_path)
    now = datetime.now(timezone.utc)
    counts = {"property": 0, "water_points": 0, "basins": 0, "sectors": 0}

    for name, item in data.items():
        kind = item["kind"]
        coords = item["coords"]

        if name == "P1" and kind == "polygon":
            geom = kml_io.to_geojson_polygon(coords)
            repository.upsert("property",
                {"project_id": project_id, "name": name},
                {"project_id": project_id, "name": name, "geom": geom,
                 "revision_id": revision, "created_at": now, "updated_at": now})
            counts["property"] += 1

        elif kind == "point" and ("eau" in name.lower() or "water" in name.lower()):
            lon, lat, ele = coords[0]
            repository.upsert("water_points",
                {"project_id": project_id, "name": name},
                {"project_id": project_id, "name": name,
                 "location": kml_io.to_geojson_point(lon, lat),
                 "elev_m": ele, "revision_id": revision,
                 "created_at": now, "updated_at": now})
            counts["water_points"] += 1

        elif kind == "polygon" and "basin" in name.lower():
            geom = kml_io.to_geojson_polygon(coords)
            ele = max(c[2] for c in coords) if coords else 0.0
            repository.upsert("basins",
                {"project_id": project_id, "name": name},
                {"project_id": project_id, "name": name, "geom": geom,
                 "elev_m": ele, "revision_id": revision,
                 "created_at": now, "updated_at": now})
            counts["basins"] += 1

        elif (kind == "polygon"
              and name.upper().startswith("S")
              and "-" not in name):
            geom = kml_io.to_geojson_polygon(coords)
            from shapely.geometry import shape
            try:
                area = shape(geom).area
            except Exception:
                area = 0.0
            repository.upsert("sectors",
                {"project_id": project_id, "sector_code": name},
                {"project_id": project_id, "name": name,
                 "sector_code": name, "geom": geom, "area_m2": area,
                 "revision_id": revision,
                 "created_at": now, "updated_at": now})
            counts["sectors"] += 1

    current_app.logger.info(
        "Imported to %s: %s", project_id, counts
    )



# ---------------------------------------------------------------- water & basin
@bp.route("/project/water", methods=["GET", "POST"])
def water():
    pid = session.get("project_id", "farm_v1")
    db = get_db()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        try:
            lon = float(request.form.get("lon", 0))
            lat = float(request.form.get("lat", 0))
            elev = float(request.form.get("elev", 0))
            size = float(request.form.get("size", 30))
        except ValueError:
            flash("Invalid numeric input.", "error")
            return redirect(url_for("project.water"))

        if not name:
            flash("Basin name is required.", "error")
            return redirect(url_for("project.water"))

        dlon = size / 111000.0
        dlat = size / 111000.0
        ring = [
            [lon - dlon, lat - dlat],
            [lon + dlon, lat - dlat],
            [lon + dlon, lat + dlat],
            [lon - dlon, lat + dlat],
            [lon - dlon, lat - dlat],
        ]
        revision = repository.new_revision(pid, "02_water_basin", f"Basin {name}")
        repository.upsert("basins",
            {"project_id": pid, "name": name},
            {"project_id": pid, "name": name,
             "geom": {"type": "Polygon", "coordinates": [ring]},
             "elev_m": elev, "revision_id": revision})
        flash(f"Basin {name} saved (revision {revision}).", "success")
        return redirect(url_for("project.water"))

    wp = list(db.water_points.find({"project_id": pid}, {"_id": 0}))
    basins = list(db.basins.find({"project_id": pid}, {"_id": 0}))
    return render_template("project/water.html", water_points=wp, basins=basins)


# ---------------------------------------------------------------- settings
@bp.route("/project/settings", methods=["GET", "POST"])
def settings():
    pid = session.get("project_id", "farm_v1")

    if request.method == "POST":
        action = request.form.get("action")
        if action == "wipe_rows_trees":
            repository.clear_step(pid, "rows")
            repository.clear_step(pid, "trees")
            flash("Wiped rows and trees.", "success")
        elif action == "wipe_all":
            for coll in ("property", "water_points", "basins", "sectors",
                         "zones", "valves", "pipes", "rows", "trees",
                         "driplines", "manifolds", "bom_items", "revisions"):
                repository.clear_step(pid, coll)
            flash(f"Wiped project {pid}.", "success")
        return redirect(url_for("project.settings"))

    from db.connection import ping
    summary = queries.project_summary(pid)
    revisions = queries.get_revisions(pid)
    return render_template("project/settings.html",
                           mongo_ok=ping(),
                           summary=summary,
                           revisions=revisions)
                           
@bp.route("/set_project", methods=["POST"])
def set_project():
    pid = request.form.get("project_id", "").strip()
    if pid:
        session["project_id"] = pid
    return redirect(request.referrer or url_for("project.overview"))