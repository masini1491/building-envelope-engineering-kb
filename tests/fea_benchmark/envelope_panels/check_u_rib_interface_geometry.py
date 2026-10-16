"""Read-only geometric interface audit for exact synthetic S8R plate / open U rib.

This checks oriented midsurface topology and shell thickness offsets, NOT actual
CalculiX SPOS/SNEG contact behavior, real stud forces, or design acceptance.
"""
from __future__ import annotations

import json
import math
from copy import deepcopy
from check_u_rib_shell_links import (
    E, LENGTH, MESHES, PANEL_WIDTH, PLATE_CROSS,
    _configuration, mesh,
)

SCOPE = "SYNTHETIC_OPEN_U_S8R_INTERFACE_GEOMETRY_ONLY"


def _fail(reason: str) -> None:
    raise ValueError("U_INTERFACE_GEOMETRY_" + reason)


def _face(ids: tuple[int, ...], coords: dict) -> tuple[float, float, float]:
    if len(ids) != 8 or len(set(ids)) != 8 or any(k not in coords for k in ids):
        _fail("INVALID_S8R_CONNECTIVITY")
    a, b, _, d = (coords[k] for k in ids[:4])
    u = [b[j] - a[j] for j in range(3)]
    v = [d[j] - a[j] for j in range(3)]
    n = (u[1]*v[2] - u[2]*v[1],
         u[2]*v[0] - u[0]*v[2],
         u[0]*v[1] - u[1]*v[0])
    area = math.sqrt(sum(q*q for q in n))
    if not math.isfinite(area) or area <= 0:
        _fail("DEGENERATE_OR_NONFINITE_FACE")
    normal = tuple(q/area for q in n)
    return (*normal, area)


