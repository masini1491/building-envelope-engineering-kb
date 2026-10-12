"""Stage 58: synthetic U-fold WEB-only uniform-pressure research.

Reuse the exact Stage 57 S8R shell geometry and ROOT/TIP boundary contract.
No generic load/surface selector, manufacturer material or capacity admission.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

from check_u_fold_cantilever import (
    B, E, L, T, MESHES, SECTIONS, _completed, _dat_vectors,
    beam_reference, build as build_end_loaded,
)

PRESSURE_N_MM2 = 0.0001
WEB_START, WEB_COUNT = SECTIONS[0], SECTIONS[1]
WEB_HALF_NODES = 2 * WEB_COUNT


def pressure_reference() -> dict:
    section = beam_reference()
    iy = section["mid_surface_iy_mm4"]
    line_load = PRESSURE_N_MM2 * B
    nominal_force = line_load * L
    moment = line_load * L ** 2 / 2
    tip = line_load * L ** 4 / (8 * E * iy)
    if not all(math.isfinite(v) and v > 0
               for v in (iy, line_load, nominal_force, moment, tip)):
        raise ValueError("U_PRESSURE_REFERENCE_NONPHYSICAL")
    return {
        "nominal_web_pressure_n_mm2": PRESSURE_N_MM2,
        "nominal_web_loaded_area_mm2": B * L,
        "nominal_total_force_n": nominal_force,
        "nominal_root_moment_demand_n_mm": moment,
        "mid_surface_iy_mm4": iy,
        "cantilever_tip_deflection_mm": tip,
        "reference_type": "EULER_BERNOULLI_UNIFORM_WEB_LOAD_APPROXIMATION",
        "pressure_direction": "POSITIVE_SHELL_NORMAL_ON_HORIZONTAL_WEB",
        "local_buckling": "NOT_MODELED",
        "engineering_acceptance": "NOT_ADMITTED",
    }


def build_pressure(n: int) -> tuple[str, set[int], set[int]]:
    if type(n) is not int or n not in MESHES:
        raise ValueError("U_PRESSURE_MESH_NOT_ADMITTED")
    original, _tip_force, root, tip = build_end_loaded(n)
    m = sum(SECTIONS)
    web_ids = [i * m + j + 1 for i in range(n)
               for j in range(WEB_START, WEB_START + WEB_COUNT)]
    if (len(web_ids) != WEB_COUNT * n or
            len(set(web_ids)) != len(web_ids) or root & tip):
        raise ValueError("U_PRESSURE_WEB_ELEMENT_IDENTITY_FAILED")
    material = "*MATERIAL,NAME=SYNTHETIC_ELASTIC"
    begin = "*CLOAD\n"
    end = "*NODE FILE,OUTPUT=3D"
    if (original.count(material) != 1 or original.count(begin) != 1
            or original.count(end) != 1):
        raise ValueError("U_PRESSURE_BASE_DECK_CONTRACT_CHANGED")
    web_set = ["*ELSET,ELSET=WEB"]
    web_set += [",".join(str(v) for v in web_ids[i:i + 12])
                for i in range(0, len(web_ids), 12)]
    deck = original.replace(material, "\n".join(web_set) + "\n" + material, 1)
    first = deck.index(begin)
    last = deck.index(end, first)
    deck = (deck[:first] + "*DLOAD\n"
            + f"WEB,P,{PRESSURE_N_MM2}\n" + deck[last:])
    deck = deck.replace("synthetic-U-fold-stage57-",
                        "synthetic-U-fold-stage58-web-pressure-", 1)
    if (deck.count("*DLOAD\n") != 1 or "*CLOAD" in deck or
            deck.count("*ELSET,ELSET=WEB") != 1 or
            "*SHELL SECTION,ELSET=FOLD" not in deck):
        raise ValueError("U_PRESSURE_DECK_SCOPE_ESCALATION")
    return deck, root, tip


def generate(folder: Path, n: int) -> None:
    if folder.is_symlink() or folder.exists():
        raise ValueError("U_PRESSURE_WORKSPACE_MUST_BE_NEW")
    deck, _, _ = build_pressure(n)
    folder.mkdir(parents=True)
    (folder / "panel.inp").write_text(deck, encoding="utf-8")


def _web_tip_displacement(deck: str, tip: set[int],
                          u: dict[int, tuple[float, float, float]]) -> float:
    section = deck.split("*NODE\n", 1)
    if len(section) != 2:
        raise ValueError("U_PRESSURE_NODE_SECTION_MISSING")
    block = section[1].split("*ELEMENT,TYPE=S8R", 1)
    if len(block) != 2:
        raise ValueError("U_PRESSURE_ELEMENT_SECTION_MISSING")
    web_nodes = []
    for line in block[0].splitlines():
        nid_s, x_s, y_s, z_s = line.split(",")
        nid = int(nid_s)
        x, y, z = float(x_s), float(y_s), float(z_s)
        if nid in tip and abs(x - L) < 1e-7 and abs(z) < 1e-7:
            web_nodes.append((y, nid))
    web_nodes.sort()
    if len(web_nodes) != WEB_HALF_NODES + 1:
        raise ValueError("U_PRESSURE_TIP_WEB_NODE_COUNT")
    weighted = 0.0
    for j, (y, nid) in enumerate(web_nodes):
        if abs(y - (-B / 2 + B * j / WEB_HALF_NODES)) > 1e-6:
            raise ValueError("U_PRESSURE_WEB_GEOMETRY_DRIFT")
        coefficient = 1 if j in (0, WEB_HALF_NODES) else (4 if j % 2 else 2)
        weighted += coefficient * u[nid][2]
    value = weighted / (3 * WEB_HALF_NODES)
    if not math.isfinite(value) or value <= 0:
        raise ValueError("U_PRESSURE_TIP_DIRECTION_OR_FINITE_INVALID")
    return value


def _case(folder: Path, n: int) -> dict:
    deck, root, tip = build_pressure(n)
    paths = {suffix: folder / f"panel.{suffix}"
             for suffix in ("inp", "dat", "sta", "frd")}
    for suffix, path in paths.items():
        bound = 64_000_000 if suffix == "frd" else 10_000_000
        if (path.is_symlink() or not path.is_file() or
                not 0 < path.stat().st_size <= bound):
            raise ValueError("U_PRESSURE_OUTPUT_MISSING_OR_UNBOUNDED:" + suffix)
    if paths["inp"].read_bytes() != deck.encode("utf-8"):
        raise ValueError("U_PRESSURE_INPUT_IDENTITY_MISMATCH")
    _completed(paths["sta"])
    u = _dat_vectors(paths["dat"], "TIP", "U")
    rf = _dat_vectors(paths["dat"], "ROOT", "RF")
    if set(u) != tip or set(rf) != root:
        raise ValueError("U_PRESSURE_PRINTED_NODE_COVERAGE")
    w = _web_tip_displacement(deck, tip, u)
    root_z = sum(row[2] for row in rf.values())
    force = pressure_reference()["nominal_total_force_n"]
    # RF on a loaded constrained shell edge can include applied pressure.
    # This 10% check is only a diagnostic; not support-force reconstruction.
    if not math.isfinite(root_z) or not (-1.1 * force <= root_z <= -0.9 * force):
        raise ValueError("U_PRESSURE_RAW_ROOT_RF_NOT_PLAUSIBLE:" + repr(root_z))
    return {
        "web_tip_simpson_displacement_mm": w,
        "raw_root_rf_z_n": root_z,
        "raw_rf_as_independent_support_reaction": "NOT_ADMITTED",
        "artifact_sha256": {
            suffix: hashlib.sha256(path.read_bytes()).hexdigest()
            for suffix, path in paths.items()
        },
    }


def assess(observed: dict[int, float]) -> dict:
    if (not isinstance(observed, dict) or set(observed) != set(MESHES) or
            any(type(value) not in (float, int) or
                not math.isfinite(value) or value <= 0
                for value in observed.values())):
        raise ValueError("U_PRESSURE_MESH_OBSERVATION_INVALID")
    ref = pressure_reference()
    analytic = ref["cantilever_tip_deflection_mm"]
    relative = abs(observed[16] - analytic) / analytic
    mesh_difference = abs(observed[16] - observed[8]) / analytic
    if relative > 0.25:
        raise ValueError("U_PRESSURE_BEAM_REFERENCE_DISAGREEMENT:" + repr(observed))
    if mesh_difference > 0.15:
        raise ValueError("U_PRESSURE_TWO_MESH_CHANGE_EXCESSIVE:" + repr(observed))
    if max(observed.values()) >= 0.05 * T:
        raise ValueError("U_PRESSURE_SMALL_DEFLECTION_SCOPE_EXCEEDED")
    return {
        **ref,
        "observed_web_tip_by_mesh_mm": observed,
        "fine_mesh_reference_relative_difference": relative,
        "two_mesh_relative_change": mesh_difference,
        "bounded_screening_limits": {"relative_beam": 0.25, "relative_mesh": 0.15},
        "mesh_convergence_order": "NOT_ESTABLISHED",
        "nonlinear_follower_pressure_full_balance": "NOT_ADMITTED",
        "material_capacity": "NOT_ADMITTED",
        "attachment_contact": "NOT_MODELED",
    }


def check(root: Path) -> dict:
    cases = {n: _case(root / f"u_fold_pressure_{n}", n) for n in MESHES}
    result = assess({n: case["web_tip_simpson_displacement_mm"]
                     for n, case in cases.items()})
    result["cases"] = cases
    return result


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--generate":
        generate(Path(sys.argv[2]), int(sys.argv[3]))
        print("SYNTHETIC_WEB_PRESSURE_GENERATED_NO_SOLVER")
    elif len(sys.argv) == 2:
        print(json.dumps(check(Path(sys.argv[1])), sort_keys=True,
                         allow_nan=False))
        print("U_FOLD_WEB_PRESSURE_BEAM_SCREENING_PASS; NO_DESIGN_ADMISSION")
    else:
        raise SystemExit("USAGE: check_u_fold_web_pressure.py ROOT | --generate DIR MESH")
