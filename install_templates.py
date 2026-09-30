#!/usr/bin/env python3
"""Templates part 1: base, index, error, map, logs, _section_nav, project/*"""
from pathlib import Path

BASE = Path(__file__).parent
FORCE = False

FILES = {}

FILES["templates/base.html"] = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}{{ app_title }}{% endblock %}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/app.css') }}">
  {% block head %}{% endblock %}
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-success">
  <div class="container-fluid">
    <a class="navbar-brand" href="{{ url_for('project.index') }}">🌱 {{ app_title }}</a>
    <form class="d-flex ms-3" method="post" action="{{ url_for('project.set_project') }}">
      <input class="form-control form-control-sm me-2" name="project_id" value="{{ project_id }}" style="max-width:180px;">
      <button class="btn btn-sm btn-outline-light" type="submit">Set</button>
    </form>
    <div class="ms-auto d-flex align-items-center">
      <span class="badge bg-light text-success me-2">v{{ app_version }}</span>
      <a class="btn btn-sm btn-outline-light me-2" href="{{ url_for('map_view.map_page') }}">🗺 Map</a>
      <a class="btn btn-sm btn-outline-light me-2" href="{{ url_for('logs.index') }}">📜 Logs</a>
    </div>
  </div>
</nav>
{% include '_section_nav.html' %}
<main class="container-fluid py-4">
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for cat, msg in messages %}
        <div class="alert alert-{{ 'danger' if cat == 'error' else 'success' }} alert-dismissible fade show">
          {{ msg }}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
      {% endfor %}
    {% endif %}
  {% endwith %}
  {% block content %}{% endblock %}
</main>
<footer class="text-center text-muted py-4 small">
  {{ app_title }} · project: <code>{{ project_id }}</code> ·
  sectors={{ summary.get('sectors', 0) }} · zones={{ summary.get('zones', 0) }} ·
  valves={{ summary.get('valves', 0) }} · pipes={{ summary.get('pipes', 0) }} ·
  rows={{ summary.get('rows', 0) }} · trees={{ summary.get('trees', 0) }}
</footer>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
{% block scripts %}{% endblock %}
</body>
</html>
'''

FILES["templates/_section_nav.html"] = r'''{% set sections = [
  ('project.index',      '📁 Project',   ['project.initial','project.water','project.settings']),
  ('geometry.sectors',   '📐 Geometry',  ['geometry.sectors','geometry.zones','geometry.valves']),
  ('hydrology.mainline', '💧 Hydrology', ['hydrology.mainline','hydrology.submains','hydrology.manifold']),
  ('field.rows',         '🌳 Field',     ['field.rows','field.trees','field.driplines']),
  ('export.bom',         '📦 Export',    ['export.bom','export.kml','export.dxf','export.geojson','export.trees_csv']),
] %}
<ul class="nav nav-pills justify-content-center bg-light border-bottom py-2 mb-0">
  {% for href, label, children in sections %}
    {% set active = request.endpoint in children or request.endpoint == href %}
    <li class="nav-item"><a class="nav-link {% if active %}active{% endif %}" href="{{ url_for(href) }}">{{ label }}</a></li>
  {% endfor %}
</ul>
{% if request.endpoint in ['geometry.sectors','geometry.zones','geometry.valves'] %}
<ul class="nav nav-tabs justify-content-center pt-2">
  <li class="nav-item"><a class="nav-link {% if request.endpoint=='geometry.sectors' %}active{% endif %}" href="{{ url_for('geometry.sectors') }}">Sectors</a></li>
  <li class="nav-item"><a class="nav-link {% if request.endpoint=='geometry.zones' %}active{% endif %}" href="{{ url_for('geometry.zones') }}">Zones</a></li>
  <li class="nav-item"><a class="nav-link {% if request.endpoint=='geometry.valves' %}active{% endif %}" href="{{ url_for('geometry.valves') }}">Valves</a></li>
</ul>
{% elif request.endpoint in ['hydrology.mainline','hydrology.submains','hydrology.manifold'] %}
<ul class="nav nav-tabs justify-content-center pt-2">
  <li class="nav-item"><a class="nav-link {% if request.endpoint=='hydrology.mainline' %}active{% endif %}" href="{{ url_for('hydrology.mainline') }}">Mainline</a></li>
  <li class="nav-item"><a class="nav-link {% if request.endpoint=='hydrology.submains' %}active{% endif %}" href="{{ url_for('hydrology.submains') }}">Sub-mains</a></li>
  <li class="nav-item"><a class="nav-link {% if request.endpoint=='hydrology.manifold' %}active{% endif %}" href="{{ url_for('hydrology.manifold') }}">Manifold</a></li>
