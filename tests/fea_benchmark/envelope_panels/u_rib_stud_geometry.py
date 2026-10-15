"""Geometry-only research input for a rear-mounted U aluminum stiffener.

An eight-vertex, sharp-corner U cross section has its bottom external face
at normal z=0, against the back of the nominal aluminum panel. Its open side
points toward +z. One central line of *nominal positions* represents studs.
No bend radius, hole/weld details, material properties, contact, FEA, load,
or fastener/section capacity are computed or admitted.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

FIELDS = frozenset({
    "units", "panel_thickness_mm", "rib_base_width_mm", "rib_height_mm",
    "rib_thickness_mm", "rib_length_mm", "stud_pitch_mm",
    "first_stud_edge_offset_mm", "last_stud_min_edge_offset_mm",
    "stud_layout",
})
SCOPE = "SHARP_CORNER_U_STIFFENER_SINGLE_CENTER_STUD_ROW_GEOMETRY_ONLY"
LIMITATIONS = (
    "SHARP_CORNERS_ONLY_NO_BEND_RADIUS_OR_TOLERANCES",
    "NO_STUD_DIAMETER_WELD_HOLE_OR_CONNECTION_STIFFNESS",
    "NO_CONTACT_SLIP_FEA_STRESS_OR_FASTENER_DEMAND",
    "NO_LOCAL_BUCKLING_OR_SECTION_CAPACITY",
    "NO_PANEL_RESTRAINT_OR_STRUCTURAL_ADMISSION",
)


def _number(value: object, key: str, low: float, high: float) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("U_RIB_INVALID_NUMBER:" + key)
    v = float(value)
    if not low <= v <= high:
        raise ValueError("U_RIB_OUTSIDE_INPUT_SANITY_BOUNDS:" + key)
    return v


def geometry(input_data: dict) -> dict:
    if not isinstance(input_data, dict) or set(input_data) != FIELDS:
        raise ValueError("U_RIB_INPUT_SCHEMA_MISMATCH")
    if input_data["units"] != "mm" or input_data["stud_layout"] != "single_center_row":
        raise ValueError("U_RIB_UNSUPPORTED_UNITS_OR_STUD_LAYOUT")
    b = _number(input_data["rib_base_width_mm"], "rib_base_width_mm", 10., 500.)
    h = _number(input_data["rib_height_mm"], "rib_height_mm", 10., 250.)
    t = _number(input_data["rib_thickness_mm"], "rib_thickness_mm", .5, 15.)
    panel = _number(input_data["panel_thickness_mm"], "panel_thickness_mm", .5, 15.)
    length = _number(input_data["rib_length_mm"], "rib_length_mm", 300., 12000.)
    pitch = _number(input_data["stud_pitch_mm"], "stud_pitch_mm", 50., 1000.)
    first = _number(input_data["first_stud_edge_offset_mm"], "first_stud_edge_offset_mm", 0., 1000.)
    last_min = _number(input_data["last_stud_min_edge_offset_mm"], "last_stud_min_edge_offset_mm", 0., 1000.)
    if b <= 2*t or h <= t:
        raise ValueError("U_RIB_DEGENERATE_OPEN_SECTION")
    if first + last_min > length:
        raise ValueError("U_RIB_NO_VALID_STUD_WINDOW")
    count = math.floor((length - last_min - first) / pitch + 1e-10) + 1
    if not 1 <= count <= 200:
        raise ValueError("U_RIB_STUD_COUNT_OUTSIDE_RESEARCH_BOUNDS")
    xs = [first + i*pitch for i in range(count)]
    if xs[-1] > length - last_min + 1e-8:
        raise ValueError("U_RIB_LAST_STUD_END_CLEARANCE_FAILED")
    # Three disjoint rectangles: bottom [0,t], left/right walls [t,h].
    base_area = b*t
    wall_area = t*(h-t)
    area = base_area + 2*wall_area
    base_cz = t/2
    wall_cz = (h+t)/2
    cz = (base_area*base_cz + 2*wall_area*wall_cz)/area
    inertia_transverse = (
        b*t**3/12 + base_area*(base_cz-cz)**2
        + 2*(t*(h-t)**3/12 + wall_area*(wall_cz-cz)**2)
    )
    inertia_normal = (
        t*b**3/12
        + 2*((h-t)*t**3/12 + wall_area*(b/2-t/2)**2)
    )
    polygon = [
        (-b/2, 0), (b/2, 0), (b/2, h), (b/2-t, h),
        (b/2-t, t), (-b/2+t, t), (-b/2+t, h), (-b/2, h),
    ]
    return {
        "scope": SCOPE,
        "inputs": {key: input_data[key] for key in sorted(FIELDS)},
        "section": {
            "profile": "OPEN_U_SHARP_CORNER_RECTANGLE_UNION",
            "outer_base_width_mm": b,
            "outer_height_from_panel_interface_mm": h,
            "geometric_area_mm2": area,
            "centroid_transverse_from_midline_mm": 0.,
            "centroid_normal_from_panel_interface_mm": cz,
            "geometric_I_about_transverse_centroid_mm4": inertia_transverse,
            "geometric_I_about_normal_centroid_mm4": inertia_normal,
            "nominal_extruded_section_volume_mm3": area*length,
            "cross_section_outline_transverse_normal_mm": polygon,
        },
        "stud_centers": {
            "coordinate_reference": "ALONG_RIB_FROM_FIRST_END; TRANSVERSE_U_BASE_MIDLINE",
            "number_of_rows": 1,
            "row_transverse_from_midline_mm": 0.,
            "positions_along_length_mm": xs,
            "count": count,
            "actual_last_stud_edge_distance_mm": length-xs[-1],
            "nominal_pitch_mm": pitch,
            "physical_stud_diameter_and_weld": "NOT_SPECIFIED_NOT_MODELED",
        },
        "panel_rib_interface": "U_BOTTOM_EXTERNAL_FACE_CONTACT_SIDE_ONLY_GEOMETRY",
        "finite_element_deck": "NOT_GENERATED",
        "connection_transfer": "NOT_ESTABLISHED",
        "engineering_acceptance": "NOT_ADMITTED",
        "research_exclusions": list(LIMITATIONS),
    }


def load(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 4096:
        raise ValueError("U_RIB_INPUT_FILE_NOT_BOUNDED")
    def unique(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ValueError("U_RIB_DUPLICATE_INPUT_KEY")
            result[k] = v
        return result
    def nonfinite(value):
        raise ValueError("U_RIB_NONFINITE_JSON_VALUE:" + value)
    return geometry(json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique,
                               parse_constant=nonfinite))


def main() -> int:
    parser = argparse.ArgumentParser(description="Geometry-only U stiffener / nominal studs (no FEA)")
    parser.add_argument("--input", required=True, type=Path)
    options = parser.parse_args()
    try:
        result = load(options.input)
    except (OSError, ValueError, TypeError) as exc:
        parser.error("U_RIB_GEOMETRY_REJECTED: " + str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
