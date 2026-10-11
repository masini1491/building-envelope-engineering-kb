"""Independent isotropic Hooke-law normal-component check, low-load only.

Compare observed averaged/extrapolated C3D20 nodal strain with the isotropic
elastic inverse compliance using independently supplied E and nu.
No shear convention assumptions, Gauss-point extremes or strength admission.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from aluminum_research_input import load
from check_aluminum_elastic_scaling import _load_case
from check_aluminum_ritz import expected_input

RELATIVE_SCREENING_TOL = 0.03
MIN_OBSERVED_NORMAL_STRESS_MPA = 1.e-6


def check_normal_hooke(stress: dict, strain: dict, *, e: float, nu: float) -> dict:
    if (not stress or set(stress) != set(strain) or
            type(e) not in (float, int) or type(nu) not in (float, int)
            or not math.isfinite(e) or not math.isfinite(nu)
            or e <= 0 or not 0 < nu < 0.49):
        raise ValueError("HOOKE_INPUT_INVALID")
    maximum_stress = 0.0
    maximum_residual = 0.0
    checked = 0
    for node in sorted(stress):
        s, observed_e = stress[node], strain[node]
        if (type(node) is not int or node <= 0 or len(s) != 6 or len(observed_e) != 6 or
                any(type(v) not in (int, float) or not math.isfinite(v)
                    for v in (*s, *observed_e))):
            raise ValueError("HOOKE_NONFINITE_OR_INCOMPLETE_TENSOR")
        # Normal compliance: eps_i=[sigma_i - nu*(sigma_j+sigma_k)]/E.
        for axis in range(3):
            expected_eps = (s[axis]-nu*(s[(axis+1)%3]+s[(axis+2)%3]))/e
            residual_in_mpa = e*(observed_e[axis]-expected_eps)
            maximum_residual=max(maximum_residual,abs(residual_in_mpa))
            maximum_stress=max(maximum_stress,abs(s[axis]))
            checked+=1
    if maximum_stress <= MIN_OBSERVED_NORMAL_STRESS_MPA:
        raise ValueError("HOOKE_STRESS_SIGNAL_TOO_SMALL")
    relative = maximum_residual/maximum_stress
    if not math.isfinite(relative) or relative > RELATIVE_SCREENING_TOL:
        raise ValueError("NORMAL_ISOTROPIC_HOOKE_MISMATCH")
    return {"verification_scope":"EXPANDED_NODAL_AVERAGED_NORMAL_TENSOR_COMPONENTS",
            "independent_law":"ISOTROPIC_LINEAR_ELASTIC_NORMAL_COMPLIANCE",
            "nodes_covered":len(stress),"normal_components_checked":checked,
            "max_normal_residual_equivalent_mpa":maximum_residual,
            "max_observed_normal_stress_mpa":maximum_stress,
            "normalized_max_residual":relative,
            "research_screening_tolerance":RELATIVE_SCREENING_TOL,
            "shear_components":"NOT_CHECKED",
            "integration_point_stress_oracle":"NOT_ESTABLISHED",
            "engineering_acceptance":"NOT_ADMITTED",
            "aluminum_design_manual_capacity":"NOT_COMPUTED"}


def check_fixture(root: Path) -> dict:
    config=expected_input("thicker_square",16)
    observed=_load_case(root,config)
    return check_normal_hooke(observed["STRESS"],observed["TOSTRAIN"],
                              e=config["youngs_modulus_mpa"],nu=config["poisson_ratio"])


if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("USAGE: check_aluminum_normal_hooke.py CASE_DIR")
    print(json.dumps(check_fixture(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
    print("ALUMINUM_NORMAL_HOOKE_RESEARCH_EVIDENCE_PASS; NO DESIGN ADMISSION")
