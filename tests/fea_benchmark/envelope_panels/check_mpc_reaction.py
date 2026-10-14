"""Stage 69: bounded single-axis CalculiX 2.21 MPC and clean SPC study.

Synthetic N-mm model only. No independent MPC multiplier, rigid-body moment,
S8R connector force, six-component balance or design capacity admission.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path

CASES = ("control", "equation")
K_N_PER_MM = 250.0
LOAD_N = 1.25
EXPECTED_U_MM = LOAD_N / K_N_PER_MM
NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?"
DATA_ROW = re.compile(r"\s*(\d+)\s+(" + NUM + r")\s+(" + NUM + r")\s+(" + NUM + r")\s*")


def deck(case: str) -> str:
    if case not in CASES:
        raise ValueError("STAGE69_CASE_OUTSIDE_SCOPE")
    lines = [
        "*HEADING", "stage69-isolated-z-equation-" + case,
        "*NODE", "1,0.,0.,0.", "2,1.,0.,0.",
    ]
    if case == "equation":
        lines.append("3,2.,0.,0.")
    lines += [
        "*NSET,NSET=SPC", "1", "*NSET,NSET=SLAVE", "2",
    ]
    if case == "equation":
        lines += ["*NSET,NSET=MASTER", "3"]
    lines += [
        "*ELEMENT,TYPE=SPRING2,ELSET=LINK", "1,1,2",
        "*SPRING,ELSET=LINK", "3,3", f"{K_N_PER_MM:.8f}",
    ]
    if case == "equation":
        # The FIRST listed DOF (2,3) is the dependent, eliminated variable.
        lines += ["*EQUATION", "2", "2,3,1.0,3,3,-1.0"]
    lines += ["*BOUNDARY", "1,1,3,0.", "2,1,2,0."]
    if case == "equation":
        lines.append("3,1,2,0.")
    lines += [
        "*STEP", "*STATIC", "0.1,1.,0.00001,0.1",
        "*CLOAD", f"{3 if case == 'equation' else 2},3,{LOAD_N:.8f}",
        "*NODE PRINT,NSET=SPC", "U,RF",
        "*NODE PRINT,NSET=SLAVE", "U,RF",
    ]
    if case == "equation":
        lines += ["*NODE PRINT,NSET=MASTER", "U,RF"]
    lines += ["*END STEP"]
    value = "\n".join(lines) + "\n"
    if (value.count("*EQUATION") != (case == "equation")
        or value.count("*RIGID BODY") != 0
        or value.count("*CLOAD") != 1
        or value.count("*ELEMENT,TYPE=SPRING2") != 1
        or any(s in value for s in ("*PLASTIC", "NLGEOM", "S8R"))):
        raise ValueError("STAGE69_DECK_ISOLATION_FAILED")
    return value


def generate(path: Path, case: str) -> None:
    if case not in CASES or path.exists() or path.is_symlink():
        raise ValueError("STAGE69_FRESH_DIRECTORY_REQUIRED")
    path.mkdir(parents=True)
    (path / "panel.inp").write_text(deck(case), encoding="utf-8")


def read_field(data: str, name: str, node_set: str, optional: bool = False) -> dict[int, tuple[float, float, float]]:
    if name not in ("displacements", "forces") or node_set not in ("SPC", "SLAVE", "MASTER"):
        raise ValueError("STAGE69_FIELD_OUTSIDE_SCOPE")
    regex = re.compile(r"(?im)^\s*" + name + r"\s+\([^\n]*\)\s+for set\s+" + node_set +
                       r"\s+and time\s+(" + NUM + r")\s*$")
    headers = list(regex.finditer(data))
    if not headers:
        if optional:
            return {}
        raise ValueError("STAGE69_FINAL_HEADER_NOT_FOUND:" + name + ":" + node_set)
    last = headers[-1]
    if abs(float(last.group(1).replace("D", "E"))-1.) > 1e-7:
        raise ValueError("STAGE69_FINAL_TIME_INVALID")
    found: dict[int, tuple[float, float, float]] = {}
    for line in data[last.end():].splitlines():
        if not line.strip():
            if found:
                break
            continue
        m = DATA_ROW.fullmatch(line)
        if m:
            n = int(m.group(1))
            xyz = tuple(float(m.group(i).replace("D", "E")) for i in (2, 3, 4))
            if n in found or not all(math.isfinite(x) for x in xyz):
                raise ValueError("STAGE69_DUPLICATE_OR_NONFINITE_NODE_VALUE")
            found[n] = xyz
        elif found:
            break
    if not found and not optional:
        raise ValueError("STAGE69_NO_NUMERIC_ROWS:" + name + ":" + node_set)
    return found


def near(observed: float, expected: float, abs_tol: float = 2e-5, rel_tol: float = 0.003) -> bool:
    return math.isfinite(observed) and abs(observed - expected) <= max(abs_tol, rel_tol * abs(expected))


def completed(path: Path) -> None:
    # CalculiX .sta is a numerical increment table, not a prose marker.
    # Require a finite final step-1 total time of 1.0 (as in existing KB tests).
    times = []
    for row in path.read_text(encoding="ascii").splitlines():
        parts = row.split()
        if len(parts) == 7 and parts[0] == "1":
            try:
                times.append(float(parts[4]))
            except ValueError as err:
                raise ValueError("STAGE69_INVALID_STA_TIME") from err
    if not times or not math.isfinite(times[-1]) or abs(times[-1]-1.) > 1e-7:
        raise ValueError("STAGE69_SOLVER_COMPLETION_NOT_ESTABLISHED")


def inspect(folder: Path, case: str) -> dict:
    if case not in CASES:
        raise ValueError("STAGE69_CASE_OUTSIDE_SCOPE")
    files = {s: folder / ("panel." + s) for s in ("inp", "dat", "sta", "frd")}
    for ext, path in files.items():
        limit = 64_000_000 if ext == "frd" else 10_000_000
        if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= limit:
            raise ValueError("STAGE69_REQUIRED_FILE_MISSING:" + ext)
    if files["inp"].read_bytes() != deck(case).encode("utf-8"):
        raise ValueError("STAGE69_DECK_PROVENANCE_MISMATCH")
    completed(files["sta"])
    dat = files["dat"].read_text(encoding="utf-8", errors="replace")
    uz1 = read_field(dat, "displacements", "SPC")
    uz2 = read_field(dat, "displacements", "SLAVE")
    rf1 = read_field(dat, "forces", "SPC")
    if set(uz1) != {1} or set(uz2) != {2} or set(rf1) != {1}:
        raise ValueError("STAGE69_REQUIRED_NODE_COVERAGE_MISMATCH")
    u3 = read_field(dat, "displacements", "MASTER") if case == "equation" else {}
    if case == "equation" and set(u3) != {3}:
        raise ValueError("STAGE69_MASTER_DISPLACEMENT_UNOBSERVED")
    support_z = rf1[1][2]
    if not near(uz1[1][2], 0, 1e-9, 0):
        raise ValueError("STAGE69_FIXED_SPC_NOT_FIXED")
    if not near(uz2[2][2], EXPECTED_U_MM):
        raise ValueError("STAGE69_SLAVE_U_ANALYTIC_MISMATCH")
    if case == "equation" and (not near(u3[3][2], EXPECTED_U_MM)
                                 or not near(u3[3][2]-uz2[2][2], 0., 1e-9, 0.)):
        raise ValueError("STAGE69_MPC_CONSTRAINT_OR_ANALYTIC_MISMATCH")
    # This clean SPC has no direct CLOAD; compare the RAW solver RF with the
    # independent simple static external force oracle, not derived k*U alone.
    if not near(support_z, -LOAD_N):
        raise ValueError("STAGE69_INDEPENDENT_SPC_RF_FORCE_BALANCE_FAILED")
    observations = {}
    for set_name, node_id in (("SLAVE",2),("MASTER",3)):
        if set_name == "MASTER" and case != "equation":
            continue
        rows = read_field(dat, "forces", set_name, optional=True)
        if rows and set(rows) != {node_id}:
            raise ValueError("STAGE69_OPTIONAL_RF_NODE_COVERAGE_MISMATCH")
        observations[set_name.lower()] = (rows[node_id][2] if rows else None)
    return {
        "case":case, "unit_system":"N_mm", "target_solver":"CalculiX_2.21",
        "equation_dependent_dof":"node2_U3" if case=="equation" else "NONE",
        "load_applied_node":3 if case=="equation" else 2,
        "independent_oracle_u_mm":EXPECTED_U_MM,
        "observed_slave_u3_mm":uz2[2][2],
        "observed_master_u3_mm":u3[3][2] if u3 else None,
        "raw_solver_spc_rf3_n":support_z,
        "independent_external_load_n":LOAD_N,
        "signed_external_and_clean_support_sum_n":support_z+LOAD_N,
        "rf_diagnostic_non_support_n":observations,
        "mpc_multiplier_native_observation":"NOT_ADMITTED",
        "solver_rf_at_dependent_dof":"DIAGNOSTIC_ONLY_NOT_SUPPORT_REACTION",
        "general_mpc_force_reconstruction":"NOT_ADMITTED",
        "six_component_balance":"NOT_ADMITTED",
        "engineering_capacity":"NOT_ADMITTED",
        "sha256":{key:hashlib.sha256(path.read_bytes()).hexdigest() for key,path in files.items()},
    }


def crosscheck(cases: dict[str,dict]) -> dict:
    if set(cases) != set(CASES):
        raise ValueError("STAGE69_CASE_COVERAGE_MISMATCH")
    control, eq = (cases[c] for c in CASES)
    for c in (control,eq):
        if not near(c["signed_external_and_clean_support_sum_n"],0.,2e-5,0.):
            raise ValueError("STAGE69_GLOBAL_FORCE_BALANCE_FAILED")
    if not near(control["observed_slave_u3_mm"],eq["observed_slave_u3_mm"]):
        raise ValueError("STAGE69_MPC_CONTROL_DISPLACEMENT_MISMATCH")
    if not near(control["raw_solver_spc_rf3_n"],eq["raw_solver_spc_rf3_n"]):
        raise ValueError("STAGE69_MPC_CONTROL_SUPPORT_FORCE_MISMATCH")
    return {"cases":cases,
            "scope":"ISOLATED_ONE_AXIS_CLEAN_SPC_AND_TWO_TERM_EQUATION",
            "qualified_result":"INDEPENDENT_SINGLE_AXIS_SUPPORT_FORCE_BALANCE_ONLY",
            "mpc_constraint_force":"NOT_INDEPENDENTLY_OBSERVED",
            "generalized_force_moment_balance":"NOT_ADMITTED",
            "engineering_capacity":"NOT_ADMITTED"}


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--generate":
        generate(Path(sys.argv[2]),sys.argv[3]); print("STAGE69_SYNTHETIC_DECK_GENERATED")
    elif len(sys.argv) == 2:
        root = Path(sys.argv[1])
        print(json.dumps(crosscheck({c:inspect(root/("mpc69_"+c),c) for c in CASES}),
                         sort_keys=True,allow_nan=False))
        print("STAGE69_MPC_SINGLE_AXIS_SUPPORT_BALANCE_PASS; NO_GENERAL_MPC_OR_CAPACITY")
    else:
        raise SystemExit("USAGE: check_mpc_reaction.py ROOT | --generate DIR CASE")
