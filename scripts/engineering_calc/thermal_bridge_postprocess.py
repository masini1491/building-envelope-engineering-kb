"""受限二維熱橋溫度因子與線熱傳透率後處理。

本模組只處理已求解的 ThermalBridge2DResult；不猜測室內表面、熱流
邊界、參考尺寸、材料或合格門檻，不宣稱 ISO 10211／13788 合規。
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

from .thermal_bridge_2d import (
    VALIDATION_SCOPE,
    ThermalBridge2DResult,
    ThermalBridgeInputError,
)


POSTPROCESS_STATUS = "NUMERICAL_POSTPROCESS_ONLY"
ENGINEERING_ACCEPTANCE = "NOT_ADMITTED"


@dataclass(frozen=True)
class TemperatureFactorResult:
    minimum_surface_temperature_c: float
    minimum_surface_node_index: int
    temperature_factor_frsi: float
    selected_node_count: int
    source_validation_scope: str
    calculation_status: str = POSTPROCESS_STATUS
    engineering_acceptance: str = ENGINEERING_ACCEPTANCE


@dataclass(frozen=True)
class LinearThermalTransmittanceResult:
    coupling_coefficient_l2d_w_mk: float
    reference_transmittance_w_mk: float
    linear_transmittance_psi_w_mk: float
    dimension_reference: str
    included_interior_boundaries: tuple[str, ...]
    source_validation_scope: str
    calculation_status: str = POSTPROCESS_STATUS
    engineering_acceptance: str = ENGINEERING_ACCEPTANCE


def _number(value: float, label: str) -> float:
    if isinstance(value, bool):
        raise ThermalBridgeInputError(f"{label} must be a finite real number")
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ThermalBridgeInputError(f"{label} must be numeric") from exc
    if not math.isfinite(parsed):
        raise ThermalBridgeInputError(f"{label} must be finite")
    return parsed


def _result(value: ThermalBridge2DResult) -> ThermalBridge2DResult:
    if not isinstance(value, ThermalBridge2DResult):
        raise ThermalBridgeInputError("requires an existing ThermalBridge2DResult")
    if value.compliance_status != "NUMERICAL_BACKEND_ONLY" or value.validation_scope != VALIDATION_SCOPE:
        raise ThermalBridgeInputError("source validation scope mismatch")
    if not value.node_temperature_c or not isinstance(value.boundary_heat_flow_w_per_m, dict):
        raise ThermalBridgeInputError("missing thermal solver result")
    for n, temperature in enumerate(value.node_temperature_c):
        _number(temperature, f"node_temperature_c[{n}]")
    for name, flow in value.boundary_heat_flow_w_per_m.items():
        if not isinstance(name, str) or not name.strip():
            raise ThermalBridgeInputError("invalid boundary heat-flow name")
        _number(flow, f"heat flow {name}")
    return value


def _temperatures(indoor_temperature_c: float, outdoor_temperature_c: float) -> tuple[float, float]:
    inside = _number(indoor_temperature_c, "indoor_temperature_c")
    outside = _number(outdoor_temperature_c, "outdoor_temperature_c")
    if inside <= outside:
        raise ThermalBridgeInputError("heating-only: indoor temperature must exceed outdoor temperature")
    return inside, outside


def compute_temperature_factor_frsi(
    result: ThermalBridge2DResult,
    *,
    interior_surface_node_indices: Sequence[int],
    indoor_temperature_c: float,
    outdoor_temperature_c: float,
) -> TemperatureFactorResult:
    """Calculate fRsi at the coldest explicitly selected interior surface node.

    Caller must supply *all* relevant interior surface nodes, verify the
    surface-resistance/boundary contract, and independently verify mesh quality.
    P1 triangular boundary interpolation is linear between selected end nodes.
    """
    result = _result(result)
    indoor, outdoor = _temperatures(indoor_temperature_c, outdoor_temperature_c)
    if not interior_surface_node_indices:
        raise ThermalBridgeInputError("interior surface node selection is required")
    selected: set[int] = set()
    for index in interior_surface_node_indices:
        if isinstance(index, bool) or not isinstance(index, int):
            raise ThermalBridgeInputError("surface node indices must be integers")
        if index < 0 or index >= len(result.node_temperature_c) or index in selected:
            raise ThermalBridgeInputError("surface node index is invalid or duplicated")
        selected.add(index)
    coldest = min(sorted(selected), key=lambda i: (result.node_temperature_c[i], i))
    surface = float(result.node_temperature_c[coldest])
    factor = (surface - outdoor) / (indoor - outdoor)
    if not math.isfinite(factor):
        raise ThermalBridgeInputError("non-finite temperature factor")
    return TemperatureFactorResult(
        minimum_surface_temperature_c=surface,
        minimum_surface_node_index=coldest,
        temperature_factor_frsi=factor,
        selected_node_count=len(selected),
        source_validation_scope=result.validation_scope,
    )


def compute_linear_transmittance_psi(
    result: ThermalBridge2DResult,
    *,
    interior_heat_flow_boundary_names: Sequence[str],
    indoor_temperature_c: float,
    outdoor_temperature_c: float,
    reference_u_length_pairs: Sequence[tuple[float, float]],
    dimension_reference: str,
) -> LinearThermalTransmittanceResult:
    """Compute L2D - sum(U_i * l_i), for explicitly defined reference lengths.

    Each selected boundary must be an actual complete indoor-to-domain
    heat-flow component, positive in the heating direction. The caller owns
    interior/exterior dimension consistency, physical U-values, and boundary
    completeness; the solver result alone cannot independently prove them.
    """
    result = _result(result)
    indoor, outdoor = _temperatures(indoor_temperature_c, outdoor_temperature_c)
    if dimension_reference not in ("internal", "external"):
        raise ThermalBridgeInputError("dimension_reference must be internal or external")
    if not interior_heat_flow_boundary_names:
        raise ThermalBridgeInputError("at least one interior heat-flow boundary is required")
    boundary_names: list[str] = []
    for name in interior_heat_flow_boundary_names:
        if not isinstance(name, str) or not name.strip() or name in boundary_names:
            raise ThermalBridgeInputError("boundary names must be unique non-empty strings")
        if name not in result.boundary_heat_flow_w_per_m:
            raise ThermalBridgeInputError(f"boundary heat-flow not found: {name}")
        boundary_names.append(name)
    if not reference_u_length_pairs:
        raise ThermalBridgeInputError("reference U/length pairs are required")
    terms: list[float] = []
    for index, pair in enumerate(reference_u_length_pairs):
        try:
            if len(pair) != 2:
                raise ValueError("pair must have 2 entries")
            u, length = pair
        except (TypeError, ValueError) as exc:
            raise ThermalBridgeInputError("each reference must have U and length") from exc
        u = _number(u, f"U[{index}]")
        length = _number(length, f"length[{index}]")
        if u <= 0 or length <= 0:
            raise ThermalBridgeInputError("reference U and length must be positive")
        terms.append(u * length)
    reference = math.fsum(terms)
    heat_flow = math.fsum(result.boundary_heat_flow_w_per_m[name] for name in boundary_names)
    if not math.isfinite(heat_flow) or not math.isfinite(reference) or heat_flow <= 0:
        raise ThermalBridgeInputError("heating-direction heat flow must be finite and positive")
    l2d = heat_flow / (indoor - outdoor)
    psi = l2d - reference
    if not math.isfinite(l2d) or not math.isfinite(psi):
        raise ThermalBridgeInputError("non-finite linear thermal transmittance")
    return LinearThermalTransmittanceResult(
        coupling_coefficient_l2d_w_mk=l2d,
        reference_transmittance_w_mk=reference,
        linear_transmittance_psi_w_mk=psi,
        dimension_reference=dimension_reference,
        included_interior_boundaries=tuple(boundary_names),
        source_validation_scope=result.validation_scope,
    )
