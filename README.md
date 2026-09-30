# Farm Irrigation Workbench

Streamlit + MongoDB application for orchard / farm irrigation design.

## Install

    python -m venv venv
    venv\Scripts\activate          # Windows
    source venv/bin/activate       # macOS / Linux

    pip install -r requirements.txt

## MongoDB

Install MongoDB Community Edition locally and start it as a service.
Default connection: `mongodb://localhost:27017`.

Then copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
and adjust if needed.

## Run

    streamlit run app.py

## Layout

| Folder     | Purpose                                |
|------------|----------------------------------------|
| `app.py`   | Streamlit entry point                  |
| `pages/`   | One file per workflow step             |
| `core/`    | Domain logic (geometry, piping, rows)  |
| `db/`      | MongoDB connection + repository        |
| `configs/` | YAML per step                          |
| `imports/` | User-uploaded KML files                |
| `exports/` | Generated KML / GeoJSON / CSV          |
| `scripts/` | Headless CLI versions                  |

## Workflow

1. **Project → Initialize** — upload the initial KML
2. **Project → Water & Basin** — review water point and basin
3. **Geometry → Sectors** — verify imported sectors
4. **Geometry → Zones** — split each sector into 3 equal-area zones
5. **Geometry → Valves** — generate MV + ZV valves
6. **Hydrology → Mainline** — route basin → MV1/MV2/MV3
7. **Hydrology → Sub-mains** — route MV → each ZV
8. **Field → Rows** — trace rows inside each zone
9. **Field → Trees** — place trees along rows
10. **Field → Driplines** — one dripline per row
11. **Hydrology → Manifold** — manifold per zone
12. **Export → BOM** — bill of materials
13. **Export → Export** — final KML / GeoJSON / CSV

## Notes

- All geometry is stored as GeoJSON in MongoDB (`2dsphere` indexed).
- Every destructive step creates a new revision — see the Settings tab.
- Page filenames must start with an underscore (Python identifier rule).