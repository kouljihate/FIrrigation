#!/usr/bin/env python3
"""
Create the Dhar Irrigation Workbench folder + file skeleton.

Usage:
    python scaffold.py [target_dir]

If target_dir is omitted, the current directory is used.
Existing files are never overwritten unless --force is passed.
"""

import argparse
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------- tree
TREE: dict[str, object] = {
    "app.py": None,
    "config.yaml": None,
    "requirements.txt": None,
    "README.md": None,

    "pages": {
        "__init__.py": None,
        "01_initial_kml.py": None,
        "02_water_basin.py": None,
        "03_sectors.py": None,
        "04_zones.py": None,
        "05_valves.py": None,
        "06_mainline.py": None,
        "07_submains.py": None,
        "08_rows.py": None,
        "09_trees.py": None,
        "10_driplines.py": None,
        "11_manifold.py": None,
        "12_bom.py": None,
        "13_export.py": None,
        "14_settings.py": None,
    },

    "core": {
        "__init__.py": None,
        "kml_io.py": None,
        "geometry.py": None,
        "elevation.py": None,
        "projection.py": None,
        "valve_rules.py": None,
        "piping.py": None,
        "rows.py": None,
        "trees.py": None,
        "driplines.py": None,
        "manifold.py": None,
        "styles.py": None,
        "bom.py": None,
    },

    "db": {
        "__init__.py": None,
        "connection.py": None,
        "schema.py": None,
        "models.py": None,
        "repository.py": None,
        "queries.py": None,
    },

    "configs": {
        "01_initial.yaml": None,
        "02_water_basin.yaml": None,
        "03_sectors.yaml": None,
        "04_zones.yaml": None,
        "05_valves.yaml": None,
        "06_mainline.yaml": None,
        "07_submains.yaml": None,
        "08_rows.yaml": None,
        "09_trees.yaml": None,
        "10_driplines.yaml": None,
        "11_manifold.yaml": None,
        "12_bom.yaml": None,
        "13_export.yaml": None,
    },

    "data": {
        "mongodb": {},
        "backups": {},
    },

    "imports": {
        ".gitkeep": None,
    },

    "exports": {
        ".gitkeep": None,
    },

    "scripts": {
        "route_mainline.py": None,
        "route_submains.py": None,
        "rows_trees.py": None,
    },

    "assets": {
        "logo.png": None,
        "help": {
            "01_initial.md": None,
            "02_water_basin.md": None,
            "03_sectors.md": None,
            "04_zones.md": None,
            "05_valves.md": None,
            "06_mainline.md": None,
            "07_submains.md": None,
            "08_rows.md": None,
            "09_trees.md": None,
            "10_driplines.md": None,
            "11_manifold.md": None,
            "12_bom.md": None,
            "13_export.md": None,
        },
    },

    ".streamlit": {
        "secrets.toml.example": None,
    },

    ".gitignore": None,
}


# ---------------------------------------------------------------- helpers
def create_tree(base: Path, tree: dict, force: bool) -> tuple[int, int, int]:
    """Recursively create folders and empty files. Returns (dirs, files, skipped)."""
    dirs = files = skipped = 0

    for name, value in tree.items():
        target = base / name

        if value is None:
            # a file
            if target.exists() and not force:
                skipped += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.touch(exist_ok=True)
            files += 1
        else:
            # a folder
            target.mkdir(parents=True, exist_ok=True)
            dirs += 1
            d, f, s = create_tree(target, value, force)
            dirs += d
            files += f
            skipped += s

    return dirs, files, skipped


def write_if_empty(path: Path, content: str) -> None:
    """Write content only if the file is empty or missing."""
    if not path.exists() or path.stat().st_size == 0:
        path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", default=".", help="Target directory")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite existing empty files")
    args = ap.parse_args()

    base = Path(args.target).resolve()
    base.mkdir(parents=True, exist_ok=True)

    print(f"Creating skeleton at: {base}")
    print("-" * 60)

    dirs, files, skipped = create_tree(base, TREE, args.force)

    print(f"Directories created/verified: {dirs}")
    print(f"Files created:                {files}")
    print(f"Files skipped (already exist):{skipped}")
    print("-" * 60)

    # small starter content so files are meaningful, not just empty
    write_if_empty(base / "README.md",
                   "# Dhar Irrigation Workbench\n\n"
                   "Streamlit + MongoDB application for irrigation design.\n\n"
                   "## Run\n\n"
                   "    pip install -r requirements.txt\n"
                   "    streamlit run app.py\n")

    write_if_empty(base / ".gitignore",
                   "venv/\n"
                   "__pycache__/\n"
                   "*.pyc\n"
                   ".streamlit/secrets.toml\n"
                   "data/mongodb/\n"
                   "imports/*.kml\n"
                   "exports/*\n"
                   "!imports/.gitkeep\n"
                   "!exports/.gitkeep\n")

    write_if_empty(base / "requirements.txt",
                   "streamlit>=1.30\n"
                   "pymongo>=4.6\n"
                   "shapely>=2.0\n"
                   "lxml>=4.9\n"
                   "numpy>=1.24\n"
                   "PyYAML>=6.0\n"
                   "pandas>=2.0\n")

    write_if_empty(base / ".streamlit" / "secrets.toml.example",
                   "# Copy this file to secrets.toml and fill in your values.\n"
                   "# secrets.toml is in .gitignore.\n\n"
                   "[mongo]\n"
                   "host = \"localhost\"\n"
                   "port = 27017\n"
                   "database = \"dhar_irrigation\"\n")

    print("Starter files populated where empty.")
    print("Done.")


if __name__ == "__main__":
    main()