</ul>
{% elif request.endpoint in ['field.rows','field.trees','field.driplines'] %}
<ul class="nav nav-tabs justify-content-center pt-2">
  <li class="nav-item"><a class="nav-link {% if request.endpoint=='field.rows' %}active{% endif %}" href="{{ url_for('field.rows') }}">Rows</a></li>
  <li class="nav-item"><a class="nav-link {% if request.endpoint=='field.trees' %}active{% endif %}" href="{{ url_for('field.trees') }}">Trees</a></li>
  <li class="nav-item"><a class="nav-link {% if request.endpoint=='field.driplines' %}active{% endif %}" href="{{ url_for('field.driplines') }}">Driplines</a></li>
</ul>
{% elif request.endpoint in ['project.initial','project.water','project.settings'] %}
<ul class="nav nav-tabs justify-content-center pt-2">
  <li class="nav-item"><a class="nav-link {% if request.endpoint=='project.initial' %}active{% endif %}" href="{{ url_for('project.initial') }}">Initialize</a></li>
  <li class="nav-item"><a class="nav-link {% if request.endpoint=='project.water' %}active{% endif %}" href="{{ url_for('project.water') }}">Water & Basin</a></li>
  <li class="nav-item"><a class="nav-link {% if request.endpoint=='project.settings' %}active{% endif %}" href="{{ url_for('project.settings') }}">Settings</a></li>
</ul>
{% endif %}
'''

FILES["templates/index.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Project Overview</h1>
<div class="row g-3 mb-4">
  {% for label, key, icon in [
      ('Sectors','sectors','📐'),('Zones','zones','🔷'),('Valves','valves','🔴'),
      ('Pipes','pipes','〰️'),('Rows','rows','➖'),('Trees','trees','🌳'),
      ('Driplines','driplines','💧'),('Revisions','revisions','📜'),
  ] %}
  <div class="col-6 col-md-3 col-lg-2">
    <div class="card text-center h-100"><div class="card-body py-3">
      <div style="font-size:1.5rem;">{{ icon }}</div>
      <div class="display-6">{{ summary.get(key, 0) }}</div>
      <div class="text-muted small">{{ label }}</div>
    </div></div>
  </div>
  {% endfor %}
</div>
<div class="alert alert-info">
  <strong>Workflow:</strong> initialize the project (Step 01), then run each step in order — Geometry → Hydrology → Field → Export.
</div>
<div class="row g-3">
  <div class="col-md-6"><div class="card">
    <div class="card-header">Quick actions</div>
    <div class="list-group list-group-flush">
      <a href="{{ url_for('project.initial') }}" class="list-group-item list-group-item-action">📥 Upload initial KML</a>
      <a href="{{ url_for('geometry.zones') }}" class="list-group-item list-group-item-action">🔷 Build zones</a>
      <a href="{{ url_for('field.rows') }}" class="list-group-item list-group-item-action">➖ Build rows</a>
      <a href="{{ url_for('field.trees') }}" class="list-group-item list-group-item-action">🌳 Place trees</a>
      <a href="{{ url_for('map_view.map_page') }}" class="list-group-item list-group-item-action">🗺 Open map</a>
    </div>
  </div></div>
  <div class="col-md-6"><div class="card">
    <div class="card-header">Exports</div>
    <div class="list-group list-group-flush">
      <a href="{{ url_for('export.kml') }}" class="list-group-item list-group-item-action">📄 Download KML</a>
      <a href="{{ url_for('export.dxf') }}" class="list-group-item list-group-item-action">📐 Download DXF (AutoCAD)</a>
      <a href="{{ url_for('export.geojson') }}" class="list-group-item list-group-item-action">🌐 Download GeoJSON</a>
      <a href="{{ url_for('export.trees_csv') }}" class="list-group-item list-group-item-action">📊 Download Trees CSV</a>
      <a href="{{ url_for('export.bom') }}" class="list-group-item list-group-item-action">📦 Bill of Materials</a>
    </div>
  </div></div>
</div>
{% endblock %}
'''

