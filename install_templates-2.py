#!/usr/bin/env python3
"""Templates part 2: geometry + hydrology."""
from pathlib import Path

BASE = Path(__file__).parent
FORCE = False
FILES = {}

FILES["templates/geometry/sectors.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Sectors</h1>
{% if sectors %}
<table class="table table-striped">
  <thead><tr><th>Code</th><th>Vertices</th><th>Area (m²)</th></tr></thead>
  <tbody>{% for s in sectors %}
  <tr><td>{{ s.code }}</td><td>{{ s.vertices }}</td><td>{{ s.area_m2 }}</td></tr>
  {% endfor %}</tbody>
</table>
<p class="text-muted">To change sectors, re-run Step 01 with a new KML.</p>
{% else %}
<div class="alert alert-warning">No sectors found. Run Step 01 first.</div>
{% endif %}
{% endblock %}
'''

FILES["templates/geometry/zones.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Zones</h1>
<div class="card mb-4"><div class="card-body">
<form method="post" class="row g-3 align-items-end">
  <div class="col-md-3"><label class="form-label">Zones per sector</label>
    <input type="number" name="n_parts" value="3" min="2" max="10" class="form-control"></div>
  <div class="col-md-3"><label class="form-label">Inward offset (m)</label>
    <input type="number" name="offset" value="0" step="0.1" class="form-control"></div>
  <div class="col-md-3"><button class="btn btn-success" type="submit">Build zones</button></div>
</form>
</div></div>
{% if zones %}
<table class="table table-striped">
  <thead><tr><th>Name</th><th>Sector</th><th>Area (m²)</th></tr></thead>
  <tbody>{% for z in zones %}
  <tr><td>{{ z.name }}</td><td>{{ z.sector }}</td><td>{{ z.area_m2 }}</td></tr>
  {% endfor %}</tbody>
</table>
<p class="text-muted">{{ zones|length }} zones total.</p>
{% else %}
<div class="alert alert-info">No zones yet.</div>
{% endif %}
{% endblock %}
'''

FILES["templates/geometry/valves.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Valves</h1>
<form method="post" class="mb-4">
  <button class="btn btn-success" type="submit">Generate valves</button>
</form>
<div class="row g-3">
  <div class="col-md-4"><div class="card"><div class="card-header">Main valves (MV)</div>
    <ul class="list-group list-group-flush">
    {% for v in mvs %}
      <li class="list-group-item d-flex justify-content-between">
        <span>{{ v.name }}</span>
        <span class="text-muted small">Ø{{ v.diameter_mm }} mm</span>
      </li>
    {% else %}<li class="list-group-item"><em>None yet.</em></li>{% endfor %}
    </ul>
  </div></div>
  <div class="col-md-8"><div class="card">
    <div class="card-header">Zone valves (ZV) — {{ zvs|length }} total</div>
    <div class="card-body" style="max-height:400px; overflow:auto;">
      <div class="row row-cols-3 g-2">
      {% for v in zvs %}
        <div class="col"><span class="badge bg-success w-100">{{ v.name }}</span></div>
      {% else %}<div class="col-12"><em>None yet.</em></div>{% endfor %}
      </div>
    </div>
  </div></div>
</div>
{% endblock %}
'''

FILES["templates/hydrology/mainline.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Mainline</h1>
<div class="card mb-4"><div class="card-body">
<form method="post" class="row g-3 align-items-end">
  <div class="col-md-3"><label class="form-label">Inward offset from P1 (m)</label>
    <input type="number" name="offset" value="5" step="0.1" class="form-control"></div>
  <div class="col-md-3"><label class="form-label">Diameter (mm)</label>
    <input type="number" name="diameter" value="75" class="form-control"></div>
  <div class="col-md-3"><button class="btn btn-success" type="submit">Build mainline</button></div>
</form>
</div></div>
{% if pipes %}
<table class="table table-striped">
  <thead><tr><th>Name</th><th>Length (m)</th><th>Diameter (mm)</th></tr></thead>
  <tbody>{% for p in pipes %}
  <tr><td>{{ p.name }}</td><td>{{ "%.1f"|format(p.length_m) }}</td><td>{{ p.diameter_mm }}</td></tr>
  {% endfor %}</tbody>
</table>
{% else %}
<div class="alert alert-info">No mainline pipes yet.</div>
{% endif %}
{% endblock %}
'''

FILES["templates/hydrology/submains.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Sub-mains</h1>
<div class="card mb-4"><div class="card-body">
<form method="post" class="row g-3 align-items-end">
  <div class="col-md-3"><label class="form-label">Inward offset from P1 (m)</label>
    <input type="number" name="offset" value="5" step="0.1" class="form-control"></div>
  <div class="col-md-3"><label class="form-label">Diameter (mm)</label>
    <input type="number" name="diameter" value="32" class="form-control"></div>
  <div class="col-md-3"><button class="btn btn-success" type="submit">Build sub-mains</button></div>
</form>
</div></div>
{% if pipes %}
<table class="table table-sm table-striped">
  <thead><tr><th>Name</th><th>Length (m)</th></tr></thead>
  <tbody>{% for p in pipes %}
  <tr><td>{{ p.name }}</td><td>{{ "%.1f"|format(p.length_m) }}</td></tr>
  {% endfor %}</tbody>
</table>
<p class="text-muted">{{ pipes|length }} sub-main pipes.</p>
{% else %}
<div class="alert alert-info">No sub-mains yet.</div>
{% endif %}
{% endblock %}
'''

FILES["templates/hydrology/manifold.html"] = r'''{% extends "base.html" %}
{% block content %}
<h1 class="h3 mb-4">Manifolds</h1>
<form method="post" class="mb-4">
  <button class="btn btn-success" type="submit">Build manifolds</button>
</form>
{% if manifolds %}
<table class="table table-striped">
  <thead><tr><th>Name</th><th>Zone</th><th>Length (m)</th></tr></thead>
  <tbody>{% for m in manifolds %}
  <tr><td>{{ m.name }}</td><td>{{ m.zone_name }}</td><td>{{ "%.1f"|format(m.length_m) }}</td></tr>
  {% endfor %}</tbody>
</table>
{% else %}
<div class="alert alert-info">No manifolds yet.</div>
{% endif %}
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