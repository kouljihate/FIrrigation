"""MongoDB connection helpers for the Farm Irrigation Workbench (Flask)."""
from __future__ import annotations

from typing import Any

from flask import Flask, current_app
from pymongo import MongoClient, ASCENDING
from pymongo.database import Database


_client: MongoClient | None = None


_COLLECTIONS_WITH_PROJECT_ID = (
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
    "logs",
)


def _ensure_indexes(db: Database) -> None:
    """Create indexes for all project-scoped collections."""
    for coll_name in _COLLECTIONS_WITH_PROJECT_ID:
        try:
            db[coll_name].create_index([("project_id", ASCENDING)])
        except Exception:
            pass

    # Compound indexes for common query patterns
    try:
        db["sectors"].create_index([("project_id", ASCENDING), ("sector_code", ASCENDING)], unique=True)
        db["zones"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
        db["valves"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
        db["pipes"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
        db["rows"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
        db["trees"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
        db["driplines"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
        db["manifolds"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
        db["revisions"].create_index([("project_id", ASCENDING), ("revision_id", ASCENDING)], unique=True)
        db["property"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
        db["water_points"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
        db["basins"].create_index([("project_id", ASCENDING), ("name", ASCENDING)], unique=True)
    except Exception:
        pass


def init_app(app: Flask) -> None:
    """Initialise the MongoClient from Flask config. Called once at app startup."""
    global _client
    kwargs: dict[str, Any] = {
        "host": app.config["MONGO_HOST"],
        "port": int(app.config["MONGO_PORT"]),
        "serverSelectionTimeoutMS": 5000,
    }
    if app.config.get("MONGO_USER"):
        kwargs["username"] = app.config["MONGO_USER"]
        kwargs["password"] = app.config["MONGO_PASSWORD"]
        kwargs["authSource"] = app.config["MONGO_AUTH_SRC"]
    _client = MongoClient(**kwargs)

    # Ensure indexes exist
    with app.app_context():
        _ensure_indexes(get_db())


def get_client() -> MongoClient:
    if _client is None:
        raise RuntimeError("MongoDB client not initialised. Call init_app().")
    return _client


def get_db() -> Database:
    """Return the configured database handle."""
    return get_client()[current_app.config["MONGO_DB"]]


def ping() -> bool:
    try:
        get_client().admin.command("ping")
        return True
    except Exception:
        return False