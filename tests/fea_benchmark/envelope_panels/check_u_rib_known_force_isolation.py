"""Isolate open-U S8R raw support reactions under a known, applied Z force.

Two equal forces on distinct mid-base nodes, no contact or stud connection.
Plate center drive is retained but independent. Pure synthetic observation.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

from check_u_rib_base_contact import DRIVE_MM, MESHES, deck as unlinked_deck, selected_faces
from check_s8r_normal_contact import rf

CASES = ("up", "down")
FORCE_N = 1.0
SCOPE = "SYNTHETIC_U_RIB_S8R_KNOWN_EXTERNAL_FORCE_NO_CONTACT"
# Existing synthetic contact check uses a 0.0002 N absolute balance floor.
# Only this no-contact, known-external-load control is admitted to this test.
NONCONTACT_RIB_BALANCE_TOL_N = 0.0002


def reject(label):
    raise ValueError("U_RIB_KNOWN_FORCE_" + label)


def noncontact_known_force_residual(rib_reaction_n, applied_force_n):
    if not (math.isfinite(rib_reaction_n) and math.isfinite(applied_force_n)):
        reject("NONFINITE_KNOWN_FORCE")
    if abs(applied_force_n) != FORCE_N:
        reject("KNOWN_FORCE_SCOPE")
    residual = math.fsum((rib_reaction_n, applied_force_n))
    if abs(residual) > NONCONTACT_RIB_BALANCE_TOL_N:
        reject("NONCONTACT_RIB_BALANCE")
    return residual


def load_nodes(n):
    topo, _, _ = selected_faces(n)
    nodes = tuple(topo["rib_studs"][1:3])
    if (len(nodes) != 2 or len(set(nodes)) != 2 or
        set(nodes) & set(topo["clamped_rib_end"]) or
        set(nodes) & set(topo["clamped_plate"])):
        reject("NODE_ADMISSION")
    x0, x1 = (topo["coords"][node][0] for node in nodes)
    if abs(x0 + x1 - 1200.0) > 1e-8 or abs(x1 - x0 - 300.0) > 1e-8:
        reject("FORCE_STATION_GEOMETRY")
    return topo, nodes


def deck(n, case):
    if type(n) is not int or n not in MESHES or case not in CASES:
        reject("OUTSIDE_SCOPE")
    _, nodes = load_nodes(n)
    original = unlinked_deck(n, "unlinked")
    target = "*NODE PRINT,NSET=PLATE_EDGE_RF"
    if original.count(target) != 1 or "*CONTACT PAIR" in original or "*CLOAD" in original:
        reject("BASE_DECK_CHANGED")
    sign = 1.0 if case == "up" else -1.0
    loads = "*CLOAD\n" + "".join(
        f"{node},3,{sign * FORCE_N / len(nodes):.8f}\n" for node in nodes)
    result = original.replace(target, loads + target)
    if (result.count("*CLOAD") != 1 or result.count("*CONTACT PAIR") != 0 or
        result.count("*ELEMENT,TYPE=S8R") != 2 or
        result.count("*STEP") != 1 or result.count("*END STEP") != 1):
        reject("DECK_SCOPE")
    return result


def generate(folder, n, case):
    path = Path(folder)
    if path.exists() or path.is_symlink():
        reject("WORKSPACE_NOT_FRESH")
    path.mkdir(parents=True)
    (path / "panel.inp").write_text(deck(n, case), encoding="utf-8")


def measure(folder, n, case):
    path = Path(folder)
    files = {suffix: path / ("panel." + suffix) for suffix in ("inp", "sta", "dat", "frd")}
    for suffix, file in files.items():
        upper = 64000000 if suffix == "frd" else 10000000
        if file.is_symlink() or not file.is_file() or not 0 < file.stat().st_size < upper:
            reject("MISSING_" + suffix)
    if files["inp"].read_bytes() != deck(n, case).encode("utf-8"):
        reject("INPUT_PROVENANCE")
    times = []
    for line in files["sta"].read_text(encoding="ascii").splitlines():
        fields = line.split()
        if len(fields) == 7 and fields[0] == "1":
            timestamp = float(fields[4])
            if not math.isfinite(timestamp):
                reject("NONFINITE_TIME")
            times.append(timestamp)
    if not times or abs(times[-1] - 1.0) > 1e-7:
        reject("INCOMPLETE_SOLVE")
    raw = files["dat"].read_text(encoding="utf-8", errors="replace")
    topo, nodes = load_nodes(n)
    values = {}
    for name, expected_nodes in (
        ("PLATE_EDGE_RF", topo["clamped_plate"]),
        ("RIB_END_RF", topo["clamped_rib_end"]),
        ("CENTER_RF", (topo["center"],)),
    ):
        entries = rf(raw, name)
        if set(entries) != set(expected_nodes):
            reject("RF_NODE_COVERAGE_" + name)
        values[name] = math.fsum(row[2] for row in entries.values())
    applied = FORCE_N if case == "up" else -FORCE_N
    rib_sum = values["RIB_END_RF"]
    residual = noncontact_known_force_residual(rib_sum, applied)
    return {
        "known_applied_force_n": applied,
        "known_applied_nodes": list(nodes),
        "rib_end_raw_rf3_n": rib_sum,
        "rib_external_force_balance_residual_n": residual,
        "noncontact_known_force_balance_state": "OBSERVED_WITHIN_NUMERIC_TOLERANCE",
        "plate_edge_raw_rf3_n": values["PLATE_EDGE_RF"],
        "center_raw_rf3_n": values["CENTER_RF"],
        "plate_raw_rf3_sum_n": math.fsum(
            (values["PLATE_EDGE_RF"], values["CENTER_RF"])),
        "sha256": {suffix: hashlib.sha256(file.read_bytes()).hexdigest()
                   for suffix, file in files.items()},
        "raw_rf_includes_all_shell_mpc_forces": "UNPROVEN",
        "engineering_acceptance": "NOT_ADMITTED",
    }


def observe(root):
    records = {}
    for n in MESHES:
        records[str(n)] = {
            case: measure(Path(root) / f"u_rib_known_force_n{n}_{case}", n, case)
            for case in CASES
        }
    return {
        "scope": SCOPE,
        "plate_control_displacement_mm": DRIVE_MM,
        "known_external_force_magnitude_n": FORCE_N,
        "noncontact_known_force_balance_tolerance_n": NONCONTACT_RIB_BALANCE_TOL_N,
        "cases": records,
        "independent_contact_transfer_oracle": "NOT_ESTABLISHED",
        "mpc_reaction_reconstruction": "NOT_ESTABLISHED",
        "engineering_acceptance": "NOT_ADMITTED",
    }


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "--generate":
        generate(sys.argv[2], int(sys.argv[3]), sys.argv[4])
    elif len(sys.argv) == 2:
        print(json.dumps(observe(sys.argv[1]), sort_keys=True, allow_nan=False))
        print("U_RIB_KNOWN_FORCE_OBSERVATION_ONLY_NOT_DESIGN")
    else:
        raise SystemExit("usage: ROOT | --generate DIR MESH CASE")