FILES["templates/error.html"] = r'''{% extends "base.html" %}
{% block content %}
<div class="text-center py-5">
  <h1 class="display-1">{{ code }}</h1>
  <p class="lead">{{ message }}</p>
  <a href="{{ url_for('project.index') }}" class="btn btn-success">Back to home</a>
</div>
{% endblock %}
'''

FILES["templates/map.html"] = r'''{% extends "base.html" %}
{% block title %}Map · {{ app_title }}{% endblock %}
{% block head %}
<style>
  #map { height: calc(100vh - 220px); min-height: 500px; border-radius: 6px; }
  .layer-toggles { max-height: 60vh; overflow-y: auto; }
</style>
{% endblock %}
{% block content %}
<h1 class="h3 mb-3">🗺 Map — <code>{{ project_id }}</code></h1>
<div class="row g-3">
  <div class="col-md-3">
    <div class="card"><div class="card-header">Layers</div>
      <div class="card-body layer-toggles" id="layer-toggles"></div>
    </div>
    <div class="card mt-3"><div class="card-body">
      <button id="fit-btn" class="btn btn-sm btn-success w-100">Fit to property</button>
    </div></div>
  </div>
  <div class="col-md-9"><div id="map"></div></div>
</div>
{% endblock %}
{% block scripts %}
<script>
  window.FARM_API = {
    geojson: "{{ url_for('api.geojson') }}",
    bounds:  "{{ url_for('api.bounds') }}",
  };
</script>
<script src="{{ url_for('static', filename='js/map.js') }}"></script>
{% endblock %}
'''

