"""Pydantic validation schemas for API endpoints."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class SectorSave(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    coords: str = Field(..., min_length=1)

    @field_validator("coords")
    @classmethod
    def validate_coords(cls, v: str) -> str:
        lines = [line.strip() for line in v.splitlines() if line.strip()]
        if len(lines) < 3:
            raise ValueError("need at least 3 coordinate lines")
        for line in lines:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2:
                raise ValueError(f"bad line: {line}")
            try:
                float(parts[0])
                float(parts[1])
            except ValueError:
                raise ValueError(f"not a number: {line}")
        return v


class ZoneBuild(BaseModel):
    n_parts: int = Field(default=3, ge=1, le=20)
    offset: float = Field(default=0.0, ge=0)
    split_mode: str = Field(default="contour")

    @field_validator("split_mode")
    @classmethod
    def validate_split_mode(cls, v: str) -> str:
        if v not in ("contour", "fan", "strip"):
            raise ValueError(f"unknown split_mode: {v}")
        return v


class MainlineBuild(BaseModel):
    offset: float = Field(default=5.0, ge=0)
    diameter: int = Field(default=75, gt=0)


class SubmainBuild(BaseModel):
    offset: float = Field(default=5.0, ge=0)
    diameter: int = Field(default=32, gt=0)


class RowBuild(BaseModel):
    spacing: float = Field(default=4.0, gt=0)
    offset: float = Field(default=2.0, ge=0)


class TreePlace(BaseModel):
    spacing: float = Field(default=4.0, gt=0)
    fig_pct: int = Field(default=20, ge=0, le=100)


class DriplineBuild(BaseModel):
    emitter_spacing: float = Field(default=0.5, gt=0)


class BasinCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    lon: float
    lat: float
    elev: float = Field(default=0.0)
    size: float = Field(default=30.0, gt=0)


class NewProject(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=100)


def validate_json(model: type[BaseModel]) -> Any:
    """Decorator to validate request JSON against a Pydantic model."""
    from functools import wraps
    from flask import request, jsonify

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return jsonify({"ok": False, "error": "Content-Type must be application/json"}), 400
            try:
                data = model(**request.get_json())
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)}), 400
            return f(data, *args, **kwargs)
        return wrapper
    return decorator


def validate_form(model: type[BaseModel]) -> Any:
    """Decorator to validate request form data against a Pydantic model."""
    from functools import wraps
    from flask import request, jsonify

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                data = model(**request.form.to_dict())
            except Exception as e:
                return jsonify({"ok": False, "error": str(e)}), 400
            return f(data, *args, **kwargs)
        return wrapper
    return decorator