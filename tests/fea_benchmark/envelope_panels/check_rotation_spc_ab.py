"""Stage 23 bounded S8R drilling-rotation SPC A/B diagnostic.

Same synthetic aluminum NLGEOM model, only EDGE,1,6 -> EDGE,1,5.
If solutions differ, report a divergence; NEVER call it invariance.
No generic drilling-rotation, MPC reaction, or capacity admission.
"""
from __future__ import annotations

import math
from pathlib import Path

from audit_rf_projection import rf_block
from check_expanded_frd import read_expanded_frd
from check_follower_pressure import displacement_block
from check_pressure_equilibrium import parse_deck


ORIGINAL = "EDGE,1,6,0."
VARIANT = "EDGE,1,5,0."


def make_pair(original: str):
    lines = original.splitlines(keepends=True)
    indices = [i for i, line in enumerate(lines) if line.strip().upper().replace(" ", "") == ORIGINAL]
    if len(indices) != 1 or original.count("*BOUNDARY") != 1:
        raise ValueError("UNSUPPORTED_ROTATION_AB_BASE")
    i = indices[0]
    lines[i] = lines[i].replace(lines[i].strip(), VARIANT)
    variant = "".join(lines)
    if variant == original or variant.replace(VARIANT, ORIGINAL, 1) != original:
        raise ValueError("ROTATION_AB_DECK_DIFF_NOT_ISOLATED")
    return variant


def compare_outputs(a_deck: Path, b_deck: Path, a_dat: Path, b_dat: Path,
                    a_frd: Path, b_frd: Path):
    if make_pair(a_deck.read_text(encoding="utf-8")) != b_deck.read_text(encoding="utf-8"):
        raise ValueError("ROTATION_AB_DECK_DIFF_NOT_ISOLATED")
    nodes, elems, edge, qa = parse_deck(a_deck)
    node_b, elem_b, edge_b, qb = parse_deck(b_deck)
    if nodes != node_b or elems != elem_b or edge != edge_b or qa != qb:
        raise ValueError("ROTATION_AB_INPUT_MODEL_CHANGED")
    original = a_deck.read_text(encoding="utf-8")
    if "synthetic aluminum clamped plate" not in original:
        raise ValueError("ROTATION_AB_FIXTURE_NOT_ALUMINUM")
    u_a = displacement_block(a_dat.read_text(errors="replace"), set(nodes))
    u_b = displacement_block(b_dat.read_text(errors="replace"), set(nodes))
    rf_a = rf_block(a_dat.read_text(errors="replace"), "NALL", set(nodes))
    rf_b = rf_block(b_dat.read_text(errors="replace"), "NALL", set(nodes))
    xyz_a, exp_a, du_a = read_expanded_frd(a_frd)
    xyz_b, exp_b, du_b = read_expanded_frd(b_frd)
    if xyz_a != xyz_b or exp_a != exp_b or set(du_a) != set(du_b):
        raise ValueError("ROTATION_AB_EXPANDED_MODEL_MISMATCH")
    def max_delta(x, y):
        return max(abs(x[n][c]-y[n][c]) for n in x for c in range(3))
    def max_mag(x,y):
        return max(1., *(abs(z) for dataset in (x,y) for triple in dataset.values() for z in triple))
    mu=max_delta(u_a,u_b)
    mf=max_delta(rf_a,rf_b)
    me=max_delta(du_a,du_b)
    results={"n_original":len(nodes),"n_expanded":len(du_a),
             "max_nall_displacement_difference_mm":mu,
             "max_nall_internal_force_difference_N":mf,
             "max_expanded_displacement_difference_mm":me,
             "nall_u_relative_difference":mu/max_mag(u_a,u_b),
             "nall_rf_relative_difference":mf/max_mag(rf_a,rf_b),
             "expanded_u_relative_difference":me/max_mag(du_a,du_b),
             "six_component_balance":"NOT_ADMITTED",
             "rotational_MPC_multiplier":"UNOBSERVED"}
    if any(not math.isfinite(v) for v in (mu,mf,me)):
        raise ValueError("NONFINITE_ROTATION_AB_DIFFERENCE")
    # This is a recorded finite comparison, not a tolerance-based PASS.
    results["observed_exact_text_invariance"] = mu == 0 and mf == 0 and me == 0
    return results


def main():
    for n in (4,8,16):
        base = Path(f"aluminum_large_{n}")
        pair = Path(f"aluminum_large_{n}_no_drilling")
        observed = compare_outputs(
            base/"panel.inp",pair/"panel.inp",
            base/"panel.dat",pair/"panel.dat",
            base/"panel.frd",pair/"panel.frd")
        print(f"aluminum n={n}: {observed}")
        print("ROTATION_AB_MEASURED_ONLY; SIX_COMPONENT_BALANCE_NOT_ADMITTED")
    print("STAGE23_DRILLING_AB_OBSERVATIONS_COMPLETE; GENERAL_GLOBAL_BALANCE_NOT_ADMITTED")


if __name__ == "__main__":
    main()
