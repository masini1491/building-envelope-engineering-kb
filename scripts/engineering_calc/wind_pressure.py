"""Taiwan 103-code components/cladding design-wind-pressure deterministic kernel.

Admitted scope:
- h > 18 m wall components/cladding under Figure 3.2,
- h <= 18 m wall components/cladding under Figure 3.1(a),
- h <= 18 m gable/hip-roof components/cladding through 45 degrees
  under Figure 3.1(b)-(d),
- enclosed or partially enclosed buildings,
- code-governed wind only.

Natural-language classification stays outside this module. Inputs reaching this kernel must
already be confirmed project facts or deterministic code classifications.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import json
import math
from pathlib import Path
from typing import Any, Mapping

DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "references"
    / "government"
    / "taiwan-wind-code-103-v2.json"
)


class WindPressureInputError(ValueError):
    """Required project/code input is missing or invalid."""


class WindPressureUnsupportedError(ValueError):
    """Requested condition is outside the admitted model."""


def load_reference_data(path: Path | None = None) -> dict[str, Any]:
    target = path or DATA_PATH
    with target.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("dataset_id") != "taiwan-wind-code-103-v2":
        raise WindPressureInputError("unexpected wind reference dataset identity")
    return data


def _normalize_admin_name(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WindPressureInputError("administrative name must be a non-empty string")
    text = value.strip().replace("台", "臺")
    legacy = {
        "桃園縣": "桃園市",
        "臺中縣": "臺中市",
        "臺南縣": "臺南市",
        "高雄縣": "高雄市",
    }
    return legacy.get(text, text)


def resolve_basic_wind_speed(
    region: str,
    district: str | None = None,
    *,
    data: Mapping[str, Any] | None = None,
) -> float:
    """Resolve V10(C) from the admitted 103-code administrative-zone dataset."""
    ref = data or load_reference_data()
    speeds = ref["basic_wind_speed"]
    region_name = _normalize_admin_name(region)
    district_name = _normalize_admin_name(district) if district else None

    probes = [x for x in (district_name, region_name) if x]
    for item in speeds.get("special_locations", []):
        aliases = {_normalize_admin_name(x) for x in item.get("aliases", [])}
        if any(probe in aliases for probe in probes):
            return float(item["v10_mps"])

    whole = speeds.get("whole_regions", {})
    if region_name in whole:
        return float(whole[region_name])

    group = speeds.get("district_groups", {}).get(region_name)
    if not group:
        raise WindPressureInputError(
            f"region is not present in the admitted V10 dataset: {region_name}"
        )
    if not district_name:
        raise WindPressureInputError(
            f"district is required to resolve V10 for {region_name}"
        )

    for value, districts in group.get("groups", {}).items():
        if district_name in {_normalize_admin_name(x) for x in districts}:
            return float(value)
    raise WindPressureInputError(
        f"district is not present in the admitted V10 dataset: {region_name} {district_name}"
    )


def resolve_importance_factor(
    building_category: int | str,
    *,
    data: Mapping[str, Any] | None = None,
) -> float:
    ref = data or load_reference_data()
    key = str(building_category).strip()
    item = ref["importance_factor"].get(key)
    if not item:
        raise WindPressureInputError("building_category must be one of 1, 2, 3, 4, 5")
    return float(item["I"])


def resolve_terrain(
    terrain_category: str,
    *,
    data: Mapping[str, Any] | None = None,
) -> tuple[float, float]:
    ref = data or load_reference_data()
    key = str(terrain_category).strip().upper()
    item = ref["terrain"].get(key)
    if not item:
        raise WindPressureInputError("terrain_category must be A, B, or C")
    return float(item["alpha"]), float(item["zg_m"])


def velocity_pressure(
    height_m: float,
    *,
    terrain_category: str,
    kzt: float,
    importance_factor: float,
    v10_mps: float,
    data: Mapping[str, Any] | None = None,
) -> dict[str, float]:
    """Return K(z), q in kgf/m^2, and q in kPa for code section 2.6."""
    ref = data or load_reference_data()
    z = float(height_m)
    if not math.isfinite(z) or z <= 0:
        raise WindPressureInputError("height must be finite and > 0")
    kzt_value = float(kzt)
    if not math.isfinite(kzt_value) or kzt_value <= 0:
        raise WindPressureInputError("kzt must be finite and > 0")
    factor = float(importance_factor)
    wind = float(v10_mps)
    if not math.isfinite(factor) or factor <= 0:
        raise WindPressureInputError("importance factor must be finite and > 0")
    if not math.isfinite(wind) or wind <= 0:
        raise WindPressureInputError("v10_mps must be finite and > 0")

    alpha, zg_m = resolve_terrain(terrain_category, data=ref)
    min_height = float(ref["constants"]["minimum_velocity_pressure_height_m"])
    z_for_k = max(z, min_height)
    kz = 2.774 * (z_for_k / zg_m) ** (2.0 * alpha)
    q_kgf_m2 = 0.06 * kz * kzt_value * (factor * wind) ** 2
    q_kpa = q_kgf_m2 * float(ref["constants"]["kgf_per_m2_to_kpa"])
    return {
        "height_m": z,
        "height_for_k_m": z_for_k,
        "k": kz,
        "q_kgf_m2": q_kgf_m2,
        "q_kpa": q_kpa,
    }


def _semilog_interpolate(
    area_m2: float,
    *,
    low_area_m2: float,
    high_area_m2: float,
    low_value: float,
    high_value: float,
) -> tuple[float, str]:
    area = float(area_m2)
    if not math.isfinite(area) or area <= 0:
        raise WindPressureInputError("effective_area_m2 must be finite and > 0")
    if area <= low_area_m2:
        return low_value, "LOW_AREA_PLATEAU"
    if area >= high_area_m2:
        return high_value, "HIGH_AREA_PLATEAU"
    ratio = (
        math.log10(area) - math.log10(low_area_m2)
    ) / (
        math.log10(high_area_m2) - math.log10(low_area_m2)
    )
    return low_value + ratio * (high_value - low_value), "SEMILOG_INTERPOLATION"


def _interpolate_family(
    effective_area_m2: float,
    *,
    low_area_m2: float,
    high_area_m2: float,
    conversion_factor: float,
    controls: Mapping[str, Mapping[str, float]],
) -> tuple[dict[str, float], str]:
    values: dict[str, float] = {}
    methods: set[str] = set()
    for key, item in controls.items():
        value, method = _semilog_interpolate(
            effective_area_m2,
            low_area_m2=low_area_m2,
            high_area_m2=high_area_m2,
            low_value=float(item["low"]) * conversion_factor,
            high_value=float(item["high"]) * conversion_factor,
        )
        values[key] = value
        methods.add(method)
    return values, next(iter(methods))


def figure_3_2_wall_gcp(
    effective_area_m2: float,
    *,
    data: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve Figure 3.2 wall Zone 4/5 GCp for h > 18 m."""
    ref = data or load_reference_data()
    fig = ref["figure_3_2_wall"]
    low_area = float(fig["low_area_m2"])
    high_area = float(fig["high_area_m2"])
    conversion = float(fig["conversion_factor_from_asce_7_02_gcp"])
    result, method = _interpolate_family(
        effective_area_m2,
        low_area_m2=low_area,
        high_area_m2=high_area,
        conversion_factor=conversion,
        controls=fig["base_asce_7_02_control_values"],
    )
    return {
        "effective_area_m2": float(effective_area_m2),
        "positive_zone4_zone5": result["positive_zone4_zone5"],
        "zone4_negative": result["zone4_negative"],
        "zone5_negative": result["zone5_negative"],
        "selection_method": method,
        "low_area_m2": low_area,
        "high_area_m2": high_area,
        "conversion_factor": conversion,
        "figure": "3.2",
    }


