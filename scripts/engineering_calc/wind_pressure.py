"""Taiwan 103-code wall design-wind-pressure deterministic kernel.

V1 scope:
- wall external components / cladding,
- mean roof height h > 18 m,
- enclosed or partially enclosed buildings,
- Figure 3.2 Zone 4 / Zone 5 wall coefficients,
- SI-facing outputs with the code's kgf/m^2 velocity-pressure basis retained in provenance.

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
    / "taiwan-wind-code-103-v1.json"
)


class WindPressureInputError(ValueError):
    """Required project/code input is missing or invalid."""


class WindPressureUnsupportedError(ValueError):
    """Requested condition is outside the admitted V1 model."""


def load_reference_data(path: Path | None = None) -> dict[str, Any]:
    target = path or DATA_PATH
    with target.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("dataset_id") != "taiwan-wind-code-103-v1":
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


def figure_3_2_wall_gcp(
    effective_area_m2: float,
    *,
    data: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve the Figure 3.2 wall Zone 4/5 GCp family for V1."""
    ref = data or load_reference_data()
    fig = ref["figure_3_2_wall"]
    low_area = float(fig["low_area_m2"])
    high_area = float(fig["high_area_m2"])
    conversion = float(fig["conversion_factor_from_asce_7_02_gcp"])
    base = fig["base_asce_7_02_control_values"]

    result: dict[str, float] = {}
    methods: set[str] = set()
    for key, item in base.items():
        value, method = _semilog_interpolate(
            effective_area_m2,
            low_area_m2=low_area,
            high_area_m2=high_area,
            low_value=float(item["low"]) * conversion,
            high_value=float(item["high"]) * conversion,
        )
        result[key] = value
        methods.add(method)

    return {
        "effective_area_m2": float(effective_area_m2),
        "positive_zone4_zone5": result["positive_zone4_zone5"],
        "zone4_negative": result["zone4_negative"],
        "zone5_negative": result["zone5_negative"],
        "selection_method": next(iter(methods)),
        "low_area_m2": low_area,
        "high_area_m2": high_area,
        "conversion_factor": conversion,
    }


def _round_half_up(value: float, digits: int) -> float:
    quantum = Decimal(1).scaleb(-digits)
    return float(Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_UP))


