"""Bounded steady-state 1D center-of-glass surface condensation screening.

All inputs must be caller-confirmed; no glass, frame or spacer material catalog.
Not an ISO 13788 compliance evaluation or a 2D thermal-bridge assessment.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


class CondensationInputError(ValueError):
    """Required numerical facts or method assumptions are invalid."""


@dataclass(frozen=True)
class CondensationScreenResult:
    interior_surface_temperature_c: float
    indoor_dew_point_c: float
    temperature_factor_frsi: float | None
    surface_condensation_status: str
    method: str = "ONE_DIMENSIONAL_STEADY_STATE_U_RSI"
    assessment_scope: str = "CENTER_OF_GLAZING_SURFACE_ONLY"
    compliance_status: str = "SCREENING_ONLY_NOT_ISO_COMPLIANCE"


def _number(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise CondensationInputError(f"{name} must be a numeric value")
    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise CondensationInputError(f"{name} must be a numeric value") from exc
    if not math.isfinite(result):
        raise CondensationInputError(f"{name} must be finite")
    return result


def screen_center_glass_condensation(
    *,
    indoor_temperature_c: float,
    outdoor_temperature_c: float,
    indoor_relative_humidity_pct: float,
    glazing_u_value_w_m2k: float,
    interior_surface_resistance_m2k_w: float,
) -> CondensationScreenResult:
    """Compare a one-dimensional surface estimate against indoor dew point.

    T_si = T_i - U * R_si * (T_i - T_o).
    Magnus approximate dew point uses a=17.62, b=243.12 degrees Celsius;
    it is an empirical screening relation, not a regulatory acceptance formula.
    The supplied U-value and R_si must describe the same center-of-glass path.
    No minimum frame/spacer temperature or mold risk may be inferred.
    """
    ti = _number(indoor_temperature_c, "indoor_temperature_c")
    to = _number(outdoor_temperature_c, "outdoor_temperature_c")
    rh = _number(indoor_relative_humidity_pct, "indoor_relative_humidity_pct")
    u = _number(glazing_u_value_w_m2k, "glazing_u_value_w_m2k")
    rsi = _number(interior_surface_resistance_m2k_w, "interior_surface_resistance_m2k_w")
    if not -40.0 <= ti <= 60.0 or not -40.0 <= to <= 60.0:
        raise CondensationInputError("temperature inputs must lie within -40 to 60 C")
    if not 0.0 < rh <= 100.0:
        raise CondensationInputError("indoor_relative_humidity_pct must be > 0 and <= 100")
    if u <= 0.0 or rsi <= 0.0:
        raise CondensationInputError("U-value and interior surface resistance must be > 0")
    if u * rsi > 1.0:
        raise CondensationInputError("U * R_si cannot exceed 1 for the prescribed 1D resistance path")

    tsi = ti - u * rsi * (ti - to)
    a, b = 17.62, 243.12
    gamma = math.log(rh / 100.0) + a * ti / (b + ti)
    dew_point = b * gamma / (a - gamma)
    if not math.isfinite(dew_point):
        raise CondensationInputError("dew-point approximation is not finite")
    factor = None if ti == to else (tsi - to) / (ti - to)
    status = (
        "POSSIBLE_SURFACE_CONDENSATION"
        if tsi <= dew_point
        else "NO_CONDENSATION_IN_THIS_1D_MODEL"
    )
    return CondensationScreenResult(
        interior_surface_temperature_c=tsi,
        indoor_dew_point_c=dew_point,
        temperature_factor_frsi=factor,
        surface_condensation_status=status,
    )
