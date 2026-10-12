"""Bounded synthetic-only cross-grade CCX replay: labels may not change physics.

Three separate explicit-input CCX runs are observed. This is not a measured
alloy/temper comparison, physical material equivalence, or strength admission.
"""
from __future__ import annotations

import json
from pathlib import Path
from aluminum_research_input import load
from prepare_aluminum_material_input import prepare

GRADES = ("3003-H14", "3004-H12", "3004-O")
MAX_JSON_BYTES = 4_000_000
LABEL_PREFIX = "USER_DECLARED_UNVERIFIED:CS Aluminum:"


def _json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= MAX_JSON_BYTES:
        raise ValueError("GRADE_REPLAY_INPUT_MISSING_OR_UNBOUNDED")
    def no_constant(_):
        raise ValueError("GRADE_REPLAY_NONFINITE_JSON")
    def unique(pairs):
        obj = {}
        for key, val in pairs:
            if key in obj:
                raise ValueError("GRADE_REPLAY_DUPLICATE_JSON_KEY")
            obj[key] = val
        return obj
    obj = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique,
                     parse_constant=no_constant)
    if not isinstance(obj, dict):
        raise ValueError("GRADE_REPLAY_INVALID_ROOT")
    return obj


def verify(root: Path) -> dict:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("GRADE_REPLAY_WORKSPACE_INVALID")
    baseline = None
    baseline_inputs = None
    input_sha = None
    solver_sha = None
    for grade in GRADES:
        choice = _json(root / f"selection_{grade}.json")
        if choice.get("alloy_temper") != grade or choice.get("property_evidence_status") != "USER_DECLARED_UNVERIFIED":
            raise ValueError("GRADE_REPLAY_NOT_EXPLICIT_UNVERIFIED_SYNTHETIC")
        wanted = prepare(choice)
        actual = load(root / f"input_{grade}.json")
        if wanted != actual or not actual["material_provenance"].startswith(LABEL_PREFIX + grade + ":"):
            raise ValueError("GRADE_REPLAY_MATERIAL_LABEL_OR_INPUT_CHANGED")
        if baseline_inputs is None:
            baseline_inputs = {k: v for k, v in actual.items() if k != "material_provenance"}
        elif {k: v for k, v in actual.items() if k != "material_provenance"} != baseline_inputs:
            raise ValueError("GRADE_REPLAY_NUMERIC_INPUTS_CHANGED")
        evidence = _json(root / f"result_{grade}.json")
        for key, value in (
            ("execution_status", "ALUMINUM_PARAMETRIC_RESEARCH_EVIDENCE_PASS"),
            ("model_scope", "RECTANGULAR_FOUR_EDGE_CLAMPED_LINEAR_ELASTIC_S8R_NLGEOM_P1"),
            ("engineering_acceptance", "NOT_ADMITTED"),
            ("global_six_component_balance", "NOT_ADMITTED"),
            ("aluminum_design_manual_capacity", "NOT_COMPUTED"),
            ("rotational_support_reaction", "UNOBSERVED"),
        ):
            if evidence.get(key) != value:
                raise ValueError("GRADE_REPLAY_EVIDENCE_SCOPE_CHANGED:" + key)
        if evidence.get("inputs") != actual:
            raise ValueError("GRADE_REPLAY_EXECUTION_INPUT_NOT_MATCHED")
        provenance = evidence.get("artifact_provenance")
        if not isinstance(provenance, dict):
            raise ValueError("GRADE_REPLAY_ARTIFACT_PROVENANCE_MISSING")
        sha = provenance.get("input_sha256")
        sol = provenance.get("solver_sha256")
        if (not isinstance(sha, str) or len(sha) != 64 or not isinstance(sol, str)
                or len(sol) != 64 or any(c not in "0123456789abcdef" for c in sha + sol)):
            raise ValueError("GRADE_REPLAY_SHA_MALFORMED")
        if input_sha is None:
            input_sha, solver_sha = sha, sol
        elif sha != input_sha or sol != solver_sha:
            raise ValueError("GRADE_REPLAY_DECK_OR_SOLVER_DIFFERENT")
        observations = {key: evidence.get(key) for key in
                        ("translational_balance", "research_observations", "expanded_moment_partition")}
        if any(value is None for value in observations.values()):
            raise ValueError("GRADE_REPLAY_OBSERVATIONS_MISSING")
        if baseline is None:
            baseline = observations
        elif observations != baseline:
            raise ValueError("GRADE_REPLAY_PHYSICS_OUTPUT_DIFFERENT")
    return {
        "scope": "SYNTHETIC_SAME_EXPLICIT_NUMERIC_PARAMETERS_DIFFERENT_GRADE_LABELS",
        "grades": list(GRADES), "same_input_deck_sha256": input_sha,
        "same_solver_sha256": solver_sha,
        "identical_observation_payload": True,
        "manufacturer_material_equivalence": "NOT_TESTED",
        "material_plasticity": "NOT_ADMITTED",
        "engineering_acceptance": "NOT_ADMITTED",
        "aluminum_design_manual_capacity": "NOT_COMPUTED",
    }


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("folder", type=Path)
    a = p.parse_args()
    print(json.dumps(verify(a.folder), sort_keys=True, allow_nan=False))
    print("SYNTHETIC_ALLOY_GRADE_LABEL_REPLAY_PASS; NO REAL ALLOY COMPARISON")
