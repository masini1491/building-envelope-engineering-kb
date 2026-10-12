"""Six already-solved synthetic plate cases: center stress and mesh refinement.

Reuses the two Stage-40 true CCX fixture families (4/8/16). No new solver
runs and no material/property admission. Nodal-averaged shell-expanded stress
is not a Gauss-point extremum or design capacity.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from aluminum_research_input import load
from aluminum_tensor_observation import read_final_tensors
from check_aluminum_elastic_scaling import _digest
from check_aluminum_ritz import CASES, MESHES, center_z, check_fixture, expected_input
from check_aluminum_ritz_stress import compare
from check_expanded_frd import read_expanded_frd


def contraction_by_mesh(values: dict[int, float]) -> dict:
    """Observed n=4 -> 8 -> 16 sequence; no extrapolated exact solution."""
    if not isinstance(values, dict) or set(values) != set(MESHES):
        raise ValueError("STRESS_MESH_TRIPLET_REQUIRED")
    if any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0
           for v in values.values()):
        raise ValueError("STRESS_MESH_NONPOSITIVE_OR_NONFINITE")
    coarse = abs(values[8] - values[4])
    fine = abs(values[16] - values[8])
    if not coarse > 1e-8 or not fine < coarse:
        raise ValueError("STRESS_MESH_CHANGE_NOT_CONTRACTING")
    return {"observed_center_bending_mpa_by_mesh":values,
            "coarse_change_mpa":coarse, "fine_change_mpa":fine,
            "change_contraction_observed":True,
            "independent_exact_field_solution":"NOT_ESTABLISHED",
            "engineering_acceptance":"NOT_ADMITTED"}


def _load_mesh(root: Path, case: str, n: int) -> dict:
    config = expected_input(case, n)
    if load(root/f"input_{n}.json") != config:
        raise ValueError("MESH_STRESS_CONFIG_DRIFT")
    result = json.loads((root/f"output_{n}.json").read_text(encoding="utf-8"))
    if (not isinstance(result, dict)
            or result.get("execution_status") != "ALUMINUM_PARAMETRIC_RESEARCH_EVIDENCE_PASS"
            or result.get("inputs") != config
            or result.get("engineering_acceptance") != "NOT_ADMITTED"
            or result.get("aluminum_design_manual_capacity") != "NOT_COMPUTED"
            or result.get("global_six_component_balance") != "NOT_ADMITTED"):
        raise ValueError("MESH_STRESS_SOLVER_EVIDENCE_REJECTED")
    obs = result.get("research_observations")
    if (not isinstance(obs, dict) or not isinstance(obs.get("stress"), dict)
            or obs.get("engineering_acceptance") != "NOT_ADMITTED"
            or obs["stress"].get("field") != "STRESS"
            or obs["stress"].get("integration_point_extreme") != "NOT_OBSERVED"
            or obs["stress"].get("independent_numerical_oracle") != "NOT_ESTABLISHED"):
        raise ValueError("MESH_STRESS_OBSERVATION_STATUS_MISMATCH")
    run = root/f"mesh_{n}"
    hashes = result.get("artifact_provenance")
    if not isinstance(hashes, dict):
        raise ValueError("MESH_STRESS_PROVENANCE_MISSING")
    for suffix, key in (("inp","input_sha256"), ("dat","dat_sha256"), ("frd","frd_sha256")):
        if hashes.get(key) != _digest(run/f"panel.{suffix}"):
            raise ValueError("MESH_STRESS_ARTIFACT_HASH_MISMATCH:" + suffix)
    coords, expanded, _ = read_expanded_frd(run/"panel.frd")
    if len(expanded) != n*n or set(expanded) != set(range(1,n*n+1)):
        raise ValueError("MESH_STRESS_EXPANDED_ELEMENTS_INCOMPLETE")
    field = read_final_tensors(run/"panel.frd", set(coords))["STRESS"]
    if obs["stress"].get("expanded_nodes_covered") != len(coords):
        raise ValueError("MESH_STRESS_NODE_COUNT_INCONSISTENT")
    center = center_z(run/"panel.dat")
    # Stage 54 screening tolerances were admitted only at n=16. Coarse
    # meshes supply observations, not a false fine-mesh PASS.
    if n == 16:
        result = compare(config, coords, field, center)
        if result["reference_is_exact_3d_field"] is not False:
            raise ValueError("MESH_STRESS_SCOPE_ESCALATION")
        return result
    a,b,t = config["width_mm"],config["height_mm"],config["thickness_mm"]
    tolerance=max(1e-5,1e-6*max(a,b,t))
    surfaces={"+":[], "-":[]}
    for node,xyz in coords.items():
        if (type(node) is not int or node<=0 or len(xyz)!=3
                or len(field[node])!=6
                or any(type(v) not in (int,float) or not math.isfinite(v)
                       for v in (*xyz,*field[node]))):
            raise ValueError("COARSE_CENTER_STRESS_INVALID")
        x,y,z=xyz
        if abs(x-a/2)<=tolerance and abs(y-b/2)<=tolerance and abs(abs(z)-t/2)<=tolerance:
            surfaces["+" if z>0 else "-"].append(field[node])
    if any(not 1<=len(surfaces[side])<=16 for side in ("+","-")):
        raise ValueError("COARSE_CENTER_SURFACE_COVERAGE_MISSING")
    stress={}
    for component,index in (("SXX",0),("SYY",1)):
        means=[sum(v[index] for v in surfaces[side])/len(surfaces[side]) for side in ("+","-")]
        stress[component]={"observed_bending_mpa":abs((means[0]-means[1])/2),
                           "observed_membrane_mpa":abs((means[0]+means[1])/2)}
        if stress[component]["observed_bending_mpa"]<=0:
            raise ValueError("COARSE_CENTER_STRESS_SIGNAL_MISSING")
    return {"center_bending_stress":stress,
            "center_deflection_observed_mm":center,
            "fine_mesh_ritz_screening":"NOT_APPLICABLE_TO_COARSE_MESH",
            "engineering_acceptance":"NOT_ADMITTED"}


def check_case(root: Path, case: str) -> dict:
    if case not in CASES:
        raise ValueError("UNSUPPORTED_MESH_STRESS_CASE")
    # Existing Stage 40 independently checks deck, material, 4/8/16 U and
    # reference trend; do not replace it with an unconstrained field parser.
    deflection = check_fixture(root, case)
    results = {n:_load_mesh(root,case,n) for n in MESHES}
    series = {}
    for component in ("SXX","SYY"):
        observed = {n:results[n]["center_bending_stress"][component]["observed_bending_mpa"]
                    for n in MESHES}
        series[component] = contraction_by_mesh(observed)
    return {"scope":"SYNTHETIC_RECTANGULAR_CLAMPED_LOW_LOAD_S8R_RESEARCH",
            "fixture_family":case, "mesh_triplet":list(MESHES),
            "reference_type":"THREE_TERM_KIRCHHOFF_CLAMPED_RITZ_APPROXIMATION",
            "stress_comparisons":{n:results[n]["center_bending_stress"] for n in MESHES},
            "center_bending_change":series,
            "displacement_mesh_reference":deflection["reference_type"],
            "stress_source":"CCX_FRD_EXTRAPOLATED_AVERAGED_EXPANDED_NODES",
            "engineering_acceptance":"NOT_ADMITTED",
            "integration_point_stress_extreme":"NOT_OBSERVED",
            "independent_exact_field_solution":"NOT_ESTABLISHED",
            "aluminum_design_manual_capacity":"NOT_COMPUTED",
            "general_global_balance":"NOT_ADMITTED"}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("USAGE: check_aluminum_ritz_mesh_stress.py CASE_ROOT CASE")
    print(json.dumps(check_case(Path(sys.argv[1]),sys.argv[2]),sort_keys=True,allow_nan=False))
    print("ALUMINUM_MESH_STRESS_RITZ_APPROXIMATION_PASS; NO ENGINEERING ACCEPTANCE")