def _inspect(n: int, topo: dict) -> dict:
    if type(n) is not int or n not in MESHES:
        _fail("UNSUPPORTED_MESH")
    expected = {"coords", "plate", "rib", "clamped_plate", "clamped_rib_end",
                "center", "panel_studs", "rib_studs"}
    if not isinstance(topo, dict) or set(topo) != expected:
        _fail("TOPOLOGY_SCHEMA")
    conf = _configuration()
    p_t = conf["inputs"]["panel_thickness_mm"]
    r_t = conf["inputs"]["rib_thickness_mm"]
    b = conf["section"]["outer_base_width_mm"]
    coords = topo["coords"]
    if (len(topo["plate"]) != n*PLATE_CROSS or len(topo["rib"]) != n*4
            or len(coords) == 0 or
            not all(len(x) == 3 and all(type(v) in (float, int) and math.isfinite(v)
                                      for v in x) for x in coords.values())):
        _fail("INVALID_COORDINATES_OR_COUNTS")
    # Original deck intentionally keeps plate/rib nodes independent.
    if (set(topo["panel_studs"]) & set(topo["rib_studs"]) or
            len(topo["panel_studs"]) != 4 or len(topo["rib_studs"]) != 4):
        _fail("STUD_NODE_IDENTITY")
    tol = 1e-7
    for e in topo["plate"]:
        nx, ny, nz, area = _face(e, coords)
        if abs(nx)>tol or abs(ny)>tol or abs(nz-1)>tol:
            _fail("PLATE_NORMAL_NOT_POSITIVE_Z")
        if any(abs(coords[k][2])>tol for k in e):
            _fail("PLATE_MIDSURFACE_NOT_ZERO")
    bottom = []
    for i in range(n):
        for j in (1, 2):
            elem = topo["rib"][4*i+j]
            nx, ny, nz, area = _face(elem, coords)
            if abs(nx)>tol or abs(ny)>tol or abs(nz-1)>tol:
                _fail("RIB_BASE_NORMAL_NOT_POSITIVE_Z")
            if any(abs(coords[k][2]-(p_t+r_t)/2)>tol for k in elem):
                _fail("RIB_BASE_MIDSURFACE_OFFSET")
            bottom.append((elem, area))
    band = sorted(set(coords[k][1] for elem,_ in bottom for k in elem))
    expected_band = [-(b-r_t)/2, -(b-r_t)/4, 0., (b-r_t)/4, (b-r_t)/2]
    if len(band) != 5 or any(abs(x-y)>tol for x,y in zip(band,expected_band)):
        _fail("RIB_BASE_WIDTH_OR_CENTER")
    plate_edges = sorted(set(coords[k][1] for e in topo["plate"] for k in e[:4]))
    expected_edges = [PANEL_WIDTH*(i/PLATE_CROSS-0.5) for i in range(PLATE_CROSS+1)]
    if len(plate_edges) != len(expected_edges) or any(
            abs(x-y)>tol for x,y in zip(plate_edges,expected_edges)):
        _fail("PLATE_TRANSVERSE_GRID")
    if any(any(abs(r-p)<tol for p in plate_edges) for r in (band[0],band[-1])):
        _fail("EXPECTED_NONCONFORMING_GRID_CHANGED")
    midplane_gap = (p_t+r_t)/2
    face_gap = midplane_gap-r_t/2-p_t/2
    if abs(face_gap)>tol or abs(sum(area for _,area in bottom)-(b-r_t)*LENGTH)>tol:
        _fail("FACE_OFFSET_OR_PROJECTED_AREA")
    stations = conf["stud_centers"]["positions_along_length_mm"]
    if len(stations)!=4:
        _fail("STUD_STATIONS")
    for a, r, x in zip(topo["panel_studs"],topo["rib_studs"],stations):
        if a not in coords or r not in coords:
            _fail("MISSING_STUD_NODE")
        if (abs(coords[a][0]-x)>tol or abs(coords[r][0]-x)>tol or
            abs(coords[a][1])>tol or abs(coords[r][1])>tol or
            abs(coords[a][2])>tol or abs(coords[r][2]-midplane_gap)>tol):
            _fail("STUD_POSITION_OR_OFFSET")
    return {
        "scope": SCOPE, "mesh": n, "units": "mm",
        "geometry_only": True, "plate_midsurface_z_mm": 0.,
        "plate_positive_normal_face_z_mm": p_t/2,
        "rib_base_midsurface_z_mm": midplane_gap,
        "rib_base_negative_normal_face_z_mm": midplane_gap-r_t/2,
        "geometric_interface_gap_mm": face_gap,
        "oriented_plate_normal": [0.,0.,1.],
        "oriented_rib_base_normal": [0.,0.,1.],
        "rib_base_s8r_midsurface_strip_width_mm": b-r_t,
        "u_nominal_outer_width_mm": b,
        "projected_base_strip_area_mm2": (b-r_t)*LENGTH,
        "bottom_rib_s8r_element_count": len(bottom),
        "plate_transverse_edges_mm": plate_edges,
        "rib_base_transverse_edges_mm": band,
        "transverse_contact_mesh": "NONCONFORMING",
        "contact_keyword_and_pressure_transfer": "NOT_VALIDATED",
        "real_stud_and_attachment": "NOT_ADMITTED",
        "engineering_acceptance": "NOT_ADMITTED",
    }


def audit(n: int) -> dict:
    if type(n) is not int or n not in MESHES:
        _fail("UNSUPPORTED_MESH")
    return _inspect(n, mesh(n))


if __name__ == "__main__":
    observations = {str(n): audit(n) for n in MESHES}
    assert observations["8"]["transverse_contact_mesh"] == "NONCONFORMING"
    print(json.dumps({"scope":SCOPE,"cases":observations,
                      "engineering_acceptance":"NOT_ADMITTED"}, sort_keys=True))
    print("U_RIB_INTERFACE_GEOMETRY_ORIENTATION_SCREEN_PASS; CONTACT_NOT_ADMITTED")
