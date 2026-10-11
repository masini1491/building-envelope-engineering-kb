"""Stage 43: bounded independent *scaling-law* check for CCX S8R research.

An analytical linear-elastic invariant (response ~ applied uniform pressure)
is checked against two separately executed real CCX 2.21 nonlinear solves.
Not an independent absolute stress/strain field oracle or capacity criterion.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

from aluminum_research_input import load
from aluminum_tensor_observation import read_final_tensors
from check_aluminum_ritz import expected_input
from check_expanded_frd import read_expanded_frd
from check_follower_pressure import displacement_block
from check_pressure_equilibrium import parse_deck

FACTOR = 2.0
RESEARCH_REL_TOL = 0.04
SIGNAL_MINIMUM = {"displacement": 1e-8, "STRESS": 1e-6, "TOSTRAIN": 1e-10}


def validate_response_scaling(baseline: dict, doubled: dict, *, label: str) -> dict:
    """Compare every keyed vector, not only maxima or cherry-picked locations."""
    if label not in SIGNAL_MINIMUM or not baseline or set(baseline) != set(doubled):
        raise ValueError("SCALING_FIELD_COVERAGE_MISMATCH")
    if not all(type(node) is int and node > 0 for node in baseline):
        raise ValueError("SCALING_NODE_ID_INVALID")
    values0, values1 = [], []
    for node in sorted(baseline):
        for first, second in ((baseline[node], doubled[node]),):
            count = 3 if label == "displacement" else 6
            if (not isinstance(first, (tuple, list)) or not isinstance(second, (tuple, list))
                    or len(first) != count or len(second) != count):
                raise ValueError("SCALING_COMPONENT_COUNT_MISMATCH")
            if any(type(x) not in (int, float) or not math.isfinite(x)
                   for x in (*first, *second)):
                raise ValueError("SCALING_NONFINITE_FIELD")
            values0.extend(float(x) for x in first)
            values1.extend(float(x) for x in second)
    amplitude = max(map(abs, values0))
    if amplitude <= SIGNAL_MINIMUM[label]:
        raise ValueError("SCALING_REFERENCE_SIGNAL_TOO_SMALL")
    maximum = max(abs(high - FACTOR * low) for low, high in zip(values0, values1))
    normalized = maximum / (FACTOR * amplitude)
    if normalized > RESEARCH_REL_TOL:
        raise ValueError("LINEAR_ELASTIC_SCALING_DISAGREEMENT:" + label)
    return {"nodes": len(baseline), "components_per_node": 3 if label == "displacement" else 6,
            "relative_max_component_deviation": normalized,
            "reference_max_abs_component": amplitude}


def _digest(path: Path) -> str:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 64_000_000:
        raise ValueError("SCALING_ARTIFACT_MISSING_OR_UNBOUNDED")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_case(directory: Path, expected: dict) -> dict:
    cfg = load(directory / "input.json")
    if cfg != expected:
        raise ValueError("SCALING_FIXTURE_CONFIG_MISMATCH")
    report = json.loads((directory / "output.json").read_text(encoding="utf-8"))
    if (report.get("execution_status") != "ALUMINUM_PARAMETRIC_RESEARCH_EVIDENCE_PASS"
            or report.get("engineering_acceptance") != "NOT_ADMITTED"
            or report.get("inputs") != cfg
            or report.get("aluminum_design_manual_capacity") != "NOT_COMPUTED"):
        raise ValueError("SCALING_SOLVER_EVIDENCE_INVALID")
    observations = report.get("research_observations")
    if (not isinstance(observations, dict)
            or observations.get("engineering_acceptance") != "NOT_ADMITTED"
            or any(not isinstance(observations.get(field), dict)
                   or observations[field].get("field") != kind
                   or observations[field].get("integration_point_extreme") != "NOT_OBSERVED"
                   or observations[field].get("independent_numerical_oracle") != "NOT_ESTABLISHED"
                   for field, kind in (("stress", "STRESS"), ("strain", "TOSTRAIN")))):
        raise ValueError("SCALING_TENSOR_EVIDENCE_INVALID")
    workspace = directory / "run"
    inp, frd, dat = (workspace / ("panel." + ext) for ext in ("inp", "frd", "dat"))
    hashes = report.get("artifact_provenance", {})
    if not isinstance(hashes, dict) or any(
            hashes.get(field) != _digest(path) for field, path in
            (("input_sha256", inp), ("frd_sha256", frd), ("dat_sha256", dat))):
        raise ValueError("SCALING_ARTIFACT_HASH_MISMATCH")
    nodes, elements, edge, pressure = parse_deck(inp)
    if (len(elements) != expected["mesh"]**2 or not edge
            or abs(pressure - expected["pressure_n_mm2"]) > 1e-12):
        raise ValueError("SCALING_DECK_INVALID")
    coords, expanded, expanded_u = read_expanded_frd(frd)
    tensor = read_final_tensors(frd, set(coords))
    original_u = displacement_block(dat.read_text(encoding="utf-8", errors="replace"),
                                    set(nodes))
    if observations["stress"].get("expanded_nodes_covered") != len(coords) or (
            observations["strain"].get("expanded_nodes_covered") != len(coords)):
        raise ValueError("SCALING_RESULT_COVERAGE_MISMATCH")
    if max(abs(u[2]) for u in original_u.values()) >= .05*expected["thickness_mm"]:
        raise ValueError("SCALING_NOT_SMALL_DEFLECTION")
    return {"nodes": nodes, "expanded_xyz": coords, "expanded": expanded,
            "displacement": original_u, **tensor}


def check_pair(baseline: Path, doubled: Path) -> dict:
    reference = expected_input("thicker_square", 16)
    twice = {**reference, "pressure_n_mm2": 2*reference["pressure_n_mm2"]}
    a = _load_case(baseline, reference)
    b = _load_case(doubled, twice)
    if (a["nodes"] != b["nodes"] or a["expanded_xyz"] != b["expanded_xyz"]
            or a["expanded"] != b["expanded"]):
        raise ValueError("SCALING_MODEL_TOPOLOGY_OR_GEOMETRY_DRIFT")
    comparison = {key: validate_response_scaling(a[key], b[key], label=key)
                  for key in ("displacement", "STRESS", "TOSTRAIN")}
    return {"verification_scope": "LOW_LOAD_SAME_MODEL_TWO_PRESSURES",
            "analytical_invariant": "FIRST_ORDER_LINEAR_ELASTIC_PRESSURE_SCALING",
            "applied_pressure_multiplier": FACTOR, "relative_research_tolerance": RESEARCH_REL_TOL,
            "fields": comparison,
            "absolute_stress_strain_oracle": "NOT_ESTABLISHED",
            "engineering_acceptance": "NOT_ADMITTED",
            "aluminum_design_manual_capacity": "NOT_COMPUTED",
            "general_global_balance": "NOT_ADMITTED"}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: check_aluminum_elastic_scaling.py BASE_DIR DOUBLE_DIR")
    print(json.dumps(check_pair(Path(sys.argv[1]), Path(sys.argv[2])),
                     allow_nan=False, sort_keys=True))
    print("ALUMINUM_TENSOR_PRESSURE_SCALING_RESEARCH_PASS; NO DESIGN CAPACITY")