def low_rise_corner_width(h_m: float, least_horizontal_dimension_m: float) -> float:
    """Figure 3.1 corner/edge width a."""
    h = float(h_m)
    width = float(least_horizontal_dimension_m)
    if not math.isfinite(h) or h <= 0:
        raise WindPressureInputError("h_m must be finite and > 0")
    if not math.isfinite(width) or width <= 0:
        raise WindPressureInputError(
            "least_horizontal_dimension_m must be finite and > 0"
        )
    return max(min(0.40 * h, 0.10 * width), 0.9, 0.04 * width)


def figure_3_1_wall_gcp(
    effective_area_m2: float,
    *,
    apply_low_slope_reduction: bool = False,
    roof_slope_deg: float | None = None,
    data: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve Figure 3.1(a) wall Zone 4/5 GCp for h <= 18 m."""
    ref = data or load_reference_data()
    fig = ref["figure_3_1"]
    wall = fig["wall"]
    conversion = float(fig["coefficient_basis"]["conversion_factor_from_asce_7_02_gcp"])
    result, method = _interpolate_family(
        effective_area_m2,
        low_area_m2=float(wall["low_area_m2"]),
        high_area_m2=float(wall["high_area_m2"]),
        conversion_factor=conversion,
        controls=wall["base_asce_7_02_control_values"],
    )

    reduction_multiplier = 1.0
    if apply_low_slope_reduction:
        if roof_slope_deg is None:
            raise WindPressureInputError(
                "roof_slope_deg is required when low-slope wall reduction is requested"
            )
        slope = float(roof_slope_deg)
        limit = float(wall["low_slope_reduction"]["eligible_when_roof_slope_deg_lte"])
        if not math.isfinite(slope) or slope < 0:
            raise WindPressureInputError("roof_slope_deg must be finite and >= 0")
        if slope > limit:
            raise WindPressureInputError(
                "Figure 3.1(a) 10% wall reduction is only eligible for roof_slope_deg <= 10"
            )
        reduction_multiplier = float(wall["low_slope_reduction"]["multiplier"])
        result = {key: value * reduction_multiplier for key, value in result.items()}

    return {
        "effective_area_m2": float(effective_area_m2),
        "positive_zone4_zone5": result["positive_zone4_zone5"],
        "zone4_negative": result["zone4_negative"],
        "zone5_negative": result["zone5_negative"],
        "selection_method": method,
        "low_area_m2": float(wall["low_area_m2"]),
        "high_area_m2": float(wall["high_area_m2"]),
        "conversion_factor": conversion,
        "figure": wall["figure"],
        "low_slope_reduction_applied": bool(apply_low_slope_reduction),
        "reduction_multiplier": reduction_multiplier,
    }


def _select_roof_branch(slope_deg: float, roof: Mapping[str, Any]) -> Mapping[str, Any]:
    slope = float(slope_deg)
    if not math.isfinite(slope) or slope < 0:
        raise WindPressureInputError("roof_slope_deg must be finite and >= 0")
    for branch in roof["slope_branches"]:
        minimum = branch.get("min_slope_deg")
        maximum = float(branch["max_slope_deg"])
        above_min = True
        if minimum is not None:
            minimum_value = float(minimum)
            above_min = slope > minimum_value if branch.get("min_exclusive") else slope >= minimum_value
        if above_min and slope <= maximum:
            return branch
    raise WindPressureUnsupportedError(
        "Figure 3.1 V2 supports gable/hip roof_slope_deg through 45 degrees only"
    )


def figure_3_1_roof_gcp(
    effective_area_m2: float,
    roof_slope_deg: float,
    *,
    data: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve Figure 3.1(b)-(d) roof Zone 1/2/3 GCp."""
    ref = data or load_reference_data()
    fig = ref["figure_3_1"]
    roof = fig["roof"]
    branch = _select_roof_branch(roof_slope_deg, roof)
    conversion = float(fig["coefficient_basis"]["conversion_factor_from_asce_7_02_gcp"])
    result, method = _interpolate_family(
        effective_area_m2,
        low_area_m2=float(roof["low_area_m2"]),
        high_area_m2=float(roof["high_area_m2"]),
        conversion_factor=conversion,
        controls=branch["base_asce_7_02_control_values"],
    )
    return {
        "effective_area_m2": float(effective_area_m2),
        "roof_slope_deg": float(roof_slope_deg),
        "positive_all_zones": result["positive_all_zones"],
        "zone1_negative": result["zone1_negative"],
        "zone2_negative": result["zone2_negative"],
        "zone3_negative": result["zone3_negative"],
        "selection_method": method,
        "low_area_m2": float(roof["low_area_m2"]),
        "high_area_m2": float(roof["high_area_m2"]),
        "conversion_factor": conversion,
        "figure": branch["figure"],
        "slope_branch": branch["id"],
    }


def _round_half_up(value: float, digits: int) -> float:
    quantum = Decimal(1).scaleb(-digits)
    return float(Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP))


