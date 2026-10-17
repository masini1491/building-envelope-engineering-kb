"""S8R reaction-output mapping A/B, synthetic observation only.

Only additional request in B is RF in the NODE FILE card. This may trigger
CalculiX 2.21 printout.f -> map3dto1d2d(iforce=1). The original S8R
physics gate is NOT replaced or relaxed; even an RF delta is not a true
expanded-node or MPC balance oracle.
"""
from __future__ import annotations
import hashlib
import json
import math
import sys
from pathlib import Path

from probe_s8r_all_original_rf import (
    deck as baseline_deck, analyze_text, _files as baseline_files,
)
from check_u_rib_shell_links import MESHES
from check_s8r_normal_contact import rf

SCOPE = "SYNTHETIC_S8R_RF_NODE_FILE_OUTPUT_MAPPING_AB"
MARKER = "*NODE FILE,OUTPUT=3D\nU\n"
REPLACEMENT = "*NODE FILE,OUTPUT=3D\nU,RF\n"
SET = "ALL_ORIGINAL_RF"


def deck(n: int) -> str:
    if type(n) is not int or n not in MESHES:
        raise ValueError("S8R_RF_PROJECTION_OUTSIDE_SCOPE")
    original = baseline_deck(n)
    if original.count(MARKER) != 1:
        raise ValueError("S8R_RF_PROJECTION_DECK_ANCHOR")
    candidate = original.replace(MARKER, REPLACEMENT)
    if candidate.replace(REPLACEMENT, MARKER) != original:
        raise ValueError("S8R_RF_PROJECTION_UNEXPECTED_DIFF")
    if candidate.count("*CONTACT PAIR") != 1 or candidate.count("*NODE FILE,OUTPUT=3D") != 1:
        raise ValueError("S8R_RF_PROJECTION_CHANGED_PHYSICS")
    return candidate


def generate(folder: str | Path, n: int) -> None:
    payload = deck(n)
    path = Path(folder)
    if path.exists() or path.is_symlink():
        raise ValueError("S8R_RF_PROJECTION_WORKSPACE_NOT_FRESH")
    path.mkdir(parents=True)
    (path / "panel.inp").write_bytes(payload.encode("utf-8"))


def _case_files(root: Path, n: int) -> dict[str, Path]:
    folder = root / f"u_s8r_rf_projection_n{n}_toward"
    out = {ext: folder / f"panel.{ext}" for ext in ("inp", "dat", "sta", "frd")}
    for ext, path in out.items():
        cap = 64_000_000 if ext == "frd" else 10_000_000
        if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size < cap:
            raise ValueError("S8R_RF_PROJECTION_ARTIFACT_MISSING_" + ext)
    if out["inp"].read_bytes() != deck(n).encode("utf-8"):
        raise ValueError("S8R_RF_PROJECTION_INPUT_PROVENANCE")
    times = []
    for row in out["sta"].read_text(encoding="ascii").splitlines():
        cells = row.split()
        if len(cells) == 7 and cells[0] == "1":
            try:
                t = float(cells[4])
            except ValueError as exc:
                raise ValueError("S8R_RF_PROJECTION_BAD_STATUS") from exc
            if not math.isfinite(t):
                raise ValueError("S8R_RF_PROJECTION_BAD_STATUS")
            times.append(t)
    if not times or abs(times[-1] - 1.0) > 1e-7:
        raise ValueError("S8R_RF_PROJECTION_INCOMPLETE")
    return out



def final_frd_forc(payload: bytes, original_node_upper_bound: int) -> dict:
    """Last complete FRD FORC block only; reported-node sum is not a solver force oracle."""
    lines = payload.decode("ascii").splitlines()
    headers = [i for i, line in enumerate(lines) if line.startswith(" -4  FORC")]
    if not headers:
        raise ValueError("S8R_FRD_FORCE_RECORD_MISSING")
    i = headers[-1]
    header = lines[i - 1].split() if i else []
    if len(header) < 4 or header[0] != "100CL":
        raise ValueError("S8R_FRD_FORCE_STEP_INVALID")
    try:
        t = float(header[2])
        count = int(header[3])
    except (ValueError, IndexError) as exc:
        raise ValueError("S8R_FRD_FORCE_STEP_INVALID") from exc
    if not math.isfinite(t) or abs(t - 1.0) > 1e-7 or count <= 0:
        raise ValueError("S8R_FRD_FORCE_STEP_INVALID")
    observed, terminated = {}, False
    for line in lines[i + 1:]:
        if line.startswith(" -3"):
            terminated = True
            break
        if line.startswith(" -5"):
            continue
        # Fixed-width FRD node ID (10) + three force components (12 each).
        # A truncated final component may still parse as a finite float.
        if not line.startswith(" -1") or len(line) < 3 + 10 + 3 * 12:
            raise ValueError("S8R_FRD_FORCE_RECORD_INVALID")
        try:
            node_id = int(line[3:13])
            vals = [float(line[13 + 12 * j:25 + 12 * j]) for j in range(3)]
        except ValueError as exc:
            raise ValueError("S8R_FRD_FORCE_RECORD_INVALID") from exc
        if (node_id in observed or node_id <= original_node_upper_bound or
                not all(map(math.isfinite, vals))):
            raise ValueError("S8R_FRD_FORCE_NODE_ID_OR_VALUE")
        observed[node_id] = vals[2]
    if not terminated or len(observed) != count:
        raise ValueError("S8R_FRD_FORCE_RECORD_COUNT")
    return {
        "frd_final_force_record_count": count,
        "frd_final_expanded_node_min_id": min(observed),
        "frd_final_expanded_node_max_id": max(observed),
        "frd_final_reported_nodes_rf3_sum_n": math.fsum(observed.values()),
        "frd_node_id_scope": "ONLY_IDS_GREATER_THAN_INPUT_ORIGINAL_NODES",
        "frd_is_complete_solver_force_oracle": False,
    }


