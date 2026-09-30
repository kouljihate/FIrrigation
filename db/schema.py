"""Ensure MongoDB collections and indexes exist."""
from __future__ import annotations

from pymongo import ASCENDING, GEOSPHERE, IndexModel

from .connection import get_db


COLLECTIONS = [
    "projects",
    "revisions",
    "property",
    "water_points",
    "basins",
    "sectors",
    "zones",
    "valves",
    "pipes",
    "rows",
    "trees",
    "driplines",
    "manifolds",
    "bom_items",
    "settings",
]


def ensure_indexes() -> None:
    db = get_db()

    # make sure collections exist
    existing = set(db.list_collection_names())
    for name in COLLECTIONS:
        if name not in existing:
            db.create_collection(name)

    # common indexes
    idx_project = IndexModel([("project_id", ASCENDING)])
    idx_created = IndexModel([("created_at", ASCENDING)])

    # 2dsphere indexes on geometry fields
    for coll, field in [
        ("property", "geom"),
        ("water_points", "location"),
        ("basins", "geom"),
        ("sectors", "geom"),
        ("zones", "geom"),
        ("valves", "location"),
        ("pipes", "geom"),
        ("rows", "geom"),
        ("trees", "location"),
        ("driplines", "geom"),
        ("manifolds", "geom"),
    ]:
        db[coll].create_indexes([
            IndexModel([(field, GEOSPHERE)]),
            idx_project,
            idx_created,
        ])

    # business-key indexes
    db["sectors"].create_index([("project_id", ASCENDING), ("sector_code", ASCENDING)], unique=True)
    db["zones"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
    db["valves"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
    db["pipes"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
    db["rows"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
    db["trees"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
    db["revisions"].create_index([("project_id", ASCENDING), ("step", ASCENDING), ("created_at", ASCENDING)])