def _pressure_sets(
    pressures: Mapping[str, Mapping[str, float]],
    *,
    kgf_per_m2_to_kpa: float,
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    raw: dict[str, dict[str, float]] = {}
    display: dict[str, dict[str, float]] = {}
    for zone, pair in pressures.items():
        pos = float(pair["positive_kpa"])
        neg = float(pair["negative_kpa"])
        raw[zone] = {
            "positive_kpa": pos,
            "negative_kpa": neg,
            "positive_kgf_m2": pos / kgf_per_m2_to_kpa,
            "negative_kgf_m2": neg / kgf_per_m2_to_kpa,
        }
        display[zone] = {
            "positive_kpa": _round_half_up(pos, 2),
            "negative_kpa": _round_half_up(neg, 2),
            "positive_kgf_m2": _round_half_up(pos / kgf_per_m2_to_kpa, 1),
            "negative_kgf_m2": _round_half_up(neg / kgf_per_m2_to_kpa, 1),
        }
    return raw, display


def _resolve_common(
    *,
    region: str,
    district: str | None,
    building_category: int | str,
    terrain_category: str,
    kzt: float,
    enclosure: str,
    h_m: float,
    governing_wind_source: str,
    data: Mapping[str, Any],
) -> dict[str, Any]:
    if str(governing_wind_source).strip().lower() != "code":
        raise WindPressureUnsupportedError(
            "code-based wind pressure only; wind-tunnel-governed cases are out of scope"
        )
    h = float(h_m)
    if not math.isfinite(h) or h <= 0:
        raise WindPressureInputError("h_m must be finite and > 0")
    enclosure_key = str(enclosure).strip().lower()
    enclosure_data = data["internal_pressure"].get(enclosure_key)
    if not enclosure_data:
        raise WindPressureInputError(
            "enclosure must be enclosed, partially_enclosed, or open"
        )
    if enclosure_key == "open":
        raise WindPressureUnsupportedError(
            "open buildings are not routed through Figure 3.1/3.2 enclosed-building GCp"
        )
    v10 = resolve_basic_wind_speed(region, district, data=data)
    importance = resolve_importance_factor(building_category, data=data)
    qh = velocity_pressure(
        h,
        terrain_category=terrain_category,
        kzt=kzt,
        importance_factor=importance,
        v10_mps=v10,
        data=data,
    )
    alpha, zg_m = resolve_terrain(terrain_category, data=data)
    return {
        "h_m": h,
        "enclosure": enclosure_key,
        "gcpi_magnitude": float(enclosure_data["gcpi_magnitude"]),
        "v10_mps": v10,
        "importance_factor": importance,
        "qh": qh,
        "alpha": alpha,
        "zg_m": zg_m,
    }


def calculate_wall_design_pressure(
    *,
    region: str,
    district: str | None,
    building_category: int | str,
    terrain_category: str,
    kzt: float,
    enclosure: str,
    h_m: float,
    z_m: float | None,
    effective_area_m2: float,
    least_horizontal_dimension_m: float,
    governing_wind_source: str,
    roof_slope_deg: float | None = None,
    apply_low_slope_wall_reduction: bool = False,
    data: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Calculate wall Zone 4/5 design pressures for admitted high- or low-rise route."""
    ref = data or load_reference_data()
    common = _resolve_common(
        region=region,
        district=district,
        building_category=building_category,
        terrain_category=terrain_category,
        kzt=kzt,
        enclosure=enclosure,
        h_m=h_m,
        governing_wind_source=governing_wind_source,
        data=ref,
    )
    h = common["h_m"]
    area = float(effective_area_m2)
    width = float(least_horizontal_dimension_m)
    if not math.isfinite(area) or area <= 0:
        raise WindPressureInputError("effective_area_m2 must be finite and > 0")
    if not math.isfinite(width) or width <= 0:
        raise WindPressureInputError(
            "least_horizontal_dimension_m must be finite and > 0"
        )

    gcpi = common["gcpi_magnitude"]
    qh = common["qh"]
    route: str
    qz: dict[str, float] | None

    if h <= 18.0:
        route = "FIGURE_3_1_A_LOW_RISE_WALL"
        gcp = figure_3_1_wall_gcp(
            area,
            apply_low_slope_reduction=apply_low_slope_wall_reduction,
            roof_slope_deg=roof_slope_deg,
            data=ref,
        )
        q_external_positive = qh
        q_external_negative = qh
        q_internal = qh
        qz = None
        corner_a_m = low_rise_corner_width(h, width)
    else:
        route = "FIGURE_3_2_HIGH_RISE_WALL"
        if apply_low_slope_wall_reduction:
            raise WindPressureUnsupportedError(
                "Figure 3.1(a) low-slope wall reduction is only available for h <= 18 m"
            )
        if z_m is None:
            raise WindPressureInputError("z_m is required for h > 18 m wall pressure")
        z = float(z_m)
        if not math.isfinite(z) or z <= 0 or z > h:
            raise WindPressureInputError("z_m must be finite, > 0, and <= h_m")
        qz = velocity_pressure(
            z,
            terrain_category=terrain_category,
            kzt=kzt,
            importance_factor=common["importance_factor"],
            v10_mps=common["v10_mps"],
            data=ref,
        )
        gcp = figure_3_2_wall_gcp(area, data=ref)
        q_external_positive = qz
        q_external_negative = qh
        q_internal = qh
        corner_a_m = max(0.10 * width, 0.9)

    positive = (
        q_external_positive["q_kpa"] * gcp["positive_zone4_zone5"]
        + q_internal["q_kpa"] * gcpi
    )
    zone4_negative = (
        q_external_negative["q_kpa"] * gcp["zone4_negative"]
        - q_internal["q_kpa"] * gcpi
    )
    zone5_negative = (
        q_external_negative["q_kpa"] * gcp["zone5_negative"]
        - q_internal["q_kpa"] * gcpi
    )
    raw, display = _pressure_sets(
        {
            "zone4": {"positive_kpa": positive, "negative_kpa": zone4_negative},
            "zone5": {"positive_kpa": positive, "negative_kpa": zone5_negative},
        },
        kgf_per_m2_to_kpa=float(ref["constants"]["kgf_per_m2_to_kpa"]),
    )

    return {
        "reference": {
            "dataset_id": ref["dataset_id"],
            "verification_status": ref["verification_status"],
            "verified_at": ref["verified_at"],
            "code_basis": "建築物耐風設計規範及解說 103 年修正版",
            "figure": gcp["figure"],
        },
        "resolved_inputs": {
            "surface": "wall",
            "region": _normalize_admin_name(region),
            "district": _normalize_admin_name(district) if district else None,
            "v10_mps": common["v10_mps"],
            "building_category": str(building_category),
            "importance_factor": common["importance_factor"],
            "terrain_category": str(terrain_category).strip().upper(),
            "alpha": common["alpha"],
            "zg_m": common["zg_m"],
            "kzt": float(kzt),
            "enclosure": common["enclosure"],
            "gcpi_magnitude": gcpi,
            "h_m": h,
            "z_m": float(z_m) if z_m is not None else None,
            "roof_slope_deg": float(roof_slope_deg) if roof_slope_deg is not None else None,
            "apply_low_slope_wall_reduction": bool(apply_low_slope_wall_reduction),
            "effective_area_m2": area,
            "least_horizontal_dimension_m": width,
        },
        "applicability": {
            "status": "SUPPORTED",
            "route": route,
            "governing_wind_source": "code",
            "partially_enclosed_internal_velocity_pressure_basis": "q(h)",
        },
        "velocity_pressure": {"qz": qz, "qh": qh, "qi": q_internal},
        "corner_zone": {
            "a_m": corner_a_m,
            "formula": (
                "max(min(0.40*h, 0.10*B), 0.9 m, 0.04*B)"
                if h <= 18.0
                else "max(0.10*B, 0.9 m)"
            ),
        },
        "coefficients": {
            "gcp": gcp,
            "gcpi_positive": gcpi,
            "gcpi_negative": -gcpi,
        },
        "pressures": raw,
        "display_pressures": display,
        "rounding": {
            "method": "ROUND_HALF_UP",
            "pressure_kpa_digits": 2,
            "pressure_kgf_m2_digits": 1,
            "rule": "raw values remain authoritative; display rounding is applied only after calculation",
        },
    }


def calculate_roof_design_pressure(
    *,
    region: str,
    district: str | None,
    building_category: int | str,
    terrain_category: str,
    kzt: float,
    enclosure: str,
    h_m: float,
    roof_slope_deg: float,
    effective_area_m2: float,
    least_horizontal_dimension_m: float,
    governing_wind_source: str,
    data: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Calculate h <= 18 m roof Zone 1/2/3 design pressures under Figure 3.1."""
    ref = data or load_reference_data()
    common = _resolve_common(
        region=region,
        district=district,
        building_category=building_category,
        terrain_category=terrain_category,
        kzt=kzt,
        enclosure=enclosure,
        h_m=h_m,
        governing_wind_source=governing_wind_source,
        data=ref,
    )
    h = common["h_m"]
    if h > 18.0:
        raise WindPressureUnsupportedError(
            "roof V2 supports Figure 3.1 h <= 18 m only"
        )
    area = float(effective_area_m2)
    width = float(least_horizontal_dimension_m)
    if not math.isfinite(area) or area <= 0:
        raise WindPressureInputError("effective_area_m2 must be finite and > 0")
    if not math.isfinite(width) or width <= 0:
        raise WindPressureInputError(
            "least_horizontal_dimension_m must be finite and > 0"
        )

    gcp = figure_3_1_roof_gcp(area, roof_slope_deg, data=ref)
    qh = common["qh"]
    gcpi = common["gcpi_magnitude"]
    positive = qh["q_kpa"] * gcp["positive_all_zones"] + qh["q_kpa"] * gcpi

    pressures: dict[str, dict[str, float]] = {}
    for zone in ("zone1", "zone2", "zone3"):
        negative_gcp = gcp[f"{zone}_negative"]
        pressures[zone] = {
            "positive_kpa": positive,
            "negative_kpa": qh["q_kpa"] * negative_gcp - qh["q_kpa"] * gcpi,
        }
    raw, display = _pressure_sets(
        pressures,
        kgf_per_m2_to_kpa=float(ref["constants"]["kgf_per_m2_to_kpa"]),
    )
    corner_a_m = low_rise_corner_width(h, width)

    return {
        "reference": {
            "dataset_id": ref["dataset_id"],
            "verification_status": ref["verification_status"],
            "verified_at": ref["verified_at"],
            "code_basis": "建築物耐風設計規範及解說 103 年修正版",
            "figure": gcp["figure"],
        },
        "resolved_inputs": {
            "surface": "roof",
            "region": _normalize_admin_name(region),
            "district": _normalize_admin_name(district) if district else None,
            "v10_mps": common["v10_mps"],
            "building_category": str(building_category),
            "importance_factor": common["importance_factor"],
            "terrain_category": str(terrain_category).strip().upper(),
            "alpha": common["alpha"],
            "zg_m": common["zg_m"],
            "kzt": float(kzt),
            "enclosure": common["enclosure"],
            "gcpi_magnitude": gcpi,
            "h_m": h,
            "roof_slope_deg": float(roof_slope_deg),
            "effective_area_m2": area,
            "least_horizontal_dimension_m": width,
        },
        "applicability": {
            "status": "SUPPORTED",
            "route": "FIGURE_3_1_LOW_RISE_ROOF",
            "slope_branch": gcp["slope_branch"],
            "governing_wind_source": "code",
            "partially_enclosed_internal_velocity_pressure_basis": "q(h)",
        },
        "velocity_pressure": {"qh": qh, "qi": qh},
        "corner_zone": {
            "a_m": corner_a_m,
            "formula": "max(min(0.40*h, 0.10*B), 0.9 m, 0.04*B)",
        },
        "coefficients": {
            "gcp": gcp,
            "gcpi_positive": gcpi,
            "gcpi_negative": -gcpi,
        },
        "pressures": raw,
        "display_pressures": display,
        "rounding": {
            "method": "ROUND_HALF_UP",
            "pressure_kpa_digits": 2,
            "pressure_kgf_m2_digits": 1,
            "rule": "raw values remain authoritative; display rounding is applied only after calculation",
        },
    }
