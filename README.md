# Farm Irrigation Workbench

Flask + MongoDB web application for orchard/farm irrigation system design.

## Stack

- **Backend**: Flask 3.x, PyMongo 4.x
- **Geometry**: Shapely 2.x, NumPy
- **Export**: lxml (KML), ezdxf (DXF), GeoJSON, CSV
- **Frontend**: Bootstrap 5 (Bootswatch Journal), Leaflet 1.9, bilingual EN/AR
- **Database**: MongoDB (local or Atlas)

## Install

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
```

## MongoDB

Install MongoDB Community Edition locally and start it as a service.
Default connection: `mongodb://localhost:27017`.

Copy `.env.example` to `.env` and adjust if needed:
```
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=farm_irrigation
SECRET_KEY=your-secret-key
FLASK_DEBUG=1
LOG_LEVEL=INFO
```

## Run

```bash
python run.py
```

Open http://127.0.0.1:5000

## Project Structure

| Folder/File      | Purpose                                           |
|------------------|---------------------------------------------------|
| `app.py`         | Flask app factory, blueprint registration         |
| `run.py`         | Dev server entry point                            |
| `config.py`      | Configuration (YAML + env)                        |
| `routes/`        | 9 blueprints: home, project, geometry, hydrology, field, export, api, map_view, logs |
| `core/`          | Domain logic: kml_io, geometry, piping, rows, trees, driplines, valves, BOM |
| `db/`            | MongoDB connection, repository, queries, models   |
| `templates/`     | Jinja2 templates (base, home, project, geometry, hydrology, field, export, logs, map) |
| `static/`        | CSS, JS (toasts, modals, Leaflet map)             |
| `imports/`       | User-uploaded KML files                           |
| `exports/`       | Generated KML / DXF / GeoJSON / CSV               |
| `logs/`          | Application log file                              |

## Workflow

1. **Home** — Create new project or open existing
2. **Project → Initialize** — Upload KML (property P1, water points, basins, sectors)
3. **Project → Water & Basin** — Add/edit water points and basins
4. **Geometry → Sectors** — Verify/edit imported sectors
5. **Geometry → Zones** — Split each sector into equal-area zones (contour/fan/strip modes)
6. **Geometry → Valves** — Generate Main Valves (MV) + Zone Valves (ZV)
7. **Hydrology → Mainline** — Route basin → each MV (with boundary detour)
8. **Hydrology → Sub-mains** — Route each MV → its ZVs
9. **Hydrology → Manifold** — Build manifold per zone (connects row starts)
10. **Field → Rows** — Trace rows inside each zone (perpendicular to fall line)
11. **Field → Trees** — Place trees along rows (configurable spacing, species mix)
12. **Field → Driplines** — One dripline per row (emitter spacing configurable)
13. **Export → BOM** — Bill of Materials (pipes, valves, trees, driplines)
14. **Export** — Download KML, DXF, GeoJSON, CSV (trees)
15. **Map** — Full-screen Leaflet map with all layers

## Features

- **Revision history** — Every build step creates a revision (see Project → Settings)
- **Bilingual UI** — English/Arabic with RTL support
- **Map view** — Interactive Leaflet map with GeoJSON API
- **Multiple zone split algorithms** — Contour (equal-area bands), Fan (radial), Strip (parallel)
- **Pipe routing** — Direct or boundary-detour routing around property
- **Export formats** — KML (Google Earth), DXF (CAD), GeoJSON (GIS), CSV (trees)

## Configuration

Edit `config.yaml` for:
- App title/version
- MongoDB connection
- Import/export/config directories
- Default parameters (spacing, diameters, etc.)

Environment variables in `.env` override YAML for secrets.

## Requirements

See `requirements.txt`:
- flask>=3.0
- flask-login>=0.6
- pymongo>=4.6
- shapely>=2.0
- lxml>=4.9
- numpy>=1.24
- PyYAML>=6.0
- pandas>=2.0
- ezdxf>=1.3
- python-dotenv>=1.0