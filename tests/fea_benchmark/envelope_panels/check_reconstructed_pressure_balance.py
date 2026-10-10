"""Bounded Cartesian force balance for synthetic CCX 2.21 NLGEOM S8R plates.

The 3D expanded-face pressure is independently integrated from real FRD
coordinates then projected to original shell nodes. Printed NALL RF is an
INTERNAL nodal force, not a support reaction. At constrained translations
only, inferred support = internal - external pressure.

NOT a separate reaction measurement, a moment/MPC audit, or capacity approval.
"""
from __future__ import annotations

import math
from pathlib import Path

from audit_rf_projection import rf_block
from check_expanded_face import integrate_p1_expanded_face
from check_expanded_frd import read_expanded_frd
from check_pressure_equilibrium import parse_deck
from check_rf_3d_projection import project_expanded_rf, reconcile as check_rf_projection

FREE_REL_TOL = 1e-7
GLOBAL_REL_TOL = 5e-7


def constrained_translations(source: str, nodes: dict, edge: set, material: str):
    """Require the exact known *BOUNDARY contract from synthetic generate.py.

    Aluminum rotational DOFs 4..6 are NOT covered by this force-only audit.
    """
    if material not in ("glass", "aluminum") or not nodes or not edge:
        raise ValueError("UNSUPPORTED_MATERIAL_OR_NODES")
    if f"synthetic {material} " not in source:
        raise ValueError("FIXTURE_MATERIAL_MISMATCH")
    xmin, xmax = min(v[0] for v in nodes.values()), max(v[0] for v in nodes.values())
    ymin = min(v[1] for v in nodes.values())
    corners = [[nid for nid, pos in nodes.items() if pos[0] == x and pos[1] == ymin]
               for x in (xmin, xmax)]
    if any(len(c) != 1 for c in corners):
        raise ValueError("AMBIGUOUS_PIN_COORDINATES")
    if material == "aluminum":
        expected = {("EDGE", 1, 6, 0.0)}
    else:
        expected = {("EDGE", 3, 3, 0.0),
                    (str(corners[0][0]), 1, 2, 0.0),
                    (str(corners[1][0]), 2, 2, 0.0)}
    observed = []
    boundary = False
    for line in source.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("**"):
            continue
        if stripped.startswith("*"):
            boundary = stripped.upper().replace(" ", "") == "*BOUNDARY"
            continue
        if not boundary:
            continue
        fields = [s.strip() for s in stripped.split(",")]
        if len(fields) != 4:
            raise ValueError("INVALID_FIXTURE_BOUNDARY")
        try:
            row = (fields[0].upper() if fields[0].upper() == "EDGE" else str(int(fields[0])),
                   int(fields[1]), int(fields[2]), float(fields[3]))
        except ValueError as exc:
            raise ValueError("INVALID_FIXTURE_BOUNDARY") from exc
        if not math.isfinite(row[3]):
            raise ValueError("INVALID_FIXTURE_BOUNDARY")
        observed.append(row)
    if len(observed) != len(expected) or set(observed) != expected:
        raise ValueError("UNSUPPORTED_BOUNDARY_CONFIGURATION")
    if material == "aluminum":
        constrained = {(nid, component) for nid in edge for component in range(3)}
    else:
        constrained = {(nid, 2) for nid in edge}
        constrained.update({(corners[0][0], 0), (corners[0][0], 1), (corners[1][0], 1)})
    if any(nid not in nodes or component not in (0, 1, 2) for nid, component in constrained):
        raise ValueError("INVALID_CONSTRAINED_TRANSLATION")
    return constrained


def reconstruct_projected_pressure(original_elements, expanded_elements, coordinates, displacement, pressure):
    """Compute exact P1 surface nodal forces, then source-grounded 3D→S8R map."""
    if not original_elements or not math.isfinite(pressure) or pressure <= 0:
        raise ValueError("INVALID_RECONSTRUCTION_INPUT")
    used = {nid for element in expanded_elements.values() for nid in element}
    if not used or set(coordinates) != used or set(displacement) != used:
        raise ValueError("EXPANDED_COORDINATE_COVERAGE_MISMATCH")
    expanded_load = {nid: [0.0, 0.0, 0.0] for nid in used}
    applied = [0.0, 0.0, 0.0]
    for eid in sorted(expanded_elements):
        node_ids = expanded_elements[eid]
        if len(node_ids) != 20:
            raise ValueError("NON_C3D20_PRESSURE_ELEMENT")
        current = [tuple(coordinates[n][axis] + displacement[n][axis] for axis in range(3))
                   for n in node_ids]
        element_forces, element_total = integrate_p1_expanded_face(current, pressure)
        for axis in range(3):
            applied[axis] += element_total[axis]
        for node, force in zip(node_ids, element_forces):
            for axis in range(3):
                expanded_load[node][axis] += force[axis]
    shell_load, _ = project_expanded_rf(
        original_elements, expanded_elements,
        {nid: tuple(force) for nid, force in expanded_load.items()})
    if any(abs(sum(v[axis] for v in shell_load.values()) - applied[axis]) >
           1e-9 * max(1.0, abs(applied[2])) for axis in range(3)):
        raise ValueError("PRESSURE_NODE_PROJECTION_NOT_CLOSED")
    return shell_load, tuple(applied)


