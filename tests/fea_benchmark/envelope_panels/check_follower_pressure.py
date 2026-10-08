"""Independent deformed-mid-surface follower pressure diagnostic for synthetic S8R panels.

NOT exact CalculiX expanded C3D20R pressure-face reproduction. An
observed residual is a *diagnostic*, not a full-global-equilibrium gate.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

from check_pressure_equilibrium import GAUSS, WEIGHTS, parse_deck, read_edge_rf, shape


def gradients(xi: float, eta: float):
    """Analytic derivatives of the S8 serendipity shape functions."""
    dx = (
        (1 - eta) * (2 * xi + eta) / 4,
        (1 - eta) * (2 * xi - eta) / 4,
        (1 + eta) * (2 * xi + eta) / 4,
        (1 + eta) * (2 * xi - eta) / 4,
        -xi * (1 - eta),
        (1 - eta * eta) / 2,
        -xi * (1 + eta),
        -(1 - eta * eta) / 2,
    )
    dy = (
        (1 - xi) * (xi + 2 * eta) / 4,
        (1 + xi) * (-xi + 2 * eta) / 4,
        (1 + xi) * (xi + 2 * eta) / 4,
        (1 - xi) * (-xi + 2 * eta) / 4,
        -(1 - xi * xi) / 2,
        -(1 + xi) * eta,
        (1 - xi * xi) / 2,
        -(1 - xi) * eta,
    )
    return dx, dy


def displacement_block(source: str, expected: set[int]):
    """Strict final-time, exactly-once Cartesian translational NALL records."""
    pattern = (r"displacements \([^)]*\) for set NALL and time\s+([\d.Ee+-]+)\s+"
               r"((?:\s*\d+\s+[\d.Ee+-]+\s+[\d.Ee+-]+\s+[\d.Ee+-]+\s*\n)+)")
    matches = list(re.finditer(pattern, source, re.I))
    if not matches:
        raise ValueError("MISSING_NALL_DISPLACEMENTS")
    last = matches[-1]
    if abs(float(last.group(1)) - 1.0) > 1e-7:
        raise ValueError("NO_FINAL_NALL_TIME")
    displacements = {}
    for line in last.group(2).splitlines():
        columns = line.split()
        if not columns:
            continue
        if len(columns) != 4:
            raise ValueError("MALFORMED_NALL_DISPLACEMENTS")
        nid = int(columns[0]); xyz = tuple(float(c) for c in columns[1:])
        if nid in displacements or not all(math.isfinite(v) for v in xyz):
            raise ValueError("DUPLICATE_OR_NONFINITE_NALL")
        displacements[nid] = xyz
    if set(displacements) != expected:
        raise ValueError(f"NALL_COVERAGE_MISMATCH expected={len(expected)} got={len(displacements)}")
    return displacements


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def integrate_follower_mid_surface(nodes, elements, displacements, pressure):
    """q integral N_i (x_,xi cross x_,eta) dxi deta on deformed S8 mid surface.

    Includes three-dimensional follower components and consistent nodal loads.
    Positive shell pressure convention calibrated to Stage 9 +Z sign.
    """
    if set(displacements) != set(nodes) or not math.isfinite(pressure) or pressure <= 0:
        raise ValueError("INVALID_DEFORMATION_INPUT")
    xyz = {
        k: tuple(nodes[k][i] + displacements[k][i] for i in range(3))
        for k in nodes
    }
    if not all(math.isfinite(c) for p in xyz.values() for c in p):
        raise ValueError("NONFINITE_DEFORMATION")
    applied = {k: [0.0, 0.0, 0.0] for k in nodes}
    signed_force = [0.0, 0.0, 0.0]
    for element in elements:
        if len(element) != 8 or len(set(element)) != 8 or any(i not in xyz for i in element):
            raise ValueError("BAD_CONNECTIVITY")
        pos = [xyz[k] for k in element]
        for a, xi in enumerate(GAUSS):
            for b, eta in enumerate(GAUSS):
                n = shape(xi, eta)
                gx, gy = gradients(xi, eta)
                tx = [sum(gx[j]*pos[j][c] for j in range(8)) for c in range(3)]
                ty = [sum(gy[j]*pos[j][c] for j in range(8)) for c in range(3)]
                area_vector = cross(tx, ty)
                if area_vector[2] <= 0 or not all(math.isfinite(v) for v in area_vector):
                    raise ValueError("FOLDED_OR_INVALID_MID_SURFACE")
                increment = [pressure * WEIGHTS[a] * WEIGHTS[b] * component for component in area_vector]
                for c in range(3):
                    signed_force[c] += increment[c]
                for k, nk in zip(element, n):
                    for c in range(3):
                        applied[k][c] += nk * increment[c]
    reconstructed = [sum(v[c] for v in applied.values()) for c in range(3)]
    if any(abs(reconstructed[c]-signed_force[c]) > 1e-7 * max(1.0,abs(signed_force[2])) for c in range(3)):
        raise ValueError("FOLLOWER_INTEGRATION_NOT_CLOSED")
    return applied, signed_force


def diagnose(deck: Path, output: Path):
    nodes, elements, edge, pressure = parse_deck(deck)
    source = output.read_text(errors="replace")
    displacement = displacement_block(source, set(nodes))
    applied, total = integrate_follower_mid_surface(nodes, elements, displacement, pressure)
    raw = read_edge_rf(output, edge)
    boundary_applied = [sum(applied[k][i] for k in edge) for i in range(3)]
    corrected = [raw[i] - boundary_applied[i] for i in range(3)]
    residual = [corrected[i]+total[i] for i in range(3)]
    reference = math.sqrt(sum(x*x for x in total))
    if reference <= 0:
        raise ValueError("NO_FOLLOWER_LOAD")
    relative = math.sqrt(sum(x*x for x in residual)) / reference
    if not math.isfinite(relative):
        raise ValueError("NONFINITE_RESIDUAL")
    return dict(raw_rf=raw, midsurface_total=total, midsurface_edge_applied=boundary_applied,
                inferred_support=corrected, residual=residual, relative_residual=relative)


def main():
    for material in ("glass", "aluminum"):
        for n in (4, 8, 16):
            case = Path(f"{material}_large_{n}")
            result = diagnose(case / "panel.inp", case / "panel.dat")
            print(f"{material} n={n} {result} ")
            print("DEFORMED_MIDSURFACE_FOLLOWER_PRESSURE_DIAGNOSTIC_ONLY; GLOBAL_BALANCE_NOT_ADMITTED")
    print("FOLLOWER_PRESSURE_MIDSURFACE_DIAGNOSTICS_COMPLETE; NO_EXACT_SHELL_FACE_BALANCE_CLAIM")


if __name__ == "__main__":
    main()
