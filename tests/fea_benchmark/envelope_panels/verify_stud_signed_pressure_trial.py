"""Fail-closed signed-pressure C3D20R four-link research-only checker.

Requires real solver .inp/.dat/.sta/.frd for 2 meshes x 3 cases x 2 signs.
The rib-end fixed SPC RF is a separate observation from spring k*(Up-Ur).
Consistent P1 loads on constrained quadratic-face nodes must be subtracted
before evaluating the nominal +/−36 N global Z balance.
"""
import argparse
import json
import math
from pathlib import Path

from stud_signed_pressure_trial import CASES, DIRECTIONS, MESHES, STATIONS, deck
from verify_stud_solid_trial import field, sets
from verify_c3d20r_u_contact import status
from check_u_rib_contact_observations import rf
from verify_pressure_contact_trial import nominal_pressure_equivalents
from pressure_contact_trial import APPLIED_TOTAL_Z_N

ABS_TOL_N = 0.002
SIGN_TOL_N = 1e-7


def stop(reason):
    raise ValueError("STUD_SIGNED_CHECK_" + reason)


def check_observations(n, case, direction, groups, plate, rib, center, plate_rf, rib_rf):
    if n not in MESHES or case not in CASES or direction not in DIRECTIONS:
        stop("SCOPE")
    if len(groups["STUD_PLATE"]) != len(groups["STUD_RIB"]) or len(groups["STUD_PLATE"]) != 4:
        stop("STATION_COVERAGE")
    if not all(set(nodes) == set(observed) for nodes, observed in (
            (groups["STUD_PLATE"], plate), (groups["STUD_RIB"], rib),
            (groups["CENTER_RF"], center))):
        stop("DISPLACEMENT_NODE_COVERAGE")
    scalar_sign = DIRECTIONS[direction]
    k = CASES[case]
    transfers = [k * (plate[p][2] - rib[q][2]) for p, q in
                 zip(groups["STUD_PLATE"], groups["STUD_RIB"])]
    if not all(math.isfinite(v) for v in transfers):
        stop("NONFINITE_STATION")
    if k == 0:
        if any(x != 0 for x in transfers) or abs(rib_rf) > ABS_TOL_N:
            stop("UNLINKED_TRANSFER")
    else:
        if any(scalar_sign * value <= SIGN_TOL_N for value in transfers):
            stop("SIGNED_TRANSFER_DIRECTION")
        if (abs(transfers[0] - transfers[3]) > ABS_TOL_N or
                abs(transfers[1] - transfers[2]) > ABS_TOL_N):
            stop("STATION_SYMMETRY")
    sum_transfer = math.fsum(transfers)
    rib_residual = math.fsum([sum_transfer, rib_rf])
    if abs(rib_residual) > ABS_TOL_N:
        stop("RIB_ACTION_REACTION")
    pressure = nominal_pressure_equivalents(n)
    support = math.fsum([plate_rf, rib_rf, -scalar_sign * pressure["edge_pressure_n"]])
    global_residual = math.fsum([support, scalar_sign * APPLIED_TOTAL_Z_N])
    if abs(global_residual) > ABS_TOL_N:
        stop("GLOBAL_Z_BALANCE")
    mean_u3 = math.fsum(v[2] for v in center.values()) / len(center)
    if not math.isfinite(mean_u3) or scalar_sign * mean_u3 <= 0:
        stop("CENTER_DIRECTION")
    return {
        "mesh": n, "case": case, "direction": direction,
        "synthetic_k_per_link_n_per_mm": k,
        "signed_derived_link_forces_z_n": transfers,
        "signed_sum_link_forces_z_n": sum_transfer,
        "fixed_rib_observed_rf3_n": rib_rf,
        "fixed_plate_edge_observed_rf3_n": plate_rf,
        "rib_action_reaction_residual_n": rib_residual,
        "corrected_global_z_residual_n": global_residual,
        "center_mean_u3_mm": mean_u3,
    }


def verify(root):
    root = Path(root)
    records = []
    for n in MESHES:
        for case in CASES:
            for direction in DIRECTIONS:
                folder = root / f"signed_{n}_{case}_{direction}"
                paths = {suffix: folder / f"panel.{suffix}" for suffix in ("inp", "dat", "sta", "frd")}
                if any(f.is_symlink() or not f.is_file() or f.stat().st_size <= 0 for f in paths.values()):
                    stop("MISSING_SOLVER_EVIDENCE")
                expected = deck(n, case, direction)
                if paths["inp"].read_text(encoding="utf-8") != expected:
                    stop("INPUT_PROVENANCE")
                status(paths["sta"].read_text(encoding="utf-8", errors="replace"))
                groups = sets(expected)
                text = paths["dat"].read_text(encoding="utf-8", errors="replace")
                plate = field(text, "STUD_PLATE", groups["STUD_PLATE"])
                rib = field(text, "STUD_RIB", groups["STUD_RIB"])
                center = field(text, "CENTER_RF", groups["CENTER_RF"])
                fixed_plate = rf(text, "PLATE_EDGE_RF", expected_nodes=groups["PLATE_EDGE_RF"])["sum_rf3_n"]
                fixed_rib = rf(text, "RIB_END_RF", expected_nodes=groups["RIB_END_RF"])["sum_rf3_n"]
                if not paths["frd"].stat().st_size:
                    stop("FRD_EMPTY")
                records.append(check_observations(n, case, direction, groups, plate, rib, center,
                                                  fixed_plate, fixed_rib))
    for n in MESHES:
        for case in CASES:
            matched = {x["direction"]: x for x in records if x["mesh"] == n and x["case"] == case}
            a, b = matched["positive"], matched["negative"]
            if a["signed_sum_link_forces_z_n"] * b["signed_sum_link_forces_z_n"] > 0:
                stop("SIGN_REVERSAL")
            if a["center_mean_u3_mm"] * b["center_mean_u3_mm"] >= 0:
                stop("CENTER_REVERSAL")
    return {
        "scope": "SYNTHETIC_C3D20R_SIGNED_FOUR_LINK_Z_ONLY_NOT_DESIGN",
        "case_count": len(records), "cases": records,
        "nominal_pressure_each_direction_n": APPLIED_TOTAL_Z_N,
        "constrained_face_load_correction": "SIGNED_QUADRATIC_P1_NODAL_EQUIVALENTS",
        "real_stud_tension_or_compression": "NOT_ESTABLISHED",
        "physical_stud_shear_and_weld": "NOT_MODELED",
        "spring_stiffness_calibration": "NOT_ESTABLISHED",
        "contact_separation": "NOT_MODELED",
        "engineering_acceptance": "NOT_ADMITTED",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.root), indent=2, sort_keys=True, allow_nan=False))