def assess_reconstructed_translational_balance(shell_load: dict, internal_rf: dict,
                                                 constrained: set, total_pressure: tuple):
    """Require free-DOF residuals and pressure+inferred-support resultant closure."""
    if not shell_load or set(shell_load) != set(internal_rf):
        raise ValueError("NALL_INTERNAL_PRESSURE_COVERAGE_MISMATCH")
    dofs = {(nid, comp) for nid in shell_load for comp in range(3)}
    if not constrained or not constrained < dofs:
        raise ValueError("INCOMPLETE_OR_INVALID_CONSTRAINT_COVERAGE")
    if len(total_pressure) != 3 or not all(math.isfinite(v) for v in total_pressure):
        raise ValueError("NONFINITE_PRESSURE_TOTAL")
    if any(len(values) != 3 or not all(math.isfinite(v) for v in values)
           for loads in (shell_load, internal_rf) for values in loads.values()):
        raise ValueError("NONFINITE_NODE_FORCE")
    external = tuple(math.fsum(v[axis] for v in shell_load.values()) for axis in range(3))
    pressure_scale = math.sqrt(math.fsum(x*x for x in total_pressure))
    if pressure_scale <= 0 or total_pressure[2] <= 0:
        raise ValueError("NONPOSITIVE_PRESSURE_SCALE")
    if any(abs(external[axis] - total_pressure[axis]) > 1e-9 * pressure_scale for axis in range(3)):
        raise ValueError("INCONSISTENT_PRESSURE_RESULTANT")
    residual = {(nid, axis): internal_rf[nid][axis] - shell_load[nid][axis]
                for nid, axis in dofs}
    free = dofs - constrained
    max_free = max(abs(residual[key]) for key in free)
    support = tuple(math.fsum(residual[(nid, axis)] for nid, comp in constrained if comp == axis)
                    for axis in range(3))
    global_residual = tuple(total_pressure[axis] + support[axis] for axis in range(3))
    global_norm = math.sqrt(math.fsum(x*x for x in global_residual))
    if max_free / pressure_scale > FREE_REL_TOL:
        raise ValueError(f"FREE_TRANSLATION_RESIDUAL_FAIL max={max_free:.8g} scale={pressure_scale:.8g}")
    if global_norm / pressure_scale > GLOBAL_REL_TOL:
        raise ValueError(f"CARTESIAN_RESULTANT_BALANCE_FAIL norm={global_norm:.8g} scale={pressure_scale:.8g}")
    return dict(pressure=total_pressure, reconstructed_support=support,
                residual=global_residual, relative_global_residual=global_norm / pressure_scale,
                relative_max_free_residual=max_free / pressure_scale,
                free_translations=len(free), constrained_translations=len(constrained))


def reconcile(deck: Path, frd: Path, dat: Path, material: str):
    nodes, elements, edge, pressure = parse_deck(deck)
    constraints = constrained_translations(deck.read_text(), nodes, edge, material)
    coordinates, expanded, displacement = read_expanded_frd(frd)
    shell_load, total = reconstruct_projected_pressure(
        elements, expanded, coordinates, displacement, pressure)
    if set(shell_load) != set(nodes):
        raise ValueError("UNMAPPED_ORIGINAL_SHELL_NODE")
    # Require Stage 18 source-projection evidence first; FRD and NALL RF must
    # remain consistent before interpreting the printed internal nodal force.
    check_rf_projection(deck, frd, dat)
    internal = rf_block(dat.read_text(errors="replace"), "NALL", set(nodes))
    return assess_reconstructed_translational_balance(shell_load, internal, constraints, total)


def main():
    for material in ("glass", "aluminum"):
        for n in (4, 8, 16):
            folder = Path(f"{material}_large_{n}")
            result = reconcile(folder / "panel.inp", folder / "panel.frd", folder / "panel.dat", material)
            print(f"{material} n={n} {result}")
            print("RECONSTRUCTED_TRANSLATIONAL_BALANCE_BOUNDED_PASS; MOMENT_AND_MPC_REACTION_NOT_ADMITTED")
    print("SYNTHETIC_P1_TRANSLATIONAL_BALANCE_DIAGNOSTICS_PASS; GENERAL_GLOBAL_BALANCE_NOT_ADMITTED")


if __name__ == "__main__":
    main()
