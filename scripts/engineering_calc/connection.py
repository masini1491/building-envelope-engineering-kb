"""Deterministic connection-demand arithmetic for calculation review.

This module intentionally does not contain material allowables, fastener capacities,
safety factors, or standard-derived interaction equations. Capacity values must come
from a traceable external engineering authority and be supplied explicitly.
"""

from dataclasses import dataclass
from math import hypot, isfinite


@dataclass(frozen=True)
class DemandCapacityResult:
    demand: float
    capacity: float
    utilization: float
    status: str


@dataclass(frozen=True)
class ShearTensionDemand:
    shear: float
    tension: float
    shear_capacity: float | None
    tension_capacity: float | None
    shear_utilization: float | None
    tension_utilization: float | None


def demand_capacity(*, demand: float, capacity: float) -> DemandCapacityResult:
    """Compare one non-negative demand magnitude with an explicitly supplied capacity.

    ``status`` is scope-qualified to this single arithmetic comparison only.
    """
    demand = abs(float(demand))
    capacity = float(capacity)
    if not isfinite(demand) or not isfinite(capacity) or capacity <= 0:
        raise ValueError("demand must be finite and capacity must be finite and > 0")
    utilization = demand / capacity
    return DemandCapacityResult(
        demand=demand,
        capacity=capacity,
        utilization=utilization,
        status="PASS" if utilization <= 1.0 else "FAIL",
    )


def projected_bearing_stress(*, force: float, diameter: float, thickness: float) -> float:
    """Return ``|P| / (d * t)`` for a caller-confirmed projected bearing-area model."""
    force = abs(float(force))
    diameter = float(diameter)
    thickness = float(thickness)
    if not all(isfinite(v) for v in (force, diameter, thickness)):
        raise ValueError("force, diameter and thickness must be finite")
    if diameter <= 0 or thickness <= 0:
        raise ValueError("diameter and thickness must be > 0")
    return force / (diameter * thickness)


def shear_tension_demand(
    *,
    shear_x: float = 0.0,
    shear_y: float = 0.0,
    tension: float = 0.0,
    shear_capacity: float | None = None,
    tension_capacity: float | None = None,
) -> ShearTensionDemand:
    """Resolve shear magnitude and optional independent utilization ratios.

    No combined shear-tension interaction equation is assumed. If the governing
    standard requires interaction, the caller must evaluate that separately using a
    verified method.
    """
    values = [float(shear_x), float(shear_y), float(tension)]
    if not all(isfinite(v) for v in values):
        raise ValueError("demands must be finite")
    shear = hypot(values[0], values[1])
    tension_mag = abs(values[2])

    def _ratio(demand_value: float, capacity_value: float | None) -> tuple[float | None, float | None]:
        if capacity_value is None:
            return None, None
        capacity_float = float(capacity_value)
        if not isfinite(capacity_float) or capacity_float <= 0:
            raise ValueError("capacities must be finite and > 0")
        return capacity_float, demand_value / capacity_float

    shear_capacity_value, shear_ratio = _ratio(shear, shear_capacity)
    tension_capacity_value, tension_ratio = _ratio(tension_mag, tension_capacity)
    return ShearTensionDemand(
        shear=shear,
        tension=tension_mag,
        shear_capacity=shear_capacity_value,
        tension_capacity=tension_capacity_value,
        shear_utilization=shear_ratio,
        tension_utilization=tension_ratio,
    )


def thread_engagement_ratio(*, actual_engagement: float, required_engagement: float) -> DemandCapacityResult:
    """Compare actual with externally established required thread engagement.

    The returned utilization is ``required / actual`` so values <= 1 correspond to
    this narrow geometric requirement being met. This function does not calculate
    the required engagement.
    """
    actual = float(actual_engagement)
    required = float(required_engagement)
    if not all(isfinite(v) for v in (actual, required)) or actual <= 0 or required <= 0:
        raise ValueError("actual_engagement and required_engagement must be finite and > 0")
    utilization = required / actual
    return DemandCapacityResult(
        demand=required,
        capacity=actual,
        utilization=utilization,
        status="PASS" if utilization <= 1.0 else "FAIL",
    )