def calculate_wall_design_pressure(
    *,
    region: str,
    district: str | None,
    building_category: int | str,
    terrain_category: str,
    kzt: float,
    enclosure: str,
    h_m: float,
    z_m: float,
    effective_area_m2: float,
    least_horizontal_dimension_m: float,
    governing_wind_source: str,
    data: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Calculate V1 Zone 4/5 wall design pressures."""
    ref = data or load_reference_data()
    if str(governing_wind_source).strip().lower() != "code":
        raise WindPressureUnsupportedError(
            "V1 supports code-based wind pressure only; wind-tunnel-governed cases are out of scope"
        )

    h = float(h_m)
    z = float(z_m)
    area = float(effective_area_m2)
    width = float(least_horizontal_dimension_m)
    if not math.isfinite(h) or h <= 18.0:
        raise WindPressureUnsupportedError("V1 supports h > 18 m only")
    if not math.isfinite(z) or z <= 0 or z > h:
        raise WindPressureInputError("z_m must be finite, > 0, and <= h_m")
    if not math.isfinite(area) or area <= 0:
        raise WindPressureInputError("effective_area_m2 must be finite and > 0")
    if not math.isfinite(width) or width <= 0:
        raise WindPressureInputError(
            "least_horizontal_dimension_m must be finite and > 0"
        )

    enclosure_key = str(enclosure).strip().lower()
    enclosure_data = ref["internal_pressure"].get(enclosure_key)
    if not enclosure_data:
        raise WindPressureInputError(
            "enclosure must be enclosed, partially_enclosed, or open"
        )
    if not enclosure_data.get("v1_supported"):
        raise WindPressureUnsupportedError(
            "V1 does not route open buildings through Figure 3.2"
        )

    v10 = resolve_basic_wind_speed(region, district, data=ref)
    importance = resolve_importance_factor(building_category, data=ref)
    qz = velocity_pressure(
        z,
        terrain_category=terrain_category,
        kzt=kzt,
        importance_factor=importance,
        v10_mps=v10,
        data=ref,
    )
    qh = velocity_pressure(
        h,
        terrain_category=terrain_category,
        kzt=kzt,
        importance_factor=importance,
        v10_mps=v10,
        data=ref,
    )

    # Section 2.2 permits q(zh0) or q(h) for positive internal pressure in a
    # partially enclosed building. V1 deliberately standardizes on q(h):
    # it is code-permitted, conservative for h >= zh0, deterministic, and
    # avoids inventing an opening height when the user has not supplied one.
    qi = qh
    gcpi_mag = float(enclosure_data["gcpi_magnitude"])
    gcp = figure_3_2_wall_gcp(area, data=ref)
    corner_a_m = max(0.10 * width, 0.9)

    positive = qz["q_kpa"] * gcp["positive_zone4_zone5"] + qi["q_kpa"] * gcpi_mag
    zone4_negative = qh["q_kpa"] * gcp["zone4_negative"] - qi["q_kpa"] * gcpi_mag
    zone5_negative = qh["q_kpa"] * gcp["zone5_negative"] - qi["q_kpa"] * gcpi_mag

    kgf_per_m2_to_kpa = float(ref["constants"]["kgf_per_m2_to_kpa"])
    pressures = {
        "zone4": {
            "positive_kpa": positive,
            "negative_kpa": zone4_negative,
            "positive_kgf_m2": positive / kgf_per_m2_to_kpa,
            "negative_kgf_m2": zone4_negative / kgf_per_m2_to_kpa,
        },
        "zone5": {
            "positive_kpa": positive,
            "negative_kpa": zone5_negative,
            "positive_kgf_m2": positive / kgf_per_m2_to_kpa,
            "negative_kgf_m2": zone5_negative / kgf_per_m2_to_kpa,
        },
    }
    display = {
        zone: {
            "positive_kpa": _round_half_up(values["positive_kpa"], 2),
            "negative_kpa": _round_half_up(values["negative_kpa"], 2),
            "positive_kgf_m2": _round_half_up(values["positive_kgf_m2"], 1),
            "negative_kgf_m2": _round_half_up(values["negative_kgf_m2"], 1),
        }
        for zone, values in pressures.items()
    }

    alpha, zg_m = resolve_terrain(terrain_category, data=ref)
    return {
        "reference": {
            "dataset_id": ref["dataset_id"],
            "verification_status": ref["verification_status"],
            "verified_at": ref["verified_at"],
            "code_basis": "建築物耐風設計規範及解說 103 年修正版",
            "figure": "3.2",
        },
        "resolved_inputs": {
            "region": _normalize_admin_name(region),
            "district": _normalize_admin_name(district) if district else None,
            "v10_mps": v10,
            "building_category": str(building_category),
            "importance_factor": importance,
            "terrain_category": str(terrain_category).strip().upper(),
            "alpha": alpha,
            "zg_m": zg_m,
            "kzt": float(kzt),
            "enclosure": enclosure_key,
            "gcpi_magnitude": gcpi_mag,
            "h_m": h,
            "z_m": z,
            "effective_area_m2": area,
            "least_horizontal_dimension_m": width,
        },
        "applicability": {
            "status": "SUPPORTED",
            "scope": ref["figure_3_2_wall"]["applicability"],
            "governing_wind_source": "code",
            "partially_enclosed_internal_velocity_pressure_basis": "q(h)",
        },
        "velocity_pressure": {
            "qz": qz,
            "qh": qh,
            "qi": qi,
        },
        "corner_zone": {
            "a_m": corner_a_m,
            "formula": "max(0.10 * B, 0.9 m)",
        },
        "coefficients": {
            "gcp": gcp,
            "gcpi_positive": gcpi_mag,
            "gcpi_negative": -gcpi_mag,
        },
        "pressures": pressures,
        "display_pressures": display,
        "rounding": {
            "method": "ROUND_HALF_UP",
            "pressure_kpa_digits": 2,
            "pressure_kgf_m2_digits": 1,
            "rule": "raw values remain authoritative for comparisons; display rounding is applied only after calculation",
        },
    }
