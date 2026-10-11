"""Stage 21: required residual couple after reconstructed translational supports.

A synthetic-only, bounded MOMENT-OBSERVABILITY DIAGNOSTIC, not a six-DOF
reaction solver. Rotational constraints, shell directors and MPC multipliers
are not measured; a near-zero required couple is not full equilibrium PASS.
"""
from __future__ import annotations

import math
from pathlib import Path

from audit_rf_projection import rf_block
from check_expanded_frd import read_expanded_frd
from check_expanded_moment_diagnostic import (
    force_and_geometric_moment, observe_case as observe_expanded_moment)
from check_follower_pressure import displacement_block
from check_pressure_equilibrium import parse_deck
from check_reconstructed_pressure_balance import (
    assess_reconstructed_translational_balance, constrained_translations,
    reconstruct_projected_pressure)


def required_unobserved_couple(positions: dict, shell_load: dict, internal_rf: dict,
                               constrained: set, pressure_force: tuple,
                               pressure_moment: tuple, origin=(0., 0., 0.)):
    """Resolve only the known translational-support geometric moment.

    Constrained nodal translational residual = internal RF - P1 nodal force,
    as admitted for this synthetic fixture in Stage 19. This is not an
    independently measured support reaction. A nonzero residual moment is
    a REQUIRED, not observed, additional couple if global balance holds.
    """
    if not positions or set(positions) != set(shell_load):
        raise ValueError("SHELL_SUPPORT_POSITION_COVERAGE_MISMATCH")
    if len(pressure_moment) != 3 or not all(
            isinstance(x, (int, float)) and math.isfinite(x) for x in pressure_moment):
        raise ValueError("INVALID_PRESSURE_MOMENT")
    trans = assess_reconstructed_translational_balance(
        shell_load, internal_rf, constrained, pressure_force)
    supported = {
        nid: tuple((internal_rf[nid][axis] - shell_load[nid][axis])
                   if (nid, axis) in constrained else 0.0 for axis in range(3))
        for nid in shell_load
    }
    support_force, support_moment = force_and_geometric_moment(
        positions, supported, origin)
    needed = tuple(-math.fsum((pressure_moment[i], support_moment[i]))
                   for i in range(3))
    if not all(math.isfinite(x) for x in needed):
        raise ValueError("NONFINITE_REQUIRED_COUPLE")
    return {
        "pressure_geometric_moment_Nmm": tuple(pressure_moment),
        "reconstructed_translation_support_N": support_force,
        "translation_support_r_cross_F_Nmm": support_moment,
        "required_unobserved_couple_if_equilibrium_Nmm": needed,
        "translation_resultant_relative_residual": trans["relative_global_residual"],
        "six_component_balance": "NOT_ADMITTED",
        "original_shell_rotational_reaction": "UNOBSERVED",
        "MPC_constraint_couple": "UNOBSERVED",
        "independent_support_measurement": "UNOBSERVED",
    }


def observe_case(deck: Path, frd: Path, dat: Path, material: str):
    """Require existing real-FRD Stage 20/19 gates first; do not infer MPC DOFs."""
    stage20 = observe_expanded_moment(deck, frd, dat, material)
    nodes, elements, edge, pressure = parse_deck(deck)
    source = deck.read_text(encoding="utf-8")
    constrained = constrained_translations(source, nodes, edge, material)
    coords, expanded, displacement = read_expanded_frd(frd)
    shell_load, total = reconstruct_projected_pressure(
        elements, expanded, coords, displacement, pressure)
    if set(shell_load) != set(nodes):
        raise ValueError("UNMAPPED_SHELL_SUPPORT_NODES")
    scale = math.sqrt(math.fsum(x*x for x in total))
    if scale <= 0 or any(
            abs(total[i] - stage20["expanded_P1_force_N"][i]) > 1e-9*scale
            for i in range(3)):
        raise ValueError("STAGE20_P1_FORCE_INCONSISTENT")
    dat_text = dat.read_text(errors="replace")
    original_u = displacement_block(dat_text, set(nodes))
    current_shell_positions = {
        nid: tuple(nodes[nid][i] + original_u[nid][i] for i in range(3))
        for nid in nodes
    }
    internal = rf_block(dat_text, "NALL", set(nodes))
    result = required_unobserved_couple(
        current_shell_positions, shell_load, internal, constrained, total,
        stage20["expanded_P1_r_cross_F_Nmm"])
    result["model"] = material
    result["nodes"] = len(nodes)
    result["constrained_translation_dofs"] = len(constrained)
    result["shell_support_arm_basis"] = "ORIGINAL_S8R_NODE_CURRENT_NALL_U"
    result["P1_moment_basis"] = "EXPANDED_C3D20_FACE_CURRENT_U"
    return result


def main():
    for material in ("glass", "aluminum"):
        for n in (4, 8, 16):
            case = Path(f"{material}_large_{n}")
            result = observe_case(case / "panel.inp", case / "panel.frd", case / "panel.dat", material)
            print(f"{material} n={n} {result}")
            print("TRANSLATION_SUPPORT_MOMENT_DIAGNOSTIC_ONLY; SIX_COMPONENT_BALANCE_NOT_ADMITTED")
    print("STAGE21_REQUIRED_COUPLE_DIAGNOSTIC_COMPLETE; GENERAL_GLOBAL_BALANCE_NOT_ADMITTED")


if __name__ == "__main__":
    main()
