"""Bounded 2D steady-state thermal-conduction kernel backed by scikit-fem.

This module owns a small backend-neutral engineering contract. It does not
select materials, infer boundary conditions, create CAD geometry, calculate
Psi-values/fRsi, or determine ISO 10211 project compliance.

The admitted numerical evidence is limited to the public ISO 10211:2017
Case 1 / Case 2 reproductions recorded by this repository.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
import math
from typing import Sequence


VALIDATION_SCOPE = "ISO_10211_2017_PUBLIC_CASE1_CASE2_BACKEND_REGRESSION"
ADMITTED_BACKEND_VERSIONS = {"scikit-fem": "12.0.2", "numpy": "2.5.3", "scipy": "1.18.1"}


class ThermalBridgeInputError(ValueError):
    """The supplied mesh/material/boundary contract is invalid or ambiguous."""


class ThermalBridgeBackendUnavailable(RuntimeError):
    """The optional thermal numerical backend is not available."""


@dataclass(frozen=True)
class FixedTemperatureBoundary:
    """Explicit Dirichlet boundary nodes.

    Corner discontinuities must be resolved by the caller. The same node may be
    repeated only when the prescribed temperature is exactly the same.
    """

    name: str
    node_indices: Sequence[int]
    temperature_c: float


@dataclass(frozen=True)
class SurfaceResistanceBoundary:
    """Explicit exterior edges with ambient temperature and surface resistance."""

    name: str
    edge_node_pairs: Sequence[tuple[int, int]]
    ambient_temperature_c: float
    surface_resistance_m2k_w: float


@dataclass(frozen=True)
class ThermalBridge2DResult:
    node_temperature_c: tuple[float, ...]
    boundary_heat_flow_w_per_m: dict[str, float]
    backend: dict[str, str]
    validation_scope: str
    compliance_status: str


def _load_backend():
    try:
        import numpy as np
        from skfem import (
            Basis,
            BilinearForm,
            ElementTriP1,
            FacetBasis,
            LinearForm,
            MeshTri,
            asm,
            condense,
            solve,
        )
        from skfem.models.poisson import laplace
    except ImportError as exc:
        raise ThermalBridgeBackendUnavailable(
            "2D thermal backend unavailable; install requirements/thermal-bridge.txt"
        ) from exc

    return {
        "np": np,
        "Basis": Basis,
        "BilinearForm": BilinearForm,
        "ElementTriP1": ElementTriP1,
        "FacetBasis": FacetBasis,
        "LinearForm": LinearForm,
        "MeshTri": MeshTri,
        "asm": asm,
        "condense": condense,
        "solve": solve,
        "laplace": laplace,
    }


def _finite_float(value: float, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ThermalBridgeInputError(f"{field} must be numeric") from exc
    if not math.isfinite(number):
        raise ThermalBridgeInputError(f"{field} must be finite")
    return number


def _name(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ThermalBridgeInputError(f"{field} must be a non-empty string")
    return value.strip()


def _int_index(value: int, field: str) -> int:
    if isinstance(value, bool):
        raise ThermalBridgeInputError(f"{field} must be an integer index")
    try:
        number = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ThermalBridgeInputError(f"{field} must be an integer index") from exc
    try:
        numeric = float(value)
    except (TypeError, ValueError, OverflowError):
        numeric = float(number)
    if not math.isfinite(numeric) or numeric != number:
        raise ThermalBridgeInputError(f"{field} must be an integer index")
    return number


def solve_steady_state_2d(
    *,
    points_m: Sequence[Sequence[float]],
    triangles: Sequence[Sequence[int]],
    conductivity_w_mk: Sequence[float],
    fixed_temperature_boundaries: Sequence[FixedTemperatureBoundary] = (),
    surface_resistance_boundaries: Sequence[SurfaceResistanceBoundary] = (),
) -> ThermalBridge2DResult:
    """Solve one edge-connected triangular 2D steady-state conduction model.

    Parameters are caller-confirmed numerical facts. The kernel validates
    connectivity, element degeneracy, duplicate/orphan vertices, manifold edge
    incidence, and explicit boundary references. Geometric conformity beyond
    those checks (for example no overlapping elements or T-junctions) remains a
    caller/mesh-generator responsibility:

    - ``points_m``: N x 2 node coordinates in metres.
    - ``triangles``: M x 3 zero-based node indices.
    - ``conductivity_w_mk``: one finite positive conductivity per triangle.
    - fixed-temperature boundaries: explicit boundary node indices.
    - surface-resistance boundaries: explicit exterior node-pair edges.

    Exterior edges not listed in a surface-resistance boundary are adiabatic
    unless their nodes are explicitly fixed. Heat-flow sign is positive from
    the boundary ambient into the modeled domain.

    The function returns numerical-backend evidence only. It does not establish
    a project-specific ISO 10211 compliance result.
    """

    backend = _load_backend()
    try:
        actual_versions = {package: metadata.version(package) for package in ADMITTED_BACKEND_VERSIONS}
    except metadata.PackageNotFoundError as exc:
        raise ThermalBridgeBackendUnavailable("thermal backend package metadata is unavailable") from exc
    if actual_versions != ADMITTED_BACKEND_VERSIONS:
        raise ThermalBridgeBackendUnavailable(
            f"unvalidated thermal backend versions: {actual_versions!r}; "
            f"expected {ADMITTED_BACKEND_VERSIONS!r}"
        )
    np = backend["np"]
    Basis = backend["Basis"]
    BilinearForm = backend["BilinearForm"]
    ElementTriP1 = backend["ElementTriP1"]
    FacetBasis = backend["FacetBasis"]
    LinearForm = backend["LinearForm"]
    MeshTri = backend["MeshTri"]
    asm = backend["asm"]
    condense = backend["condense"]
    solve = backend["solve"]
    laplace = backend["laplace"]

    try:
        points = np.asarray(points_m, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ThermalBridgeInputError("points_m must be numeric N x 2 coordinates") from exc
    if points.ndim != 2 or points.shape[1] != 2 or points.shape[0] < 3:
        raise ThermalBridgeInputError("points_m must have shape N x 2 with N >= 3")
    if not np.isfinite(points).all():
        raise ThermalBridgeInputError("points_m must contain only finite coordinates")

    try:
        triangle_raw = np.asarray(triangles, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ThermalBridgeInputError("triangles must be numeric M x 3 indices") from exc
    if triangle_raw.ndim != 2 or triangle_raw.shape[1] != 3 or triangle_raw.shape[0] < 1:
        raise ThermalBridgeInputError("triangles must have shape M x 3 with M >= 1")
    if not np.isfinite(triangle_raw).all() or not np.equal(
        triangle_raw, np.floor(triangle_raw)
    ).all():
        raise ThermalBridgeInputError("triangles must contain finite integer indices")
    triangle_array = triangle_raw.astype(int)
    if (triangle_array < 0).any() or (triangle_array >= points.shape[0]).any():
        raise ThermalBridgeInputError("triangle node index is outside points_m")
    if any(len(set(row.tolist())) != 3 for row in triangle_array):
        raise ThermalBridgeInputError("each triangle must reference three distinct nodes")

    canonical_triangles = [tuple(sorted(row.tolist())) for row in triangle_array]
    if len(set(canonical_triangles)) != len(canonical_triangles):
        raise ThermalBridgeInputError("duplicate triangles are not allowed")

    span = max(float(np.ptp(points[:, 0])), float(np.ptp(points[:, 1])), 1.0)
    area_tolerance = np.finfo(float).eps * span * span * 16.0
    for row in triangle_array:
        p0, p1, p2 = points[row]
        twice_area = abs(
            (p1[0] - p0[0]) * (p2[1] - p0[1])
            - (p1[1] - p0[1]) * (p2[0] - p0[0])
        )
        if not math.isfinite(float(twice_area)) or twice_area <= area_tolerance:
            raise ThermalBridgeInputError("triangles must have finite non-zero area")

    try:
        conductivity = np.asarray(conductivity_w_mk, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ThermalBridgeInputError("conductivity_w_mk must be numeric") from exc
    if conductivity.ndim != 1 or conductivity.shape[0] != triangle_array.shape[0]:
        raise ThermalBridgeInputError(
            "conductivity_w_mk must contain exactly one value per triangle"
        )
    if not np.isfinite(conductivity).all() or (conductivity <= 0.0).any():
        raise ThermalBridgeInputError(
            "conductivity_w_mk values must be finite and > 0"
        )

    edge_counts: dict[tuple[int, int], int] = {}
    edge_to_triangles: dict[tuple[int, int], list[int]] = {}
    for tri_index, row in enumerate(triangle_array):
        tri_edges = (
            tuple(sorted((int(row[0]), int(row[1])))),
            tuple(sorted((int(row[1]), int(row[2])))),
            tuple(sorted((int(row[2]), int(row[0])))),
        )
        for edge in tri_edges:
            edge_counts[edge] = edge_counts.get(edge, 0) + 1
            edge_to_triangles.setdefault(edge, []).append(tri_index)
    if any(count > 2 for count in edge_counts.values()):
        raise ThermalBridgeInputError("mesh must be manifold; an edge belongs to > 2 triangles")

    triangle_neighbors = [set() for _ in range(triangle_array.shape[0])]
    for members in edge_to_triangles.values():
        if len(members) == 2:
            left, right = members
            triangle_neighbors[left].add(right)
            triangle_neighbors[right].add(left)
    visited = {0}
    stack = [0]
    while stack:
        current = stack.pop()
        for neighbor in triangle_neighbors[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)
    if len(visited) != triangle_array.shape[0]:
        raise ThermalBridgeInputError("mesh triangles must form one edge-connected domain")

    exterior_edges = {edge for edge, count in edge_counts.items() if count == 1}
    exterior_nodes = {node for edge in exterior_edges for node in edge}

    fixed_by_node: dict[int, float] = {}
    boundary_names: set[str] = set()
    for boundary in fixed_temperature_boundaries:
        boundary_name = _name(boundary.name, "fixed boundary name")
        if boundary_name in boundary_names:
            raise ThermalBridgeInputError("boundary names must be unique")
        boundary_names.add(boundary_name)
        temperature = _finite_float(boundary.temperature_c, "temperature_c")
        if len(boundary.node_indices) == 0:
            raise ThermalBridgeInputError(
                f"fixed boundary {boundary_name!r} must contain at least one node"
            )
        for raw_node in boundary.node_indices:
            node = _int_index(raw_node, "fixed boundary node")
            if node < 0 or node >= points.shape[0]:
                raise ThermalBridgeInputError("fixed boundary node is outside points_m")
            if node not in exterior_nodes:
                raise ThermalBridgeInputError("fixed-temperature nodes must lie on mesh exterior")
            prior = fixed_by_node.get(node)
            if prior is not None and prior != temperature:
                raise ThermalBridgeInputError(
                    "a fixed-temperature node cannot have conflicting temperatures"
                )
            fixed_by_node[node] = temperature

    surface_specs: list[tuple[str, list[tuple[int, int]], float, float]] = []
    claimed_surface_edges: set[tuple[int, int]] = set()
    for boundary in surface_resistance_boundaries:
        boundary_name = _name(boundary.name, "surface boundary name")
        if boundary_name in boundary_names:
            raise ThermalBridgeInputError("boundary names must be unique")
        boundary_names.add(boundary_name)
        ambient = _finite_float(
            boundary.ambient_temperature_c, "ambient_temperature_c"
        )
        resistance = _finite_float(
            boundary.surface_resistance_m2k_w, "surface_resistance_m2k_w"
        )
        if resistance <= 0.0:
            raise ThermalBridgeInputError("surface_resistance_m2k_w must be > 0")
        if len(boundary.edge_node_pairs) == 0:
            raise ThermalBridgeInputError(
                f"surface boundary {boundary_name!r} must contain at least one edge"
            )
        normalized_edges: list[tuple[int, int]] = []
        for raw_edge in boundary.edge_node_pairs:
            try:
                edge_length = len(raw_edge)
            except TypeError as exc:
                raise ThermalBridgeInputError(
                    "surface boundary edges must contain two nodes"
                ) from exc
            if edge_length != 2:
                raise ThermalBridgeInputError("surface boundary edges must contain two nodes")
            left = _int_index(raw_edge[0], "surface boundary edge node")
            right = _int_index(raw_edge[1], "surface boundary edge node")
            if left == right:
                raise ThermalBridgeInputError("surface boundary edge nodes must differ")
            if left < 0 or right < 0 or left >= points.shape[0] or right >= points.shape[0]:
                raise ThermalBridgeInputError("surface boundary edge node is outside points_m")
            edge = tuple(sorted((left, right)))
            if edge not in exterior_edges:
                raise ThermalBridgeInputError(
                    "surface-resistance edges must be actual exterior mesh edges"
                )
            if edge in claimed_surface_edges:
                raise ThermalBridgeInputError(
                    "one exterior edge cannot belong to multiple surface-resistance boundaries"
                )
            if left in fixed_by_node and right in fixed_by_node:
                raise ThermalBridgeInputError(
                    "a full surface-resistance edge cannot also be fully fixed-temperature"
                )
            claimed_surface_edges.add(edge)
            normalized_edges.append(edge)
        surface_specs.append((boundary_name, normalized_edges, ambient, resistance))

    if not fixed_by_node and not surface_specs:
        raise ThermalBridgeInputError(
            "model requires fixed-temperature nodes or a surface-resistance boundary"
        )

    mesh = MeshTri(points.T, triangle_array.T)
    try:
        mesh.is_valid(raise_=True)
    except ValueError as exc:
        raise ThermalBridgeInputError(
            "mesh failed backend structural validation"
        ) from exc
    element = ElementTriP1()
    basis = Basis(mesh, element)

    @BilinearForm
    def material_laplace(u, v, w):
        return w.conductivity * (u.grad[0] * v.grad[0] + u.grad[1] * v.grad[1])

    matrix = asm(
        material_laplace,
        basis,
        conductivity=conductivity[:, None] * np.ones((1, basis.X.shape[1])),
    )

    @BilinearForm
    def boundary_mass(u, v, _):
        return u * v

    @LinearForm
    def boundary_unit_load(v, _):
        return v

    boundary_facet_by_edge = {
        tuple(sorted(int(node) for node in mesh.facets[:, facet_index])): int(facet_index)
        for facet_index in mesh.boundary_facets()
    }

    load = np.zeros(basis.N, dtype=float)
    surface_runtime: list[tuple[str, object, float, float]] = []
    for boundary_name, edges, ambient, resistance in surface_specs:
        facet_indices = np.array(
            [boundary_facet_by_edge[edge] for edge in edges], dtype=int
        )
        facet_basis = FacetBasis(mesh, element, facets=facet_indices)
        h_value = 1.0 / resistance
        matrix = matrix + h_value * asm(boundary_mass, facet_basis)
        load = load + h_value * ambient * asm(boundary_unit_load, facet_basis)
        surface_runtime.append((boundary_name, facet_basis, ambient, resistance))

    if fixed_by_node:
        prescribed = basis.zeros()
        dofs: list[int] = []
        for node, temperature in fixed_by_node.items():
            dof = int(basis.nodal_dofs[0, node])
            prescribed[dof] = temperature
            dofs.append(dof)
        temperature = solve(
            *condense(
                matrix,
                load,
                x=prescribed,
                D=np.asarray(sorted(set(dofs)), dtype=int),
            )
        )
    else:
        temperature = solve(matrix, load)

    if not np.isfinite(temperature).all():
        raise ThermalBridgeInputError("thermal solve returned non-finite temperatures")

    heat_flow: dict[str, float] = {}
    for boundary_name, facet_basis, ambient, resistance in surface_runtime:
        weights = asm(boundary_unit_load, facet_basis)
        h_value = 1.0 / resistance
        flow = h_value * (
            ambient * float(weights.sum()) - float(weights @ temperature)
        )
        heat_flow[boundary_name] = float(flow)

    skfem_version = actual_versions["scikit-fem"]
    numpy_version = actual_versions["numpy"]
    scipy_version = actual_versions["scipy"]

    return ThermalBridge2DResult(
        node_temperature_c=tuple(float(value) for value in temperature),
        boundary_heat_flow_w_per_m=heat_flow,
        backend={
            "engine": "scikit-fem",
            "scikit_fem_version": skfem_version,
            "numpy_version": numpy_version,
            "scipy_version": scipy_version,
        },
        validation_scope=VALIDATION_SCOPE,
        compliance_status="NUMERICAL_BACKEND_ONLY",
    )
