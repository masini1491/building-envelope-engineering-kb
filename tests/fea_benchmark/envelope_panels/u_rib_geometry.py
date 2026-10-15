"""Bounded geometric preflight for a stud-fastened, panel-back U stiffener.

Geometry ONLY. No CalculiX deck, load transfer, stud capacity, material
allowables, contact/friction, buckling or design approval is calculated.
The U is an OPEN sharp-corner cross-section with nominal outside dimensions.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

SCOPE = "OPEN_U_NOMINAL_SHARP_CORNER_GEOMETRY_ONLY"
DEFAULTS = {
    "section_width_mm": 50.0,
    "section_height_mm": 50.0,
    "rib_thickness_mm": 3.0,
    "panel_thickness_mm": 3.0,
    "stud_pitch_mm": 300.0,
}
_REQUIRED = set(DEFAULTS)
_OPTIONAL = {"rib_length_mm", "first_stud_offset_mm"}
# Input sanitation bounds only. They are NOT design-approved ranges.
_BOUNDS = {
    "section_width_mm": (12.0, 300.0),
    "section_height_mm": (12.0, 300.0),
    "rib_thickness_mm": (0.5, 12.0),
    "panel_thickness_mm": (0.5, 12.0),
    "stud_pitch_mm": (30.0, 2000.0),
    "rib_length_mm": (50.0, 12000.0),
}


def _number(value: object, key: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("U_RIB_NONFINITE_OR_NONNUMERIC:" + key)
    return float(value)


def _polygon(section_width: float, section_height: float, thickness: float) -> list[list[float]]:
    half = section_width / 2
    return [
        [-half, 0.0], [half, 0.0], [half, section_height],
        [half - thickness, section_height], [half - thickness, thickness],
        [-half + thickness, thickness], [-half + thickness, section_height],
        [-half, section_height],
    ]


def _polygon_properties(poly: list[list[float]]) -> tuple[float, float, float, float, float]:
    # Independent shoelace / area-integral check of rectangle decomposition.
    a2 = cx_num = cz_num = ix12 = iz12 = 0.0
    for i, (x, z) in enumerate(poly):
        xn, zn = poly[(i+1) % len(poly)]
        cross = x*zn - xn*z
        a2 += cross
        cx_num += (x+xn)*cross
        cz_num += (z+zn)*cross
        ix12 += (z*z + z*zn + zn*zn)*cross
        iz12 += (x*x + x*xn + xn*xn)*cross
    if a2 <= 0:
        raise ValueError("U_RIB_POLYGON_ORIENTATION_INVALID")
    area = a2 / 2
    cx = cx_num / (3*a2)
    cz = cz_num / (3*a2)
    return area, cx, cz, ix12/12-area*cz**2, iz12/12-area*cx**2


def analyze(value: dict) -> dict:
    if not isinstance(value, dict) or not _REQUIRED.issubset(value) or set(value)-(_REQUIRED | _OPTIONAL):
        raise ValueError("U_RIB_INPUT_SCHEMA_MISMATCH")
    if ("rib_length_mm" in value) != ("first_stud_offset_mm" in value):
        raise ValueError("U_RIB_STUD_LAYOUT_REQUIRES_LENGTH_AND_FIRST_OFFSET")
    p = {key:_number(value[key],key) for key in _REQUIRED}
    if "rib_length_mm" in value:
        p["rib_length_mm"] = _number(value["rib_length_mm"], "rib_length_mm")
        p["first_stud_offset_mm"] = _number(value["first_stud_offset_mm"], "first_stud_offset_mm")
    for key,(low,high) in _BOUNDS.items():
        if key in p and not low <= p[key] <= high:
            raise ValueError("U_RIB_INPUT_OUTSIDE_SOFTWARE_BOUNDS:"+key)
    b,h,t = p["section_width_mm"],p["section_height_mm"],p["rib_thickness_mm"]
    if b <= 2*t or h <= t:
        raise ValueError("U_RIB_DEGENERATE_OPEN_SECTION")

    # Non-overlapping rectangles: base b*t, plus two side webs t*(h-t).
    abase=b*t
    aside=t*(h-t)
    area=abase+2*aside
    base_z=t/2
    side_z=(h+t)/2
    centroid_z=(abase*base_z+2*aside*side_z)/area
    ix=(b*t**3/12+abase*(base_z-centroid_z)**2+
        2*((t*(h-t)**3)/12+aside*(side_z-centroid_z)**2))
    iz=(t*b**3/12+2*((h-t)*t**3/12+aside*((b-t)/2)**2))
    poly=_polygon(b,h,t)
    ap,xp,zp,ixp,izp=_polygon_properties(poly)
    for actual,ref in ((area,ap),(0.0,xp),(centroid_z,zp),(ix,ixp),(iz,izp)):
        if not math.isclose(actual,ref,rel_tol=1e-10,abs_tol=1e-9):
            raise ValueError("U_RIB_SECTION_INDEPENDENT_GEOMETRY_MISMATCH")

    layout = {"status":"FIRST_STUD_OFFSET_AND_LENGTH_REQUIRED",
              "stud_centerline_x_mm":0.0,
              "pitch_mm":p["stud_pitch_mm"],
              "positions_mm":[],
              "connection_stiffness":"NOT_MODELED"}
    if "rib_length_mm" in p:
        length=p["rib_length_mm"]
        offset=p["first_stud_offset_mm"]
        if offset < 0 or offset >= length:
            raise ValueError("U_RIB_FIRST_STUD_OUTSIDE_MEMBER")
        count = int(math.floor((length-offset)/p["stud_pitch_mm"])) + 1
        # Reject an end-stud exactly at the terminal boundary; the end spacing
        # is input-specific and may be zero; it is never design-checked here.
        positions=[]
        for i in range(count):
            y=offset+i*p["stud_pitch_mm"]
            if y >= length-1e-9:
                break
            positions.append({"x_mm":0.0,"y_mm":y,"z_mm":0.0})
        if not positions:
            raise ValueError("U_RIB_STUDS_ABSENT")
        layout={"status":"EXPLICIT_CENTERLINE_STUD_COORDINATES_ONLY",
                "stud_centerline_x_mm":0.0,"pitch_mm":p["stud_pitch_mm"],
                "positions_mm":positions,
                "first_edge_distance_mm":offset,
                "last_edge_distance_mm":length-positions[-1]["y_mm"],
                "connection_stiffness":"NOT_MODELED"}

    return {
        "scope":SCOPE,
        "inputs_mm":p,
        "profile_polygon_xz_mm":poly,
        "cross_section":{"area_mm2":area,"centroid_x_mm":0.0,
                         "centroid_z_from_panel_back_mm":centroid_z,
                         "second_moment_about_centroid_x_mm4":ix,
                         "second_moment_about_centroid_z_mm4":iz,
                         "reference":"SHARP_CORNER_OPEN_U_RECTANGLES_AND_INDEPENDENT_POLYGON_INTEGRALS"},
        "stud_layout":layout,
        "geometry_conventions":{
            "width_height":"OUTSIDE_NOMINAL_DIMENSIONS",
            "section":"OPEN_U_BASE_AGAINST_PANEL_BACK_OPENING_AWAY_FROM_PANEL",
            "studs":"ONE_CENTERED_ROW; MARKERS_ONLY; STUD DIAMETER_AND_HOLES_UNSPECIFIED",
            "stud_coordinates":"x_across_U; y_along_rib; z_from_panel_back_contact_plane",
            "fold_radius":"NOT_MODELED",
            "rib_to_panel_contact":"NOT_MODELED",
        },
        "solver_execution":"NOT_RUN",
        "fastener_loads":"NOT_COMPUTED",
        "design_stress_and_buckling":"NOT_COMPUTED",
        "material_capacity":"NOT_ADMITTED",
        "engineering_acceptance":"NOT_ADMITTED",
        "software_bounds_are_engineering_limits":False,
    }


def _unique(pairs):
    values={}
    for k,v in pairs:
        if k in values:
            raise ValueError("U_RIB_DUPLICATE_INPUT_KEY")
        values[k]=v
    return values


def _reject_constant(value):
    raise ValueError("U_RIB_NONFINITE_JSON_CONSTANT")


def load(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 4096:
        raise ValueError("U_RIB_INPUT_NOT_BOUNDED_REGULAR_FILE")
    return analyze(json.loads(path.read_text(encoding="utf-8"),
                              object_pairs_hook=_unique,parse_constant=_reject_constant))


def main() -> int:
    parser=argparse.ArgumentParser(description="U-stiffener geometry only; no CalculiX or capacity")
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--defaults",action="store_true",help="Common nominal 50x50x3, no stud positions")
    group.add_argument("--input",type=Path,help="Explicit JSON; length and first stud offset required for positions")
    args=parser.parse_args()
    try:
        data=analyze(DEFAULTS) if args.defaults else load(args.input)
    except (OSError,ValueError,TypeError) as exc:
        parser.exit(2,"U_RIB_GEOMETRY_REJECTED:"+str(exc)+"\n")
    print(json.dumps(data,sort_keys=True,allow_nan=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