def observe(root: str | Path) -> dict:
    root = Path(root)
    results = {}
    for n in MESHES:
        original = baseline_files(root, n)
        projection = _case_files(root, n)
        original_dat = original["dat"].read_text(encoding="utf-8", errors="replace")
        projection_dat = projection["dat"].read_text(encoding="utf-8", errors="replace")
        original_report = analyze_text(original_dat, n)
        projection_report = analyze_text(projection_dat, n)
        old_nodes = rf(original_dat, SET)
        new_nodes = rf(projection_dat, SET)
        if set(old_nodes) != set(new_nodes):
            raise ValueError("S8R_RF_PROJECTION_NODE_ID_DRIFT")
        delta = math.fsum(new_nodes[i][2] - old_nodes[i][2] for i in old_nodes)
        abs_delta = max(abs(new_nodes[i][2] - old_nodes[i][2]) for i in old_nodes)
        if not all(map(math.isfinite, (delta, abs_delta))):
            raise ValueError("S8R_RF_PROJECTION_NONFINITE")
        frd_report = final_frd_forc(
            projection["frd"].read_bytes(),
            original_report["all_original_node_count"],
        )
        results[str(n)] = {
            "baseline_all_original_rf3_n": original_report["all_original_nodes_rf3_sum_n"],
            "frd_reported_node_force_observation": frd_report,
            "frd_minus_dat_original_rf3_n": (
                frd_report["frd_final_reported_nodes_rf3_sum_n"] -
                projection_report["all_original_nodes_rf3_sum_n"]
            ),
            "rf_output_all_original_rf3_n": projection_report["all_original_nodes_rf3_sum_n"],
            "sum_of_per_node_rf3_changes_n": delta,
            "max_abs_per_node_rf3_change_n": abs_delta,
            "baseline_other_original_rf3_n": original_report["other_original_nodes_rf3_sum_n"],
            "rf_output_other_original_rf3_n": projection_report["other_original_nodes_rf3_sum_n"],
            "baseline_contact_slave_cf3_n": original_report["contact_slave_cf_z_n"],
            "rf_output_contact_slave_cf3_n": projection_report["contact_slave_cf_z_n"],
            "output_mapping_difference_state": (
                "OBSERVED_NODE_FORCE_CHANGE" if abs_delta > 1e-7
                else "NO_CHANGE_AT_REPORTED_PRECISION"
            ),
            "input_provenance_sha256": {
                "baseline": hashlib.sha256(original["inp"].read_bytes()).hexdigest(),
                "rf_output": hashlib.sha256(projection["inp"].read_bytes()).hexdigest(),
            },
            "artifacts_sha256": {
                "baseline": {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in original.items()},
                "rf_output": {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in projection.items()},
            },
        }
    return {
        "scope": SCOPE,
        "only_intentional_input_change": "NODE_FILE_U_TO_U_RF",
        "mechanical_equivalence": "NOT_INDEPENDENTLY_ESTABLISHED",
        "all_internal_expanded_nodes_reaction_oracle": "NOT_ESTABLISHED",
        "original_s8r_physical_balance_gate": "UNCHANGED_FAIL_CLOSED",
        "engineering_acceptance": "NOT_ADMITTED",
        "cases": results,
    }


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--generate":
        generate(sys.argv[2], int(sys.argv[3]))
    elif len(sys.argv) == 2:
        print(json.dumps(observe(sys.argv[1]), sort_keys=True, allow_nan=False))
    else:
        raise SystemExit("usage: ROOT | --generate DIR MESH")
