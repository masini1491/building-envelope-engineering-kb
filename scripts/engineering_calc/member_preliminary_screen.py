"""帷幕鋁直料／橫料初步方案比較：受限單跨、全跨均布橫向荷載。

只計算線彈性小變形的荷載需求、彎曲應力與撓度；輸入區間由
caller 提供並有來源。區間是獨立端點組合下的 mathematical envelope，
不是機率信賴區間，也不是 ADM 容量／安全鑑定。
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

from .beam import simple_span_udl


class MemberScreenInputError(ValueError):
    """輸入缺少可信的結構模型、單位或有界數值。"""


@dataclass(frozen=True)
class NumericInterval:
    minimum: float
    maximum: float


@dataclass(frozen=True)
class WindCaseScreen:
    name: str
    direction: str
    line_load_n_per_mm: NumericInterval
    max_shear_n: NumericInterval
    max_moment_n_mm: NumericInterval
    max_deflection_mm: NumericInterval
    extreme_fiber_stress_mpa: NumericInterval
    deflection_limit_comparison: str


@dataclass(frozen=True)
class MemberOptionScreen:
    name: str
    support_model: str
    cases: tuple[WindCaseScreen, ...]


@dataclass(frozen=True)
class MemberPreliminaryScreen:
    member_role: str
    options: tuple[MemberOptionScreen, ...]
    analysis_model: str = "SINGLE_SPAN_UNIFORM_TRANSVERSE_LOAD_LINEAR_ELASTIC"
    interval_interpretation: str = "CALLER_BOUNDED_INDEPENDENT_ENDPOINT_ENVELOPE_NOT_STATISTICAL"
    source_status: str = "USER_DECLARED_NOT_INDEPENDENTLY_VERIFIED"
    acceptance_status: str = "NOT_ADMITTED"
    unevaluated_modes: tuple[str, ...] = (
        "ADM_MEMBER_CAPACITY", "LOCAL_BUCKLING", "LATERAL_TORSIONAL_BUCKLING",
        "SHEAR_CAPACITY", "CONNECTIONS", "TORSION", "COMBINED_ACTIONS",
        "SHEAR_DEFORMATION", "SECOND_ORDER_EFFECTS",
    )


def _map(value: object, label: str) -> Mapping:
    if not isinstance(value, Mapping):
        raise MemberScreenInputError(f"{label} must be an object")
    return value


def _text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MemberScreenInputError(f"{label} must be a nonempty string")
    return value.strip()


def _number(value: object, label: str, *, positive: bool = True) -> float:
    if isinstance(value, bool):
        raise MemberScreenInputError(f"{label} must be a finite numeric value")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise MemberScreenInputError(f"{label} must be numeric") from exc
    if not isfinite(result) or result < 0 or (positive and result == 0):
        raise MemberScreenInputError(f"{label} must be finite and {'positive' if positive else 'nonnegative'}")
    return result


def _interval(value: object, label: str, *, positive: bool = True) -> NumericInterval:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise MemberScreenInputError(f"{label} must be [minimum, maximum]")
    lo = _number(value[0], f"{label}[0]", positive=positive)
    hi = _number(value[1], f"{label}[1]", positive=positive)
    if lo > hi or (not positive and hi == 0):
        raise MemberScreenInputError(f"{label} bounds must be ordered with a nonzero upper bound")
    return NumericInterval(lo, hi)


def _finite_interval(lo: float, hi: float, label: str) -> NumericInterval:
    if not isfinite(lo) or not isfinite(hi) or lo < 0 or lo > hi:
        raise MemberScreenInputError(f"{label}: output overflow or inverted interval")
    return NumericInterval(lo, hi)


def _scenario(q: float, span_mm: float, E_mpa: float, I_mm4: float, Z_mm3: float,
              model: str) -> tuple[float, float, float, float]:
    if model == "simply_supported":
        beam = simple_span_udl(span=span_mm, line_load=q,
                               elastic_modulus=E_mpa, inertia=I_mm4)
        shear, moment, delta = beam.shear_max, beam.moment_max, beam.deflection_max
    else:
        # Ideal, fully fixed cantilever only; not a semi-rigid connection.
        shear = q * span_mm
        moment = q * span_mm ** 2 / 2.0
        delta = q * span_mm ** 4 / (8.0 * E_mpa * I_mm4)
    stress = moment / Z_mm3
    if not all(isfinite(x) and x >= 0 for x in (shear, moment, delta, stress)):
        raise MemberScreenInputError("nonfinite screen result; check ranges and unit scales")
    return shear, moment, delta, stress


def _deflection_comparison(bounds: NumericInterval, limit: float | None) -> str:
    if limit is None:
        return "NOT_EVALUATED_NO_USER_CRITERION"
    if bounds.minimum > limit:
        return "ALL_MODELED_SCENARIOS_EXCEED_SUPPLIED_LIMIT"
    if bounds.maximum > limit:
        return "MIXED_MODEL_SCENARIOS_AGAINST_SUPPLIED_LIMIT"
    return "ALL_MODELED_SCENARIOS_WITHIN_SUPPLIED_LIMIT_NOT_ENGINEERING_PASS"


def screen_preliminary_member_options(
    *,
    member_role: str,
    span_m_range: Sequence[float],
    span_source: str,
    tributary_width_m_range: Sequence[float],
    tributary_width_source: str,
    elastic_modulus_mpa_range: Sequence[float],
    elastic_modulus_source: str,
    wind_cases: Sequence[Mapping],
    options: Sequence[Mapping],
    deflection_limit_mm: float | None = None,
    deflection_limit_source: str | None = None,
) -> MemberPreliminaryScreen:
    """Compare explicitly supplied single-span options; never infer ADM capacities.

    p[kPa] * b[m] = q[N/mm]. Options require both S+ and S- because
    asymmetric extrusion / pressure direction may have different extreme fibres.
    The caller confirms that these S values match the load/support moment sign.
    """
    if member_role not in ("mullion", "transom"):
        raise MemberScreenInputError("member_role must be mullion or transom")
    span = _interval(span_m_range, "span_m_range")
    width = _interval(tributary_width_m_range, "tributary_width_m_range")
    E = _interval(elastic_modulus_mpa_range, "elastic_modulus_mpa_range")
    _text(span_source, "span_source")
    _text(tributary_width_source, "tributary_width_source")
    _text(elastic_modulus_source, "elastic_modulus_source")
    limit = None
    if deflection_limit_mm is not None:
        limit = _number(deflection_limit_mm, "deflection_limit_mm")
        _text(deflection_limit_source, "deflection_limit_source")
    elif deflection_limit_source is not None:
        raise MemberScreenInputError("deflection_limit_source without criterion")
    if not isinstance(wind_cases, (list, tuple)) or not wind_cases:
        raise MemberScreenInputError("wind_cases must be a nonempty array")
    if not isinstance(options, (list, tuple)) or not options:
        raise MemberScreenInputError("options must be a nonempty array")

    cases = []
    case_names: set[str] = set()
    for raw in wind_cases:
        obj = _map(raw, "wind case")
        name = _text(obj.get("name"), "wind case name")
        direction = _text(obj.get("direction"), "wind case direction")
        if direction not in ("positive", "negative") or name in case_names:
            raise MemberScreenInputError("wind cases require unique names and positive/negative direction")
        case_names.add(name)
        pressure = _interval(obj.get("pressure_magnitude_kpa_range"),
                             f"{name}.pressure_magnitude_kpa_range", positive=False)
        _text(obj.get("pressure_source"), f"{name}.pressure_source")
        cases.append((name, direction, pressure))

    evaluated = []
    option_names: set[str] = set()
    for raw in options:
        obj = _map(raw, "member option")
        name = _text(obj.get("name"), "option name")
        support = _text(obj.get("support_model"), f"{name}.support_model")
        if name in option_names or support not in ("simply_supported", "cantilever"):
            raise MemberScreenInputError("options require unique names and supported ideal end restraints")
        option_names.add(name)
        _text(obj.get("support_source"), f"{name}.support_source")
        _text(obj.get("section_property_source"), f"{name}.section_property_source")
        I = _interval(obj.get("inertia_mm4_range"), f"{name}.inertia_mm4_range")
        Zplus = _interval(obj.get("section_modulus_positive_mm3_range"),
                          f"{name}.section_modulus_positive_mm3_range")
        Zminus = _interval(obj.get("section_modulus_negative_mm3_range"),
                           f"{name}.section_modulus_negative_mm3_range")
        outputs = []
        for case_name, direction, pressure in cases:
            Z = Zplus if direction == "positive" else Zminus
            q_min = pressure.minimum * width.minimum
            q_max = pressure.maximum * width.maximum
            _finite_interval(q_min, q_max, "line load")
            # All demand formulas are monotone for positive inputs on the
            # supported ideal beams. Caller intervals are independently combined;
            # correlation is not known or inferred.
            min_shear, min_moment, min_defl, min_stress = _scenario(
                q_min, span.minimum * 1000.0, E.maximum, I.maximum, Z.maximum, support)
            max_shear, max_moment, max_defl, max_stress = _scenario(
                q_max, span.maximum * 1000.0, E.minimum, I.minimum, Z.minimum, support)
            delta = _finite_interval(min_defl, max_defl, "deflection")
            outputs.append(WindCaseScreen(
                name=case_name, direction=direction,
                line_load_n_per_mm=_finite_interval(q_min, q_max, "line load"),
                max_shear_n=_finite_interval(min_shear, max_shear, "shear"),
                max_moment_n_mm=_finite_interval(min_moment, max_moment, "moment"),
                max_deflection_mm=delta,
                extreme_fiber_stress_mpa=_finite_interval(min_stress, max_stress, "stress"),
                deflection_limit_comparison=_deflection_comparison(delta, limit),
            ))
        evaluated.append(MemberOptionScreen(name=name, support_model=support, cases=tuple(outputs)))
    return MemberPreliminaryScreen(member_role=member_role, options=tuple(evaluated))
