"""Flask configuration for the Farm Irrigation Workbench."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _load_yaml() -> dict:
    path = BASE_DIR / "config.yaml"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


_yaml = _load_yaml()


class Config:
    # Flask core
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"

    # Paths
    BASE_DIR = BASE_DIR
    IMPORT_DIR = BASE_DIR / _yaml.get("paths", {}).get("imports", "imports")
    EXPORT_DIR = BASE_DIR / _yaml.get("paths", {}).get("exports", "exports")
    CONFIG_DIR = BASE_DIR / _yaml.get("paths", {}).get("configs", "configs")
    HELP_DIR   = BASE_DIR / "assets" / "help"
    LOG_DIR    = BASE_DIR / "logs"

    # Uploads
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

    # MongoDB
    MONGO_HOST     = _yaml.get("mongodb", {}).get("host", "localhost")
    MONGO_PORT     = int(_yaml.get("mongodb", {}).get("port", 27017))
    MONGO_DB       = _yaml.get("mongodb", {}).get("database", "farm_irrigation")
    MONGO_USER     = _yaml.get("mongodb", {}).get("username")
    MONGO_PASSWORD = _yaml.get("mongodb", {}).get("password")
    MONGO_AUTH_SRC = _yaml.get("mongodb", {}).get("auth_source", "admin")

    # App
    APP_TITLE   = _yaml.get("app", {}).get("title", "Farm Irrigation Workbench")
    APP_VERSION = _yaml.get("app", {}).get("version", "0.1.0")

    # Defaults
    DEFAULTS = _yaml.get("defaults", {})

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


# ensure runtime folders exist
for d in (Config.IMPORT_DIR, Config.EXPORT_DIR, Config.LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)