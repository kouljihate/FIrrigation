"""Assign elevations to generated points from reference vertices."""
from __future__ import annotations

import math


def nearest_vertex(
    ref_pts: list[tuple[float, float, float]],
    lon: float,
    lat: float,
) -> float:
    best_d2, best_ele = 1e18, 0.0
    for plon, plat, pele in ref_pts:
        d2 = (plon - lon) ** 2 + (plat - lat) ** 2
        if d2 < best_d2:
            best_d2, best_ele = d2, pele
    return best_ele


def linear_between(e0: float, e1: float, t: float) -> float:
    t = max(0.0, min(1.0, t))
    return e0 + t * (e1 - e0)