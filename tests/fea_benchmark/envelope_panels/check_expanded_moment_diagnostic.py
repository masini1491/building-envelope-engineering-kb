"""Stage 20: expanded-node geometric torque observation, NOT six-DOF equilibrium.

This captures only the r x F part visible in CCX 2.21 expanded FRD.
It does not recover shell rotational reaction couples, MPC multipliers,
or independent support reactions. No six-component PASS gate is provided.
"""
from __future__ import annotations

import math
from pathlib import Path


def _triple(value):
    try:
        data = tuple(value)
    except TypeError as exc:
        raise ValueError("INVALID_MOMENT_VECTOR") from exc
    if len(data) != 3 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in data):
        raise ValueError("INVALID_MOMENT_VECTOR")
    return data


def force_and_geometric_moment(positions: dict, forces: dict, origin=(0., 0., 0.)):
    """Return sum F and sum[(current xyz - origin) x F] in Cartesian axes.

    `forces` must be actual nodal forces, not per-element forces with shared
    nodes counted more than once. The result is only a geometric r x F moment.
    """
    center = _triple(origin)
    if not positions or set(positions) != set(forces):
        raise ValueError("EXPANDED_MOMENT_NODE_COVERAGE_MISMATCH")
    force_items, moment_items = [[], [], []], [[], [], []]
    for nid in sorted(positions):
        p = _triple(positions[nid])
        f = _triple(forces[nid])
        r = tuple(p[axis] - center[axis] for axis in range(3))
        m = (r[1]*f[2] - r[2]*f[1],
             r[2]*f[0] - r[0]*f[2],
             r[0]*f[1] - r[1]*f[0])
        for axis in range(3):
            force_items[axis].append(f[axis])
            moment_items[axis].append(m[axis])
    result_f = tuple(math.fsum(values) for values in force_items)
    result_m = tuple(math.fsum(values) for values in moment_items)
    if not all(math.isfinite(v) for v in (*result_f, *result_m)):
        raise ValueError("NONFINITE_EXPANDED_RESULTANT")
    return result_f, result_m


def observe_case(deck: Path, frd: Path, dat: Path, material: str):
    """Observe real expanded r x F after Stage 18/19 force checks pass.

    Does not interpret the residual as a support reaction or moment couple.
    The actual rotational/MPC constraint sources remain unobserved.
    """
    from check_pressure_equilibrium import parse_deck
    from check_expanded_face import integrate_p1_expanded_face
    from check_expanded_frd import read_expanded_frd
    from check_rf_3d_projection import read_final_expanded_rf
    from check_reconstructed_pressure_balance import reconcile as check_stage19

    check_stage19(deck, frd, dat, material)
    _, original_elements, _, pressure = parse_deck(deck)
    xyz, elements, displacement = read_expanded_frd(frd)
    used = {n for conn in elements.values() for n in conn}
    if not used or set(xyz) != used or set(displacement) != used:
        raise ValueError("EXPANDED_MOMENT_GEOMETRY_COVERAGE_MISMATCH")
    actual = {n: tuple(xyz[n][a] + displacement[n][a] for a in range(3)) for n in used}
    internal = read_final_expanded_rf(frd, used)
    loads = {n: [0., 0., 0.] for n in used}
    if set(elements) != set(range(1, len(original_elements)+1)):
        raise ValueError("EXPANDED_MOMENT_ELEMENT_COVERAGE_MISMATCH")
    for eid in sorted(elements):
        conn = elements[eid]
        if len(conn) != 20:
            raise ValueError("NON_C3D20_MOMENT_ELEMENT")
        nodal, _ = integrate_p1_expanded_face([actual[n] for n in conn], pressure)
        for nid, f in zip(conn, nodal):
            for axis in range(3):
                loads[nid][axis] += f[axis]
    pressure_force, pressure_moment = force_and_geometric_moment(actual, loads)
    internal_force, internal_moment = force_and_geometric_moment(actual, internal)
    return {
        "observed_nodes": len(used),
        "origin_mm": (0., 0., 0.),
        "expanded_P1_force_N": pressure_force,
        "expanded_P1_r_cross_F_Nmm": pressure_moment,
        "expanded_internal_RF_force_N": internal_force,
        "expanded_internal_RF_r_cross_F_Nmm": internal_moment,
        "unpartitioned_geometric_residual_Nmm": tuple(
            internal_moment[i] - pressure_moment[i] for i in range(3)),
        "six_component_balance": "NOT_ADMITTED",
        "rotational_reaction_couples": "UNOBSERVED",
        "rotational_MPC_multipliers": "UNOBSERVED",
        "independent_support_reactions": "UNOBSERVED",
    }


def main():
    for material in ("glass", "aluminum"):
        for n in (4, 8, 16):
            case = Path(f"{material}_large_{n}")
            result = observe_case(case / "panel.inp", case / "panel.frd", case / "panel.dat", material)
            print(f"{material} n={n} {result}")
            print("EXPANDED_GEOMETRIC_MOMENT_OBSERVED; SIX_COMPONENT_BALANCE_NOT_ADMITTED")
    print("STAGE20_EXPANDED_MOMENT_DIAGNOSTIC_COMPLETE; GENERAL_GLOBAL_BALANCE_NOT_ADMITTED")


if __name__ == "__main__":
    main()
