"""Bounded CCX 2.21 C3D20R P1 quadratic-face pressure geometry oracle.

Input must be the actual expanded element's current 20 nodal coordinates
(reference + displacement), not the 8 S8R midsurface displacement records.
This is an independent, synthetic diagnostic, never a global-balance admission.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

# CCX 2.21 e_c3d_rhs.f ifaceq(:,1) (one-based expanded solid slots).
P1_FACE_SLOTS = (4, 3, 2, 1, 11, 10, 9, 12)
GAUSS = (-1.0 / math.sqrt(3.0), 1.0 / math.sqrt(3.0))


def _s8(xi: float, eta: float):
    """Eight-node serendipity shape functions and local derivatives."""
    one_x, plus_x = 1 - xi, 1 + xi
    one_y, plus_y = 1 - eta, 1 + eta
    values = (
        -one_x * one_y * (1 + xi + eta) / 4,
        -plus_x * one_y * (1 - xi + eta) / 4,
        -plus_x * plus_y * (1 - xi - eta) / 4,
        -one_x * plus_y * (1 + xi - eta) / 4,
        (1 - xi * xi) * one_y / 2,
        plus_x * (1 - eta * eta) / 2,
        (1 - xi * xi) * plus_y / 2,
        one_x * (1 - eta * eta) / 2,
    )
    dx = (
        one_y * (2 * xi + eta) / 4,
        one_y * (2 * xi - eta) / 4,
        plus_y * (2 * xi + eta) / 4,
        plus_y * (2 * xi - eta) / 4,
        -xi * one_y,
        (1 - eta * eta) / 2,
        -xi * plus_y,
        -(1 - eta * eta) / 2,
    )
    dy = (
        one_x * (xi + 2 * eta) / 4,
        plus_x * (-xi + 2 * eta) / 4,
        plus_x * (xi + 2 * eta) / 4,
        one_x * (-xi + 2 * eta) / 4,
        -(1 - xi * xi) / 2,
        -plus_x * eta,
        (1 - xi * xi) / 2,
        -one_x * eta,
    )
    return values, dx, dy


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def integrate_p1_expanded_face(current_xyz: Sequence[Sequence[float]], pressure: float):
    """Integrate solver-sign-equivalent pressure force on explicit P1 face.

    Returns (20-slot nodal force tuple, 3D force resultant). Assumes C3D20R
    connectivity matches CCX ifaceq, strictly uses 2x2 quadrature and the
    negative of the oriented face Jacobian, as in e_c3d_rhs.f:544-549.
    No midsurface-to-expanded coordinate reconstruction is performed.
    """
    if len(current_xyz) != 20 or not math.isfinite(pressure) or pressure <= 0:
        raise ValueError("INVALID_EXPANDED_FACE_INPUT")
    if any(len(p) != 3 or not all(math.isfinite(v) for v in p) for p in current_xyz):
        raise ValueError("INVALID_EXPANDED_FACE_COORDINATES")
    face = [current_xyz[k - 1] for k in P1_FACE_SLOTS]
    nodal = [[0.0, 0.0, 0.0] for _ in range(20)]
    total = [0.0, 0.0, 0.0]
    reference_normal = _cross(tuple(face[1][c] - face[0][c] for c in range(3)),
                              tuple(face[3][c] - face[0][c] for c in range(3)))
    reference_norm = math.sqrt(sum(v * v for v in reference_normal))
    if reference_norm <= 1e-12:
        raise ValueError("DEGENERATE_P1_FACE")
    for xi in GAUSS:
        for eta in GAUSS:
            n, dx, dy = _s8(xi, eta)
            dx_position = tuple(sum(dx[j] * face[j][c] for j in range(8)) for c in range(3))
            dy_position = tuple(sum(dy[j] * face[j][c] for j in range(8)) for c in range(3))
            jacobian = _cross(dx_position, dy_position)
            magnitude = math.sqrt(sum(v * v for v in jacobian))
            if magnitude <= 1e-12 or sum(jacobian[c] * reference_normal[c] for c in range(3)) <= 0:
                raise ValueError("FOLDED_OR_DEGENERATE_P1_FACE")
            force = [-pressure * v for v in jacobian]
            for c in range(3):
                total[c] += force[c]
            for shape_weight, slot in zip(n, P1_FACE_SLOTS):
                for c in range(3):
                    nodal[slot - 1][c] += shape_weight * force[c]
    if any(abs(sum(row[c] for row in nodal) - total[c]) >
           1e-10 * max(1.0, *(abs(v) for v in total)) for c in range(3)):
        raise ValueError("P1_NODAL_RESULTANT_MISMATCH")
    return tuple(tuple(v) for v in nodal), tuple(total)
