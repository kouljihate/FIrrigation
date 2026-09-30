"""Local ENU projection (metres) around a reference lon/lat."""
from __future__ import annotations

import math

R_EARTH = 6371000.0


def to_local(lon: float, lat: float, lon0: float, lat0: float) -> tuple[float, float]:
    x = math.radians(lon - lon0) * R_EARTH * math.cos(math.radians(lat0))
    y = math.radians(lat - lat0) * R_EARTH
    return x, y


def to_lonlat(x: float, y: float, lon0: float, lat0: float) -> tuple[float, float]:
    lon = lon0 + math.degrees(x / (R_EARTH * math.cos(math.radians(lat0))))
    lat = lat0 + math.degrees(y / R_EARTH)
    return lon, lat


def centroid_lonlat(coords: list[tuple[float, float]]) -> tuple[float, float]:
    lon = sum(c[0] for c in coords) / len(coords)
    lat = sum(c[1] for c in coords) / len(coords)
    return lon, lat