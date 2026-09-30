"""Manifold generation helpers."""
from __future__ import annotations

import math


def manifold_from_rows(
    row_centers_uphill: list[tuple[float, float]],
    offset_uphill_m: float = 2.0,
) -> list[tuple[float, float]]:
    """
    Given row uphill endpoints (unsorted), produce a manifold line
    running perpendicular to the rows (i.e., joining them).
    """
    if not row_centers_uphill:
        return []
    xs = [p[0] for p in row_centers_uphill]
    ys = [p[1] for p in row_centers_uphill]
    # Sort by x (rows run along X in rotated frame; manifold runs along Y)
    pairs = sorted(zip(xs, ys))
    x0, y0 = pairs[0]
    x1, y1 = pairs[-1]
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return [(x0, y0)]
    ux, uy = dx / length, dy / length
    return [
        (x0 + ux * offset_uphill_m, y0 + uy * offset_uphill_m),
        (x1 + ux * offset_uphill_m, y1 + uy * offset_uphill_m),
    ]