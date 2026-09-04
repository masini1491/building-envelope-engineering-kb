"""Linear-elastic 1D Euler-Bernoulli beam helpers for deterministic review.

Engineering authority remains in the corresponding knowledge pages. This module only
performs deterministic mathematics after the caller has selected the structural model.

Sign convention for ``solve_beam``:
- transverse displacement / force: positive upward
- rotation / nodal moment: positive counter-clockwise
- element UDL ``q``: positive upward

Use one consistent unit system, for example N, mm, MPa (= N/mm^2), mm^4.
"""

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class SimpleSpanUdlResult:
    reaction_each: float
    shear_max: float
    moment_max: float
    deflection_max: float


@dataclass(frozen=True)
class BeamElement:
    start: int
    end: int
    elastic_modulus: float
    inertia: float
    udl: float = 0.0


@dataclass(frozen=True)
class ElementEndForces:
    element_index: int
    start_shear: float
    start_moment: float
    end_shear: float
    end_moment: float


@dataclass(frozen=True)
class BeamResult:
    displacements: tuple[float, ...]
    rotations: tuple[float, ...]
    reactions: tuple[float | None, ...]
    reaction_moments: tuple[float | None, ...]
    element_end_forces: tuple[ElementEndForces, ...]


def simple_span_udl(*, span: float, line_load: float, elastic_modulus: float, inertia: float) -> SimpleSpanUdlResult:
    """Closed-form simple span with full-span uniform load.

    ``line_load`` may be signed; maxima are returned as magnitudes.
    """
    span = float(span)
    line_load = float(line_load)
    elastic_modulus = float(elastic_modulus)
    inertia = float(inertia)
    if span <= 0 or elastic_modulus <= 0 or inertia <= 0:
        raise ValueError("span, elastic_modulus and inertia must be > 0")

    reaction = line_load * span / 2.0
    moment = line_load * span**2 / 8.0
    deflection = 5.0 * line_load * span**4 / (384.0 * elastic_modulus * inertia)
    return SimpleSpanUdlResult(
        reaction_each=reaction,
        shear_max=abs(reaction),
        moment_max=abs(moment),
        deflection_max=abs(deflection),
    )


def _solve_linear_system(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    """Solve a dense linear system with partial pivoting."""
    n = len(rhs)
    if n == 0:
        return []
    a = [row[:] + [rhs_i] for row, rhs_i in zip(matrix, rhs)]
    scale = max((abs(value) for row in matrix for value in row), default=1.0)
    pivot_tol = max(scale * 1e-12, 1e-15)

    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(a[row][col]))
        if abs(a[pivot][col]) <= pivot_tol:
            raise ValueError("beam stiffness matrix is singular; check supports and releases")
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]

        pivot_value = a[col][col]
        for row in range(col + 1, n):
            factor = a[row][col] / pivot_value
            if factor == 0:
                continue
            for j in range(col, n + 1):
                a[row][j] -= factor * a[col][j]

    x = [0.0] * n
    for row in range(n - 1, -1, -1):
        subtotal = sum(a[row][j] * x[j] for j in range(row + 1, n))
        x[row] = (a[row][n] - subtotal) / a[row][row]
    return x


def _element_stiffness(elastic_modulus: float, inertia: float, length: float) -> list[list[float]]:
    factor = elastic_modulus * inertia / length**3
    l = length
    return [
        [12 * factor, 6 * l * factor, -12 * factor, 6 * l * factor],
        [6 * l * factor, 4 * l**2 * factor, -6 * l * factor, 2 * l**2 * factor],
        [-12 * factor, -6 * l * factor, 12 * factor, -6 * l * factor],
        [6 * l * factor, 2 * l**2 * factor, -6 * l * factor, 4 * l**2 * factor],
    ]


def _element_udl_vector(q: float, length: float) -> list[float]:
    """Consistent nodal load vector for a constant transverse UDL."""
    l = length
    return [q * l / 2.0, q * l**2 / 12.0, q * l / 2.0, -q * l**2 / 12.0]


