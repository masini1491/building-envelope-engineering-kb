import json
import unittest

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


CASE1_EXPECTED_C = {
    (0.1, 0.1): 0.3,
    (0.2, 0.1): 0.6,
    (0.3, 0.1): 0.8,
    (0.4, 0.1): 0.9,
    (0.1, 0.2): 0.7,
    (0.2, 0.2): 1.4,
    (0.3, 0.2): 1.8,
    (0.4, 0.2): 1.9,
    (0.1, 0.3): 1.3,
    (0.2, 0.3): 2.3,
    (0.3, 0.3): 3.0,
    (0.4, 0.3): 3.2,
    (0.1, 0.4): 2.0,
    (0.2, 0.4): 3.6,
    (0.3, 0.4): 4.7,
    (0.4, 0.4): 5.0,
    (0.1, 0.5): 3.2,
    (0.2, 0.5): 5.6,
    (0.3, 0.5): 7.0,
    (0.4, 0.5): 7.5,
    (0.1, 0.6): 5.3,
    (0.2, 0.6): 8.6,
    (0.3, 0.6): 10.3,
    (0.4, 0.6): 10.8,
    (0.1, 0.7): 9.7,
    (0.2, 0.7): 13.4,
    (0.3, 0.7): 14.7,
    (0.4, 0.7): 15.1,
}

CASE2_EXPECTED_C = {
    (0.0, 0.0475): 7.1,
    (0.0, 0.0415): 7.9,
    (0.0, 0.0365): 16.4,
    (0.0, 0.0): 16.8,
    (0.015, 0.0415): 6.3,
    (0.015, 0.0365): 16.3,
    (0.5, 0.0475): 0.8,
    (0.5, 0.0415): 0.8,
    (0.5, 0.0): 18.3,
}


@BilinearForm
def boundary_mass(u, v, _):
    return u * v


@LinearForm
def boundary_unit_load(v, _):
    return v


def _node_value(basis, values, x_m, y_m):
    matches = np.flatnonzero(
        np.isclose(basis.doflocs[0], x_m, atol=1e-12, rtol=0.0)
        & np.isclose(basis.doflocs[1], y_m, atol=1e-12, rtol=0.0)
    )
    if matches.size != 1:
        raise AssertionError(
            f"Expected one P1 node at ({x_m}, {y_m}), found {matches.size}"
        )
    return float(values[matches[0]])


class ThermalBridgeBackendProbeTests(unittest.TestCase):
    """Ephemeral P2 backend probe; this file is not a production solver."""

    def test_iso_10211_case1_public_benchmark(self):
        mesh = (
            MeshTri.init_tensor(
                np.linspace(0.0, 0.4, 81),
                np.linspace(0.0, 0.8, 161),
            )
            .with_boundaries(
                {
                    "cold_left": lambda x: np.isclose(x[0], 0.0),
                    "cold_bottom": lambda x: np.isclose(x[1], 0.0),
                    "hot_top": lambda x: np.isclose(x[1], 0.8),
                }
            )
        )
        basis = Basis(mesh, ElementTriP1())
        matrix = asm(laplace, basis)

        temperature = basis.zeros()
        temperature[basis.get_dofs("hot_top")] = 20.0
        prescribed = basis.get_dofs({"cold_left", "cold_bottom", "hot_top"})
        temperature = solve(*condense(matrix, x=temperature, D=prescribed))

        errors = {
            point: abs(_node_value(basis, temperature, *point) - expected)
            for point, expected in CASE1_EXPECTED_C.items()
        }
        max_error = max(errors.values())
        print(
            "P2_THERMAL_BACKEND_CASE1 "
            + json.dumps(
                {"max_temperature_error_c": max_error},
                sort_keys=True,
            )
        )
        self.assertLessEqual(max_error, 0.1)

    def test_iso_10211_case2_public_benchmark(self):
        x_coords = np.concatenate(
            [
                np.linspace(0.0, 0.015, 61),
                np.linspace(0.015, 0.05, 71)[1:],
                np.linspace(0.05, 0.5, 181)[1:],
            ]
        )
        y_coords = np.linspace(0.0, 0.0475, 191)

        mesh = (
            MeshTri.init_tensor(x_coords, y_coords)
            .with_boundaries(
                {
                    "bottom": lambda x: np.isclose(x[1], 0.0),
                    "top": lambda x: np.isclose(x[1], 0.0475),
                }
            )
        )
        element = ElementTriP1()
        basis = Basis(mesh, element)

        centroids = mesh.p[:, mesh.t].mean(axis=1)
        cx = centroids[0]
        cy = centroids[1]
        aluminum = (
            (cy < 0.0015)
            | ((cx < 0.0015) & (cy < 0.0365))
            | ((cx < 0.015) & (cy >= 0.0350) & (cy < 0.0365))
        )
        wood = (
            (~aluminum)
            & (cx < 0.015)
            & (cy >= 0.0365)
            & (cy < 0.0415)
        )
        concrete = (~aluminum) & (~wood) & (cy >= 0.0415)
        insulation = ~(aluminum | wood | concrete)

        materials = (
            (aluminum, 230.0),
            (wood, 0.12),
            (concrete, 1.15),
            (insulation, 0.029),
        )

        matrix = None
        for mask, conductivity in materials:
            sub_basis = Basis(mesh, element, elements=np.flatnonzero(mask))
            contribution = conductivity * asm(laplace, sub_basis)
            matrix = contribution if matrix is None else matrix + contribution

        bottom_basis = FacetBasis(
            mesh, element, facets=mesh.boundaries["bottom"]
        )
        top_basis = FacetBasis(mesh, element, facets=mesh.boundaries["top"])
        h_inside = 1.0 / 0.11
        h_outside = 1.0 / 0.06

        matrix = (
            matrix
            + h_inside * asm(boundary_mass, bottom_basis)
            + h_outside * asm(boundary_mass, top_basis)
        )
        load = (
            h_inside * 20.0 * asm(boundary_unit_load, bottom_basis)
            + h_outside * 0.0 * asm(boundary_unit_load, top_basis)
        )
        temperature = solve(matrix, load)

        temperature_errors = {
            point: abs(_node_value(basis, temperature, *point) - expected)
            for point, expected in CASE2_EXPECTED_C.items()
        }
        max_temperature_error = max(temperature_errors.values())

        bottom_nodes = np.flatnonzero(
            np.isclose(basis.doflocs[1], 0.0, atol=1e-12, rtol=0.0)
        )
        order = np.argsort(basis.doflocs[0, bottom_nodes])
        bottom_nodes = bottom_nodes[order]
        bottom_x = basis.doflocs[0, bottom_nodes]
        inward_flux = h_inside * (20.0 - temperature[bottom_nodes])
        heat_flow_w_per_m = float(np.trapezoid(inward_flux, bottom_x))
        heat_flow_relative_error = abs(heat_flow_w_per_m - 9.5) / 9.5

        print(
            "P2_THERMAL_BACKEND_CASE2 "
            + json.dumps(
                {
                    "heat_flow_relative_error": heat_flow_relative_error,
                    "heat_flow_w_per_m": heat_flow_w_per_m,
                    "max_temperature_error_c": max_temperature_error,
                },
                sort_keys=True,
            )
        )
        self.assertLessEqual(max_temperature_error, 0.1)
        self.assertLessEqual(heat_flow_relative_error, 0.001)


if __name__ == "__main__":
    unittest.main()
