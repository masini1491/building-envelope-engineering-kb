"""Numerical comparison helpers for calculation-document review.

Tolerance here describes numerical agreement only. It is not an engineering acceptance limit.
"""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Comparison:
    reported: float
    recomputed: float
    absolute_difference: float
    relative_difference: float | None
    status: str


def compare_values(
    reported: float,
    recomputed: float,
    *,
    abs_tol: float = 1e-9,
    rel_tol: float = 1e-6,
) -> Comparison:
    if abs_tol < 0 or rel_tol < 0:
        raise ValueError("tolerances must be non-negative")
    reported = float(reported)
    recomputed = float(recomputed)
    if not math.isfinite(reported) or not math.isfinite(recomputed):
        raise ValueError("reported and recomputed values must be finite")

    diff = abs(reported - recomputed)
    scale = max(abs(reported), abs(recomputed))
    relative = None if scale == 0 else diff / scale
    matched = math.isclose(reported, recomputed, abs_tol=abs_tol, rel_tol=rel_tol)
    return Comparison(
        reported=reported,
        recomputed=recomputed,
        absolute_difference=diff,
        relative_difference=relative,
        status="MATCH" if matched else "MISMATCH",
    )