def solve_beam(
    *,
    node_positions: Sequence[float],
    elements: Sequence[BeamElement],
    vertical_restraints: Iterable[int],
    rotational_restraints: Iterable[int] = (),
    nodal_forces: Mapping[int, float] | None = None,
    nodal_moments: Mapping[int, float] | None = None,
) -> BeamResult:
    """Solve a 1D Euler-Bernoulli beam by the direct-stiffness method.

    Each node has two DOF: transverse displacement and rotation. Elements may have
    different ``E``, ``I`` and constant UDL values. Point loads or moments must be
    applied at nodes; add a node at the load location when reviewing an arbitrary
    point load.

    The function returns nodal responses, support reactions, and element end actions.
    It does not select supports, infer splice rigidity, calculate allowable capacity,
    or issue an overall structural PASS.
    """
    positions = tuple(float(x) for x in node_positions)
    if len(positions) < 2:
        raise ValueError("at least two node positions are required")
    if any(not isfinite(x) for x in positions):
        raise ValueError("node positions must be finite")
    if any(b <= a for a, b in zip(positions, positions[1:])):
        raise ValueError("node positions must be strictly increasing")

    n = len(positions)
    ndof = 2 * n
    k_global = [[0.0] * ndof for _ in range(ndof)]
    load = [0.0] * ndof
    element_cache: list[tuple[list[list[float]], list[float], tuple[int, int, int, int]]] = []

    for element_index, element in enumerate(elements):
        if not (0 <= element.start < n and 0 <= element.end < n):
            raise ValueError(f"element {element_index} references an invalid node")
        if element.end <= element.start:
            raise ValueError(f"element {element_index} must run from a lower to a higher node index")
        if element.end != element.start + 1:
            raise ValueError("elements must connect adjacent nodes; insert explicit intermediate nodes")
        e = float(element.elastic_modulus)
        inertia = float(element.inertia)
        q = float(element.udl)
        if e <= 0 or inertia <= 0 or not all(isfinite(v) for v in (e, inertia, q)):
            raise ValueError("element elastic_modulus and inertia must be finite and > 0; udl must be finite")
        length = positions[element.end] - positions[element.start]
        k_local = _element_stiffness(e, inertia, length)
        f_local = _element_udl_vector(q, length)
        dofs = (2 * element.start, 2 * element.start + 1, 2 * element.end, 2 * element.end + 1)
        for i, gi in enumerate(dofs):
            load[gi] += f_local[i]
            for j, gj in enumerate(dofs):
                k_global[gi][gj] += k_local[i][j]
        element_cache.append((k_local, f_local, dofs))

    for node, force in (nodal_forces or {}).items():
        if not 0 <= node < n:
            raise ValueError("nodal force references an invalid node")
        force = float(force)
        if not isfinite(force):
            raise ValueError("nodal forces must be finite")
        load[2 * node] += force

    for node, moment in (nodal_moments or {}).items():
        if not 0 <= node < n:
            raise ValueError("nodal moment references an invalid node")
        moment = float(moment)
        if not isfinite(moment):
            raise ValueError("nodal moments must be finite")
        load[2 * node + 1] += moment

    vertical = set(vertical_restraints)
    rotational = set(rotational_restraints)
    if any(not 0 <= node < n for node in vertical | rotational):
        raise ValueError("restraint references an invalid node")

    constrained = {2 * node for node in vertical} | {2 * node + 1 for node in rotational}
    free = [dof for dof in range(ndof) if dof not in constrained]
    if not free:
        raise ValueError("beam has no free degrees of freedom")

    k_ff = [[k_global[i][j] for j in free] for i in free]
    f_f = [load[i] for i in free]
    d_f = _solve_linear_system(k_ff, f_f)

    displacement_vector = [0.0] * ndof
    for dof, value in zip(free, d_f):
        displacement_vector[dof] = value

    residual = [
        sum(k_global[i][j] * displacement_vector[j] for j in range(ndof)) - load[i]
        for i in range(ndof)
    ]
    reactions: list[float | None] = []
    reaction_moments: list[float | None] = []
    for node in range(n):
        reactions.append(residual[2 * node] if node in vertical else None)
        reaction_moments.append(residual[2 * node + 1] if node in rotational else None)

    end_forces: list[ElementEndForces] = []
    for element_index, (k_local, f_local, dofs) in enumerate(element_cache):
        d_local = [displacement_vector[dof] for dof in dofs]
        internal = [
            sum(k_local[i][j] * d_local[j] for j in range(4)) - f_local[i]
            for i in range(4)
        ]
        end_forces.append(
            ElementEndForces(
                element_index=element_index,
                start_shear=internal[0],
                start_moment=internal[1],
                end_shear=internal[2],
                end_moment=internal[3],
            )
        )

    return BeamResult(
        displacements=tuple(displacement_vector[0::2]),
        rotations=tuple(displacement_vector[1::2]),
        reactions=tuple(reactions),
        reaction_moments=tuple(reaction_moments),
        element_end_forces=tuple(end_forces),
    )