FILES["templates/logs.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">📜 Logs & Revisions</h1>
<ul class="nav nav-tabs" role="tablist">
  <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#tab-app">Application log</button></li>
  <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-mongo">Audit log</button></li>
  <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-rev">Revisions</button></li>
</ul>
<div class="tab-content pt-3">
  <div class="tab-pane fade show active" id="tab-app">
    <pre style="max-height:60vh; overflow:auto; background:#111; color:#eee; padding:1rem; border-radius:6px; font-size:0.8rem;">{% for line in file_lines %}{{ line }}{% endfor %}</pre>
  </div>
  <div class="tab-pane fade" id="tab-mongo">
    <table class="table table-sm table-striped">
      <thead><tr><th>Time</th><th>Step</th><th>Action</th><th>Status</th><th>Duration</th><th>Items</th></tr></thead>
      <tbody>
      {% for l in mongo_logs %}
      <tr><td>{{ l.timestamp }}</td><td>{{ l.step }}</td><td>{{ l.action }}</td>
          <td><span class="badge bg-{{ 'success' if l.status=='ok' else 'danger' }}">{{ l.status }}</span></td>
          <td>{{ l.duration_ms }}</td><td>{{ l.items_created }}</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
  <div class="tab-pane fade" id="tab-rev">
    <table class="table table-sm table-striped">
      <thead><tr><th>#</th><th>Step</th><th>Note</th><th>When</th></tr></thead>
      <tbody>{% for r in revisions %}
      <tr><td>{{ r.revision_id }}</td><td>{{ r.step }}</td><td>{{ r.note }}</td><td>{{ r.created_at }}</td></tr>
      {% endfor %}</tbody>
    </table>
  </div>
</div>
{% endblock %}
'''

FILES["templates/project/initial.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Step 01 — Initialize Project</h1>
<div class="card mb-4"><div class="card-body">
<form method="post" enctype="multipart/form-data">
  <div class="mb-3">
    <label class="form-label">KML file</label>
    <input type="file" name="kml" accept=".kml" class="form-control" required>
  </div>
  <button type="submit" name="action" value="preview" class="btn btn-outline-secondary">Preview only</button>
  <button type="submit" name="action" value="import" class="btn btn-success">Import to database</button>
</form>
</div></div>
{% if preview %}
<div class="card">
  <div class="card-header">Preview — {{ preview_count }} placemarks</div>
  <div class="card-body" style="max-height:500px; overflow:auto;">
    <table class="table table-sm">
      <thead><tr><th>Name</th><th>Kind</th><th>Vertices</th></tr></thead>
      <tbody>{% for r in preview %}
      <tr><td>{{ r.name }}</td><td>{{ r.kind }}</td><td>{{ r.vertices }}</td></tr>
      {% endfor %}</tbody>
    </table>
  </div>
</div>
{% endif %}
{% endblock %}
'''

FILES["templates/project/water.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Step 02 — Water Point & Basin</h1>
<div class="row g-3">
  <div class="col-md-6"><div class="card"><div class="card-header">Water points</div>
    <div class="card-body">
      {% if water_points %}<ul class="list-group list-group-flush">
        {% for p in water_points %}<li class="list-group-item">
        <strong>{{ p.name }}</strong><br>
        <small class="text-muted">
          lon={{ "%.6f"|format(p.location.coordinates[0]) }},
          lat={{ "%.6f"|format(p.location.coordinates[1]) }},
          elev={{ "%.0f"|format(p.elev_m|default(0)) }} m
        </small></li>{% endfor %}
      </ul>{% else %}
      <div class="alert alert-warning mb-0">No water point. Run Step 01.</div>
      {% endif %}
    </div>
  </div></div>
  <div class="col-md-6"><div class="card"><div class="card-header">Basins</div>
    <div class="card-body">
      {% if basins %}<ul class="list-group list-group-flush">
        {% for b in basins %}<li class="list-group-item">
        <strong>{{ b.name }}</strong><br>
        <small class="text-muted">elev={{ "%.0f"|format(b.elev_m|default(0)) }} m</small>
        </li>{% endfor %}
      </ul>{% else %}
      <div class="alert alert-info mb-0">No basin yet. Add one below.</div>
      {% endif %}
    </div>
  </div></div>
</div>
<div class="card mt-4"><div class="card-header">Add / edit a basin</div><div class="card-body">
<form method="post">
  <div class="row g-3">
    <div class="col-md-4"><label class="form-label">Name</label>
      <input class="form-control" name="name" value="NEW BASIN — 967m" required></div>
    <div class="col-md-2"><label class="form-label">lon</label>
      <input class="form-control" name="lon" value="-4.5856651"></div>
    <div class="col-md-2"><label class="form-label">lat</label>
      <input class="form-control" name="lat" value="33.8455339"></div>
    <div class="col-md-2"><label class="form-label">elev (m)</label>
      <input class="form-control" name="elev" value="967"></div>
    <div class="col-md-2"><label class="form-label">side (m)</label>
      <input class="form-control" name="size" value="30"></div>
  </div>
  <button class="btn btn-success mt-3" type="submit">Save basin</button>
</form>
</div></div>
{% endblock %}
'''

FILES["templates/project/settings.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Settings</h1>
<div class="row g-3">
  <div class="col-md-4"><div class="card"><div class="card-header">MongoDB</div>
    <div class="card-body">
      <p>Connection:
        {% if mongo_ok %}<span class="badge bg-success">OK</span>
        {% else %}<span class="badge bg-danger">FAILED</span>{% endif %}
      </p>
      <pre class="small">{{ summary }}</pre>
    </div>
  </div></div>
  <div class="col-md-8"><div class="card"><div class="card-header">Revisions</div>
    <div class="card-body" style="max-height:300px; overflow:auto;">
      {% if revisions %}
      <table class="table table-sm">
        <thead><tr><th>#</th><th>Step</th><th>Note</th><th>When</th></tr></thead>
        <tbody>{% for r in revisions %}
        <tr><td>{{ r.revision_id }}</td><td>{{ r.step }}</td>
            <td>{{ r.note }}</td><td>{{ r.created_at }}</td></tr>
        {% endfor %}</tbody>
      </table>
      {% else %}<em>No revisions yet.</em>{% endif %}
    </div>
  </div></div>
</div>
<div class="card mt-4 border-danger">
  <div class="card-header text-danger">Danger zone</div>
  <div class="card-body">
    <p class="text-muted">These actions cannot be undone.</p>
    <form method="post" class="d-inline">
      <button name="action" value="wipe_rows_trees" class="btn btn-outline-warning">Wipe rows + trees</button>
    </form>
    <form method="post" class="d-inline" onsubmit="return confirm('Delete EVERYTHING for this project?');">
      <button name="action" value="wipe_all" class="btn btn-outline-danger">Wipe everything</button>
    </form>
  </div>
</div>
{% endblock %}
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