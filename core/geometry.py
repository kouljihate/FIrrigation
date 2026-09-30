"""Shapely helpers used across the workbench."""
from __future__ import annotations

import math

from shapely.geometry import Polygon, LineString, Point, MultiPolygon, mapping, shape
from shapely.validation import make_valid


def polygon_from_geojson(geom: dict) -> Polygon:
    return shape(geom)


def geojson_from_polygon(poly: Polygon) -> dict:
    return mapping(poly)


def clean_polygon(poly: Polygon) -> Polygon:
    if poly.is_valid:
        return poly
    fixed = make_valid(poly)
    if fixed.geom_type == "MultiPolygon":
        fixed = max(fixed.geoms, key=lambda g: g.area)
    return fixed


def polygon_area_m2(poly: Polygon) -> float:
    return float(poly.area)


def fall_direction(poly: Polygon, elevations: list[float]) -> tuple[float, float]:
    """Return (ux, uy) unit vector pointing downhill."""
    import numpy as np
    coords = list(poly.exterior.coords)[:-1]
    xs = np.array([c[0] for c in coords])
    ys = np.array([c[1] for c in coords])
    zs = np.array(elevations[:len(coords)])
    cx, cy = xs.mean(), ys.mean()
    A = np.column_stack([xs - cx, ys - cy, np.ones_like(xs)])
    coef, *_ = np.linalg.lstsq(A, zs, rcond=None)
    gx, gy = -coef[0], -coef[1]
    n = math.hypot(gx, gy)
    if n < 1e-9:
        return (1.0, 0.0)
    return (gx / n, gy / n)


def inward_offset(poly: Polygon, meters: float) -> Polygon:
    inner = poly.buffer(-meters, join_style=2)
    if inner.is_empty:
        raise ValueError(f"Offset {meters} m is too large for polygon")
    if inner.geom_type == "MultiPolygon":
        inner = max(inner.geoms, key=lambda g: g.area)
    return inner


def line_inside(poly: Polygon, p1: tuple[float, float], p2: tuple[float, float]) -> bool:
    return poly.contains(LineString([p1, p2]))