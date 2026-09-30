"""Flask configuration for the Farm Irrigation Workbench."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class MongoDBConfig(BaseModel):
    host: str = "localhost"
    port: int = Field(default=27017, ge=1, le=65535)
    database: str = "farm_irrigation"
    username: str | None = None
    password: str | None = None
    auth_source: str = "admin"


class PathsConfig(BaseModel):
    imports: str = "imports"
    exports: str = "exports"
    configs: str = "configs"


class AppConfig(BaseModel):
    title: str = "Farm Irrigation Workbench"
    version: str = "1.0.0"
    layout: str = "wide"


class DefaultsConfig(BaseModel):
    project_name: str = "farm_v1"
    row_spacing_m: float = Field(default=4.0, gt=0)
    tree_spacing_m: float = Field(default=4.0, gt=0)
    first_row_offset_m: float = Field(default=2.0, ge=0)
    pipe_main_diameter_mm: int = Field(default=75, gt=0)
    pipe_submain_diameter_mm: int = Field(default=32, gt=0)
    pipe_zone_diameter_mm: int = Field(default=32, gt=0)


class RootConfig(BaseModel):
    app: AppConfig = Field(default_factory=AppConfig)
    mongodb: MongoDBConfig = Field(default_factory=MongoDBConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    defaults: DefaultsConfig = Field(default_factory=DefaultsConfig)


def _load_yaml() -> dict:
    path = BASE_DIR / "config.yaml"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _validate_config(raw: dict) -> RootConfig:
    try:
        return RootConfig(**raw)
    except ValidationError as e:
        errors = "; ".join(f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}" for err in e.errors())
        raise RuntimeError(f"Invalid config.yaml: {errors}") from e


_raw = _load_yaml()
_config = _validate_config(_raw)
_yaml = _config.model_dump()


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
    APP_VERSION = _yaml.get("app", {}).get("version", "1.0.0")

    # Defaults
    DEFAULTS = _yaml.get("defaults", {})

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


# ensure runtime folders exist
for d in (Config.IMPORT_DIR, Config.EXPORT_DIR, Config.LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)