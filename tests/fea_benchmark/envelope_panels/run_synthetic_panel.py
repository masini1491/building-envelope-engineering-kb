"""Opt-in, synthetic-only CalculiX execution + evidence adapter (KB-CAND-007).

Only repo-generated S8R large-load fixtures are admitted; no arbitrary decks,
user geometry, engineering capacity, MPC reaction or global six-DOF acceptance.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

# Support direct execution by path from any cwd, with repo-owned probe.
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.engineering_calc.calculix_probe import probe_calculix
from generate import build
from check_reconstructed_pressure_balance import reconcile
from check_expanded_moment_partition import observe_case


class SyntheticPanelEvidenceError(ValueError):
    """A solver run did not establish the required bounded evidence."""


def _completed_step(path: Path) -> None:
    """Require a final nonlinear step at time 1.0, not just process exit zero."""
    try:
        rows = path.read_text(encoding="ascii").splitlines()
    except (OSError, UnicodeError) as exc:
        raise SyntheticPanelEvidenceError("MISSING_OR_INVALID_STA") from exc
    times = []
    for line in rows:
        parts = line.split()
        if len(parts) == 7 and parts[0] == "1":
            try:
                value = float(parts[4])
            except ValueError as exc:
                raise SyntheticPanelEvidenceError("INVALID_STA_TIME") from exc
            if not math.isfinite(value):
                raise SyntheticPanelEvidenceError("INVALID_STA_TIME")
            times.append(value)
    if not times or abs(times[-1] - 1.0) > 1e-7:
        raise SyntheticPanelEvidenceError("NONLINEAR_STEP_NOT_COMPLETE")


def run_synthetic_panel(*, material: str, mesh: int, workspace: str | Path,
                        executable: str, execute: bool = False,
                        timeout_seconds: int = 90) -> dict:
    """Create one fixed, reviewed model, run CCX, audit force/moment evidence.

    The workspace must be existing, empty and operator-controlled. The solver
    executable remains external and explicitly supplied. Caller must trust the
    local executable; this is NOT a process sandbox.
    """
    if material not in ("glass", "aluminum") or type(mesh) is not int or mesh not in (4, 8, 16):
        raise ValueError("UNSUPPORTED_SYNTHETIC_FIXTURE")
    if not execute:
        return {"execution_status": "NOT_EXECUTED_OPT_IN_REQUIRED",
                "model_scope": "SYNTHETIC_S8R_ONLY",
                "engineering_acceptance": "NOT_ADMITTED"}
    raw = Path(workspace)
    if raw.is_symlink():
        raise ValueError("WORKSPACE_SYMLINK_NOT_ALLOWED")
    try:
        directory = raw.resolve(strict=True)
    except OSError as exc:
        raise ValueError("WORKSPACE_NOT_FOUND") from exc
    if not directory.is_dir() or any(directory.iterdir()):
        raise ValueError("WORKSPACE_MUST_BE_EXISTING_AND_EMPTY")
    # generate.py is the canonical synthetic deck owner; do not accept external
    # *INCLUDE, geometry, loads or arbitrary user-authored input files here.
    build(material, mesh, "large", directory)
    outcome = probe_calculix(executable=executable, job_name="panel",
                             workspace=directory, timeout_seconds=timeout_seconds,
                             execute=True)
    if outcome.execution_status != "PROCESS_EXIT_ZERO_UNVERIFIED":
        raise SyntheticPanelEvidenceError("SOLVER_DID_NOT_EXIT_ZERO:" + outcome.execution_status)
    for suffix, maximum in ((".inp", 5_000_000), (".dat", 10_000_000),
                            (".frd", 64_000_000), (".sta", 2_000_000)):
        path = directory / ("panel" + suffix)
        if (path.is_symlink() or not path.is_file() or
                not 0 < path.stat().st_size <= maximum):
            raise SyntheticPanelEvidenceError("REQUIRED_OUTPUT_MISSING_OR_UNBOUNDED:" + suffix)
    _completed_step(directory / "panel.sta")
    deck, frd, dat = (directory / ("panel" + s) for s in (".inp", ".frd", ".dat"))
    try:
        translation = reconcile(deck, frd, dat, material)
        moment = observe_case(deck, frd, dat, material)
    except (ValueError, OSError) as exc:
        raise SyntheticPanelEvidenceError("BOUNDED_AUDIT_REJECTED:" + type(exc).__name__) from exc
    output = {
        "execution_status": "SYNTHETIC_BENCHMARK_EVIDENCE_PASS",
        "process_exit_code": outcome.exit_code,
        "model_scope": "FIXED_SYNTHETIC_S8R_NLGEOM_P1",
        "material_proxy": material, "mesh": mesh,
        "translational_balance": translation,
        "expanded_moment_partition": moment,
        "independent_rotational_reaction": "UNOBSERVED",
        "six_component_global_balance": "NOT_ADMITTED",
        "engineering_acceptance": "NOT_ADMITTED",
        "design_capacity": "NOT_COMPUTED",
    }
    json.dumps(output, allow_nan=False)
    return output


def main() -> int:
    cli = argparse.ArgumentParser(description="Synthetic-only CCX audited execution")
    cli.add_argument("--material", choices=("glass", "aluminum"), required=True)
    cli.add_argument("--mesh", type=int, choices=(4, 8, 16), required=True)
    cli.add_argument("--workspace", type=Path, required=True)
    cli.add_argument("--ccx", required=True, help="explicit trusted installed executable path")
    cli.add_argument("--execute", action="store_true", default=False)
    args = cli.parse_args()
    try:
        result = run_synthetic_panel(material=args.material, mesh=args.mesh,
                                     workspace=args.workspace, executable=args.ccx,
                                     execute=args.execute)
    except (ValueError, OSError) as exc:
        print(json.dumps({"execution_status": "EVIDENCE_REJECTED",
                          "reason": str(exc)[:180],
                          "engineering_acceptance": "NOT_ADMITTED"}))
        return 2
    print(json.dumps(result, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
