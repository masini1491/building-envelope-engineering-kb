"""Explicit-case continuous multi-span curtain-wall member screening.

Numerical demand only. All interior supports remain rotationally continuous; every
node is vertically supported. Beam is Euler-Bernoulli and load is constant on
each span. User-declared cases are discrete samples, NOT interval bounds.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from .beam import BeamElement, solve_beam
from .beam_extrema import beam_extrema


class MultispanInputError(ValueError):
    """Unsupported/missing bounded structural input."""


@dataclass(frozen=True)
class SpanScreen:
    span_index: int
    maximum_absolute_shear_n: float
    maximum_absolute_moment_n_mm: float
    maximum_absolute_deflection_mm: float
    positive_moment_max_n_mm: float
    negative_moment_magnitude_max_n_mm: float
    maximum_absolute_bending_stress_mpa: float


@dataclass(frozen=True)
class CaseScreen:
    name: str
    maximum_absolute_shear_n: float
    maximum_absolute_moment_n_mm: float
    maximum_absolute_deflection_mm: float
    maximum_absolute_bending_stress_mpa: float
    positive_moment_max_n_mm: float
    negative_moment_magnitude_max_n_mm: float
    deflection_limit_comparison: str
    reactions_n: tuple[float, ...]
    span_results: tuple[SpanScreen, ...]


@dataclass(frozen=True)
class OptionScreen:
    name: str
    support_model: str
    cases: tuple[CaseScreen, ...]


@dataclass(frozen=True)
class MultispanScreen:
    member_role: str
    options: tuple[OptionScreen, ...]
    analysis_model: str = "CONTINUOUS_EULER_BERNOULLI_ALL_NODES_VERTICALLY_RESTRAINED"
    scenario_interpretation: str = "EXPLICIT_DISCRETE_CASES_NOT_UNCERTAINTY_BOUNDS"
    source_status: str = "USER_DECLARED_NOT_INDEPENDENTLY_VERIFIED"
    engineering_acceptance: str = "NOT_ADMITTED"
    unevaluated_modes: tuple[str, ...] = (
        "ADM_MEMBER_CAPACITY", "LOCAL_BUCKLING", "LATERAL_TORSIONAL_BUCKLING",
        "SHEAR_CAPACITY", "CONNECTIONS", "TORSION", "COMBINED_ACTIONS",
        "SHEAR_DEFORMATION", "SECOND_ORDER_EFFECTS", "JOINT_RELEASES",
        "PARTIAL_ROTATIONAL_RESTRAINT", "SUPPORT_SETTLEMENT",
    )


def _source(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MultispanInputError(f"{name} requires a nonempty source")
    return value.strip()


def _num(value: object, name: str, *, positive: bool = True) -> float:
    if isinstance(value, bool):
        raise MultispanInputError(f"{name} must be numeric, not boolean")
    try:
        result = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise MultispanInputError(f"{name} must be numeric") from exc
    if not isfinite(result) or (positive and result <= 0):
        raise MultispanInputError(f"{name} must be finite" + (" and positive" if positive else ""))
    return result


def _values(raw: object, count: int, name: str, *, positive: bool = True) -> tuple[float, ...]:
    if not isinstance(raw, (tuple, list)) or len(raw) != count:
        raise MultispanInputError(f"{name} requires {count} values")
    return tuple(_num(value, f"{name}[{i}]", positive=positive) for i, value in enumerate(raw))


def _object(value: object, name: str, allowed: frozenset[str]) -> Mapping:
    if not isinstance(value, Mapping):
        raise MultispanInputError(f"{name} must be an object")
    extra = set(value) - allowed
    if extra:
        raise MultispanInputError(f"{name} contains unsupported fields")
    return value


_OPTION_FIELDS = frozenset((
    "name", "support_model", "support_source", "continuity_source",
    "material_source", "section_property_source", "elastic_modulus_mpa",
    "inertia_mm4_by_span", "section_modulus_positive_mm3_by_span",
    "section_modulus_negative_mm3_by_span",
))
_CASE_FIELDS = frozenset(("name", "signed_pressure_kpa_by_span", "pressure_source"))


def _moments(end_actions, q: float, L: float) -> tuple[float, float]:
    """Physical signed moment extrema, including zero-shear interior station."""
    m0 = -end_actions.start_moment
    v0 = end_actions.start_shear
    points = [0.0, L]
    if q:
        station = -v0 / q
        if 0.0 < station < L:
            points.append(station)
    values = [m0 + v0 * x + 0.5 * q * x * x for x in points]
    if not all(isfinite(value) for value in values):
        raise MultispanInputError("nonfinite moment result")
    return max(0.0, *values), max(0.0, *(-value for value in values))


def screen_multispan_options(
    *,
    member_role: str,
    span_lengths_m: list[float],
    span_source: str,
    tributary_widths_m: list[float],
    tributary_width_source: str,
    wind_cases: list[Mapping],
    options: list[Mapping],
    deflection_limit_mm: float | None = None,
    deflection_limit_source: str | None = None,
) -> MultispanScreen:
    if member_role not in ("mullion", "transom"):
        raise MultispanInputError("member_role must be mullion/transom")
    if not isinstance(span_lengths_m, list) or not 2 <= len(span_lengths_m) <= 6:
        raise MultispanInputError("span_lengths_m requires 2 to 6 continuous spans")
    n = len(span_lengths_m)
    lengths = _values(span_lengths_m, n, "span_lengths_m")
    widths = _values(tributary_widths_m, n, "tributary_widths_m")
    _source(span_source, "span_source")
    _source(tributary_width_source, "tributary_width_source")
    limit = None
    if deflection_limit_mm is not None:
        limit = _num(deflection_limit_mm, "deflection_limit_mm")
        _source(deflection_limit_source, "deflection_limit_source")
    elif deflection_limit_source is not None:
        raise MultispanInputError("deflection_limit_source requires a limit")
    if not isinstance(wind_cases, list) or not wind_cases or len(wind_cases) > 12:
        raise MultispanInputError("wind_cases requires 1-12 explicit cases")
    if not isinstance(options, list) or not options or len(options) > 12:
        raise MultispanInputError("options requires 1-12 explicit sections")
    positions = [0.0]
    for length in lengths:
        end_position = positions[-1] + length * 1000.0
        if not isfinite(end_position) or end_position <= positions[-1]:
            raise MultispanInputError("invalid span positions")
        positions.append(end_position)

    loads = []
    names: set[str] = set()
    for i, raw in enumerate(wind_cases):
        case = _object(raw, f"wind_cases[{i}]", _CASE_FIELDS)
        name = _source(case.get("name"), "wind case name")
        _source(case.get("pressure_source"), f"{name}.pressure_source")
        if name in names:
            raise MultispanInputError("wind case names must be unique")
        names.add(name)
        pressures = _values(case.get("signed_pressure_kpa_by_span"), n,
                            f"{name}.signed_pressure_kpa_by_span", positive=False)
        if all(p == 0 for p in pressures):
            raise MultispanInputError("all-zero wind case has no load to screen")
        line_loads = tuple(p * width for p, width in zip(pressures, widths))
        if not all(isfinite(q) for q in line_loads):
            raise MultispanInputError("line-load overflow")
        loads.append((name, line_loads))

    results = []
    option_names: set[str] = set()
    for i, raw in enumerate(options):
        option = _object(raw, f"options[{i}]", _OPTION_FIELDS)
        name = _source(option.get("name"), "option name")
        support = _source(option.get("support_model"), f"{name}.support_model")
        if name in option_names:
            raise MultispanInputError("option names must be unique")
        option_names.add(name)
        if support not in ("continuous_pinned_supports", "continuous_fixed_ends"):
            raise MultispanInputError("unsupported support_model")
        _source(option.get("support_source"), f"{name}.support_source")
        _source(option.get("continuity_source"), f"{name}.continuity_source")
        _source(option.get("material_source"), f"{name}.material_source")
        _source(option.get("section_property_source"), f"{name}.section_property_source")
        E = _num(option.get("elastic_modulus_mpa"), f"{name}.elastic_modulus_mpa")
        inertia = _values(option.get("inertia_mm4_by_span"), n, f"{name}.inertia_mm4_by_span")
        s_pos = _values(option.get("section_modulus_positive_mm3_by_span"), n,
                        f"{name}.section_modulus_positive_mm3_by_span")
        s_neg = _values(option.get("section_modulus_negative_mm3_by_span"), n,
                        f"{name}.section_modulus_negative_mm3_by_span")
        case_results = []
        for case_name, q_by_span in loads:
            elements = [BeamElement(i, i+1, E, inertia[i], q_by_span[i]) for i in range(n)]
            try:
                beam = solve_beam(
                    node_positions=positions, elements=elements,
                    vertical_restraints=range(n+1),
                    rotational_restraints=(0, n) if support == "continuous_fixed_ends" else (),
                )
                elem_extrema, global_extrema = beam_extrema(
                    node_positions=positions, elements=elements, result=beam)
            except (ValueError, OverflowError, ZeroDivisionError) as exc:
                raise MultispanInputError(f"beam cannot solve for {name}/{case_name}: {exc}") from exc
            per_span = []
            for j, (element, end, ext) in enumerate(
                    zip(elements, beam.element_end_forces, elem_extrema)):
                positive, negative = _moments(end, q_by_span[j], lengths[j]*1000.0)
                stress = max(positive/s_pos[j], negative/s_neg[j])
                values = (ext.max_abs_shear, ext.max_abs_moment,
                          ext.max_abs_deflection, positive, negative, stress)
                if not all(isfinite(v) and v >= 0 for v in values):
                    raise MultispanInputError("nonfinite/invalid case result")
                per_span.append(SpanScreen(j, *values))
            max_delta = global_extrema.max_abs_deflection
            if limit is None:
                comparison = "NOT_EVALUATED_NO_USER_CRITERION"
            elif max_delta > limit:
                comparison = "MODELED_CASE_EXCEEDS_USER_LIMIT"
            else:
                comparison = "MODELED_CASE_WITHIN_USER_LIMIT_NOT_ENGINEERING_PASS"
            reactions = tuple(float(v) for v in beam.reactions)
            if not all(isfinite(v) for v in reactions):
                raise MultispanInputError("nonfinite support reaction")
            case_results.append(CaseScreen(
                name=case_name,
                maximum_absolute_shear_n=global_extrema.max_abs_shear,
                maximum_absolute_moment_n_mm=global_extrema.max_abs_moment,
                maximum_absolute_deflection_mm=max_delta,
                maximum_absolute_bending_stress_mpa=max(x.maximum_absolute_bending_stress_mpa for x in per_span),
                positive_moment_max_n_mm=max(x.positive_moment_max_n_mm for x in per_span),
                negative_moment_magnitude_max_n_mm=max(x.negative_moment_magnitude_max_n_mm for x in per_span),
                deflection_limit_comparison=comparison,
                reactions_n=reactions, span_results=tuple(per_span),
            ))
        results.append(OptionScreen(name, support, tuple(case_results)))
    return MultispanScreen(member_role, tuple(results))
