#!/usr/bin/env python3
"""Templates part 3: field + export + CSS + JS."""
from pathlib import Path

BASE = Path(__file__).parent
FORCE = False
FILES = {}

FILES["templates/field/rows.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Rows</h1>
<div class="card mb-4"><div class="card-body">
<form method="post" class="row g-3 align-items-end">
  <div class="col-md-3"><label class="form-label">Row spacing (m)</label>
    <input type="number" name="spacing" value="4" step="0.1" class="form-control"></div>
  <div class="col-md-3"><label class="form-label">First row offset (m)</label>
    <input type="number" name="offset" value="2" step="0.1" class="form-control"></div>
  <div class="col-md-3"><button class="btn btn-success" type="submit">Build rows</button></div>
</form>
</div></div>
{% if rows %}
<p class="text-muted">{{ rows|length }} rows total.</p>
<table class="table table-sm table-striped">
  <thead><tr><th>Name</th><th>Zone</th><th>Length (m)</th></tr></thead>
  <tbody>{% for r in rows[:200] %}
  <tr><td>{{ r.name }}</td><td>{{ r.zone_name }}</td><td>{{ "%.1f"|format(r.length_m) }}</td></tr>
  {% endfor %}</tbody>
</table>
{% if rows|length > 200 %}<p class="text-muted">Showing first 200.</p>{% endif %}
{% else %}
<div class="alert alert-info">No rows yet.</div>
{% endif %}
{% endblock %}
'''

FILES["templates/field/trees.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Trees</h1>
<div class="card mb-4"><div class="card-body">
<form method="post" class="row g-3 align-items-end">
  <div class="col-md-3"><label class="form-label">Tree spacing (m)</label>
    <input type="number" name="spacing" value="4" step="0.1" class="form-control"></div>
  <div class="col-md-3"><label class="form-label">Fig percentage</label>
    <input type="number" name="fig_pct" value="20" min="0" max="100" class="form-control"></div>
  <div class="col-md-3"><button class="btn btn-success" type="submit">Place trees</button></div>
</form>
</div></div>
{% if trees %}
<p class="text-muted">{{ trees|length }} trees total.</p>
<table class="table table-sm table-striped">
  <thead><tr><th>Name</th><th>Zone</th><th>Row</th><th>Species</th></tr></thead>
  <tbody>{% for t in trees[:200] %}
  <tr><td>{{ t.name }}</td><td>{{ t.zone_name }}</td><td>{{ t.row_name }}</td><td>{{ t.species }}</td></tr>
  {% endfor %}</tbody>
</table>
{% if trees|length > 200 %}<p class="text-muted">Showing first 200.</p>{% endif %}
{% else %}
<div class="alert alert-info">No trees yet.</div>
{% endif %}
{% endblock %}
'''

FILES["templates/field/driplines.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Driplines</h1>
<div class="card mb-4"><div class="card-body">
<form method="post" class="row g-3 align-items-end">
  <div class="col-md-3"><label class="form-label">Emitter spacing (m)</label>
    <input type="number" name="emitter_spacing" value="0.5" step="0.1" class="form-control"></div>
  <div class="col-md-3"><button class="btn btn-success" type="submit">Build driplines</button></div>
</form>
</div></div>
{% if driplines %}
<p class="text-muted">{{ driplines|length }} driplines total.</p>
<table class="table table-sm table-striped">
  <thead><tr><th>Name</th><th>Row</th><th>Length (m)</th><th>Emitters</th></tr></thead>
  <tbody>{% for d in driplines[:200] %}
  <tr><td>{{ d.name }}</td><td>{{ d.row_name }}</td>
      <td>{{ "%.1f"|format(d.length_m) }}</td><td>{{ d.emitter_count }}</td></tr>
  {% endfor %}</tbody>
</table>
{% else %}
<div class="alert alert-info">No driplines yet.</div>
{% endif %}
{% endblock %}
'''

FILES["templates/export/bom.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Bill of Materials</h1>
<form method="post" class="mb-3">
  <button class="btn btn-success" type="submit">Recompute BOM</button>
</form>
{% if rows %}
<table class="table table-striped">
  <thead><tr><th>Category</th><th>Description</th><th>Spec</th><th>Unit</th><th>Qty</th><th>Unit price</th><th>Total</th></tr></thead>
  <tbody>{% for r in rows %}
  <tr>
    <td>{{ r.category }}</td><td>{{ r.description }}</td><td>{{ r.spec }}</td>
    <td>{{ r.unit }}</td><td>{{ "%.1f"|format(r.quantity) }}</td>
    <td>{{ "%.2f"|format(r.unit_price) }}</td>
    <td>{{ "%.2f"|format(r.quantity * r.unit_price) }}</td>
  </tr>
  {% endfor %}</tbody>
</table>
<h4>Estimated total: <strong>{{ "%.2f"|format(total) }}</strong></h4>
{% else %}
<div class="alert alert-info">Nothing to compute yet. Run the previous steps.</div>
{% endif %}
{% endblock %}
'''

FILES["static/css/app.css"] = r'''/* Farm Irrigation Workbench — custom styles */

body {
  background: #f6f8fa;
}

.navbar-brand {
  font-weight: 600;
}

.card {
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  border: 1px solid #e3e6ea;
}

.card-header {
  background: #f0f3f6;
  font-weight: 600;
  font-size: 0.95rem;
}

.table-sm td, .table-sm th {
  font-size: 0.85rem;
}

.nav-pills .nav-link {
  color: #495057;
}

.nav-pills .nav-link.active {
  background-color: #198754;
}

#map {
  z-index: 1;
}

pre {
  white-space: pre-wrap;
  word-break: break-all;
}

footer {
  border-top: 1px solid #e3e6ea;
  margin-top: 2rem;
}
'''

FILES["static/js/map.js"] = r'''// Farm Irrigation Workbench — Leaflet map

(function () {
  // ---- init map ----
  const map = L.map("map").setView([33.8455, -4.5860], 15);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 20,
    attribution: '© OpenStreetMap'
  }).addTo(map);

  // layer groups per collection
  const layers = {
    property:  L.layerGroup().addTo(map),
    sectors:   L.layerGroup().addTo(map),
    zones:     L.layerGroup().addTo(map),
    pipes:     L.layerGroup().addTo(map),
    rows:      L.layerGroup(),
    valves:    L.layerGroup().addTo(map),
    trees:     L.layerGroup(),
    driplines: L.layerGroup(),
    manifolds: L.layerGroup(),
  };

  // colors per collection
  const colors = {
    property:  "#000000",
    sectors:   "#00bcd4",
    zones:     "#3f51b5",
    pipes:     "#ff0000",
    rows:      "#00c853",
    valves:    "#e91e63",
    trees:     "#2e7d32",
    driplines: "#00897b",
    manifolds: "#ff9800",
  };

  // ---- helpers ----
  function addGeoJSONFeature(feature) {
    const coll = feature.properties.collection;
    if (!layers[coll]) return;

    const color = colors[coll] || "#888";
    const geom = feature.geometry;

    const style = {
      color: color,
      weight: coll === "property" ? 2 : 1.5,
      fillOpacity: coll === "zones" ? 0.15 : 0,
    };

    if (geom.type === "Point") {
      const latlng = [geom.coordinates[1], geom.coordinates[0]];
      const marker = L.circleMarker(latlng, {
        radius: coll === "trees" ? 2 : 5,
        color: color,
        fillColor: color,
        fillOpacity: 0.8,
      }).bindTooltip(feature.properties.name || "");
      layers[coll].addLayer(marker);
    } else if (geom.type === "LineString") {
      const latlngs = geom.coordinates.map(c => [c[1], c[0]]);
      const line = L.polyline(latlngs, style)
        .bindTooltip(feature.properties.name || "");
      layers[coll].addLayer(line);
    } else if (geom.type === "Polygon") {
      const latlngs = geom.coordinates[0].map(c => [c[1], c[0]]);
      const poly = L.polygon(latlngs, style)
        .bindTooltip(feature.properties.name || "");
      layers[coll].addLayer(poly);
    }
  }

  // ---- load data ----
  fetch(window.FARM_API.geojson)
    .then(r => r.json())
    .then(fc => {
      fc.features.forEach(addGeoJSONFeature);
    })
    .catch(err => console.error("GeoJSON load failed:", err));

  // ---- layer toggles UI ----
  const toggleBox = document.getElementById("layer-toggles");
  Object.keys(layers).forEach(name => {
    const checked = map.hasLayer(layers[name]);
    const id = `layer-${name}`;
    const wrapper = document.createElement("div");
    wrapper.className = "form-check";
    wrapper.innerHTML = `
      <input class="form-check-input" type="checkbox" id="${id}" ${checked ? "checked" : ""}>
      <label class="form-check-label" for="${id}">${name}</label>
    `;
    toggleBox.appendChild(wrapper);
    wrapper.querySelector("input").addEventListener("change", e => {
      if (e.target.checked) map.addLayer(layers[name]);
      else map.removeLayer(layers[name]);
    });
  });

  // ---- fit to property ----
  document.getElementById("fit-btn").addEventListener("click", () => {
    fetch(window.FARM_API.bounds)
      .then(r => r.json())
      .then(d => {
        if (d.bounds) {
          map.fitBounds(d.bounds, { padding: [20, 20] });
        }
      });
  });

})();
'''


def main():
    for path, content in FILES.items():
        p = BASE / path
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists() and not FORCE:
            print(f"  skip   {path}")
            continue
        p.write_text(content, encoding="utf-8")
        print(f"  write  {path}")
    print(f"\nDone. {len(FILES)} files.")


if __name__ == "__main__":
    main()