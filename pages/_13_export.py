"""Step 13 — Export the whole project as KML / GeoJSON / CSV."""
from __future__ import annotations

import json
import os
from datetime import datetime

import streamlit as st
from lxml import etree

from db import queries
from db.connection import get_db

KML_NS = "http://www.opengis.net/kml/2.2"


def render():
    st.header("Step 13 — Export")
    st.caption("Generate KML / GeoJSON / CSV from the current database state.")

    project_id = st.session_state.get("project_id", "dhar_v1")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Generate KML"):
            path = _write_kml(project_id)
            st.session_state["last_kml"] = path
            st.success(f"Wrote {path}")
    with col2:
        if st.button("Generate GeoJSON"):
            path = _write_geojson(project_id)
            st.success(f"Wrote {path}")
    with col3:
        if st.button("Generate CSV (trees)"):
            path = _write_trees_csv(project_id)
            st.success(f"Wrote {path}")

    if "last_kml" in st.session_state:
        with open(st.session_state["last_kml"], "rb") as f:
            st.download_button("Download KML",
                               f.read(),
                               file_name=os.path.basename(st.session_state["last_kml"]),
                               mime="application/vnd.google-earth.kml+xml")


def _write_kml(project_id: str) -> str:
    db = get_db()
    os.makedirs("exports", exist_ok=True)
    path = f"exports/{project_id}_{datetime.now():%Y%m%d_%H%M%S}.kml"

    kml = etree.Element("kml", nsmap={None: KML_NS})
    doc = etree.SubElement(kml, "Document")
    etree.SubElement(doc, "name").text = project_id

    def add_polygon(name, ring):
        pm = etree.SubElement(doc, "Placemark")
        etree.SubElement(pm, "name").text = name
        poly = etree.SubElement(pm, "Polygon")
        obi = etree.SubElement(poly, "outerBoundaryIs")
        lr = etree.SubElement(obi, "LinearRing")
        cs = " ".join(f"{x},{y},0" for x, y in ring)
        etree.SubElement(lr, "coordinates").text = cs

    def add_line(name, coords):
        pm = etree.SubElement(doc, "Placemark")
        etree.SubElement(pm, "name").text = name
        ls = etree.SubElement(pm, "LineString")
        etree.SubElement(ls, "tessellate").text = "1"
        etree.SubElement(ls, "altitudeMode").text = "clampToGround"
        cs = " ".join(f"{x},{y},0" for x, y in coords)
        etree.SubElement(ls, "coordinates").text = cs

    def add_point(name, lon, lat):
        pm = etree.SubElement(doc, "Placemark")
        etree.SubElement(pm, "name").text = name
        p = etree.SubElement(pm, "Point")
        etree.SubElement(p, "coordinates").text = f"{lon},{lat},0"

    prop = db.property.find_one({"project_id": project_id})
    if prop:
        add_polygon("P1", prop["geom"]["coordinates"][0])

    for s in queries.get_sectors(project_id):
        add_polygon(s["name"], s["geom"]["coordinates"][0])

    for z in queries.get_zones(project_id):
        add_polygon(z["name"], z["geom"]["coordinates"][0])

    for v in queries.get_valves(project_id):
        lon, lat = v["location"]["coordinates"]
        add_point(v["name"], lon, lat)

    for p in queries.get_pipes(project_id):
        add_line(p["name"], p["geom"]["coordinates"])

    for r in queries.get_rows(project_id):
        add_line(r["name"], r["geom"]["coordinates"])

    for t in queries.get_trees(project_id):
        lon, lat = t["location"]["coordinates"]
        add_point(t["name"], lon, lat)

    etree.ElementTree(kml).write(path, xml_declaration=True, encoding="UTF-8", pretty_print=True)
    return path


def _write_geojson(project_id: str) -> str:
    db = get_db()
    os.makedirs("exports", exist_ok=True)
    path = f"exports/{project_id}_{datetime.now():%Y%m%d_%H%M%S}.geojson"

    features = []
    for coll, gfield in [("property", "geom"), ("sectors", "geom"),
                         ("zones", "geom"), ("pipes", "geom"),
                         ("rows", "geom"), ("valves", "location"),
                         ("trees", "location"), ("driplines", "geom"),
                         ("manifolds", "geom")]:
        for doc in db[coll].find({"project_id": project_id}):
            geom = doc.get(gfield)
            if not geom:
                continue
            features.append({
                "type": "Feature",
                "properties": {"name": doc.get("name"),
                               "collection": coll,
                               "id": str(doc.get("_id"))},
                "geometry": geom,
            })

    fc = {"type": "FeatureCollection", "features": features}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(fc, f, indent=2)
    return path


def _write_trees_csv(project_id: str) -> str:
    import csv
    os.makedirs("exports", exist_ok=True)
    path = f"exports/{project_id}_trees_{datetime.now():%Y%m%d_%H%M%S}.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "zone", "row", "species", "lon", "lat"])
        for t in queries.get_trees(project_id):
            lon, lat = t["location"]["coordinates"]
            w.writerow([t["name"], t["zone_name"], t["row_name"],
                        t.get("species", ""), lon, lat])
    return path