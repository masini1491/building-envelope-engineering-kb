"""Elastic in-plane fastener-group arithmetic for independent numerical review.

The model distributes direct Fx/Fy equally and Mz in proportion to radius from the centroid.
It does not determine fastener capacity, prying, local extrusion, pullout, or other failure modes.
"""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class FastenerDemand:
    x: float
    y: float
    fx: float
    fy: float
    resultant: float


@dataclass(frozen=True)
class FastenerGroupResult:
    centroid_x: float
    centroid_y: float
    sum_r2: float
    demands: tuple[FastenerDemand, ...]
    governing_index: int


def elastic_in_plane_group(points, *, fx: float = 0.0, fy: float = 0.0, mz: float = 0.0) -> FastenerGroupResult:
    pts = tuple((float(x), float(y)) for x, y in points)
    if not pts:
        raise ValueError("at least one fastener point is required")

    n = len(pts)
    cx = sum(x for x, _ in pts) / n
    cy = sum(y for _, y in pts) / n
    rel = tuple((x - cx, y - cy) for x, y in pts)
    sum_r2 = sum(x * x + y * y for x, y in rel)
    if mz != 0 and sum_r2 == 0:
        raise ValueError("nonzero Mz requires a fastener group with nonzero radius")

    direct_fx = float(fx) / n
    direct_fy = float(fy) / n
    demands = []
    for (x, y), (rx, ry) in zip(pts, rel):
        # Tangential force from positive Mz: (-y, +x) * Mz / sum(r^2)
        moment_fx = 0.0 if sum_r2 == 0 else -float(mz) * ry / sum_r2
        moment_fy = 0.0 if sum_r2 == 0 else float(mz) * rx / sum_r2
        total_fx = direct_fx + moment_fx
        total_fy = direct_fy + moment_fy
        demands.append(FastenerDemand(x, y, total_fx, total_fy, math.hypot(total_fx, total_fy)))

    governing = max(range(n), key=lambda i: demands[i].resultant)
    return FastenerGroupResult(cx, cy, sum_r2, tuple(demands), governing)
