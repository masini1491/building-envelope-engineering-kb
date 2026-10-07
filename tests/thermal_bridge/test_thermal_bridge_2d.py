import unittest
from unittest.mock import patch

import numpy as np
from skfem import MeshTri

from scripts.engineering_calc.thermal_bridge_2d import (
    FixedTemperatureBoundary,
    SurfaceResistanceBoundary,
    ThermalBridgeBackendUnavailable,
    ThermalBridgeInputError,
    VALIDATION_SCOPE,
    solve_steady_state_2d,
)


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


def node_at(mesh, x, y):
    matches = np.flatnonzero(
        np.isclose(mesh.p[0], x, atol=1e-12, rtol=0.0)
        & np.isclose(mesh.p[1], y, atol=1e-12, rtol=0.0)
    )
    if matches.size != 1:
        raise AssertionError(f"Expected one node at ({x}, {y}), found {matches.size}")
    return int(matches[0])


def horizontal_boundary_edges(mesh, y):
    result = []
    for facet in mesh.boundary_facets():
        nodes = [int(value) for value in mesh.facets[:, facet]]
        if all(np.isclose(mesh.p[1, node], y, atol=1e-12, rtol=0.0) for node in nodes):
            result.append(tuple(nodes))
    return result


class ThermalBridge2DTests(unittest.TestCase):
    def test_iso_10211_case1_via_production_kernel(self):
        mesh = MeshTri.init_tensor(
            np.linspace(0.0, 0.4, 81),
            np.linspace(0.0, 0.8, 161),
        )
        points = mesh.p.T.tolist()
        triangles = mesh.t.T.tolist()
        conductivity = [1.0] * len(triangles)

        # ISO/COMSOL Case 1 has a temperature discontinuity at the top-left
        # corner. Resolve that node explicitly as 20 C instead of relying on
        # implicit boundary precedence inside the kernel.
        left_cold = [
            index
            for index in range(mesh.p.shape[1])
            if np.isclose(mesh.p[0, index], 0.0)
            and not np.isclose(mesh.p[1, index], 0.8)
        ]
        bottom_cold = [
            index
            for index in range(mesh.p.shape[1])
            if np.isclose(mesh.p[1, index], 0.0)
        ]
        top_hot = [
            index
            for index in range(mesh.p.shape[1])
            if np.isclose(mesh.p[1, index], 0.8)
        ]

        result = solve_steady_state_2d(
            points_m=points,
            triangles=triangles,
            conductivity_w_mk=conductivity,
            fixed_temperature_boundaries=[
                FixedTemperatureBoundary("left-cold", left_cold, 0.0),
                FixedTemperatureBoundary("bottom-cold", bottom_cold, 0.0),
                FixedTemperatureBoundary("top-hot", top_hot, 20.0),
            ],
        )

        max_error = 0.0
        for point, expected in CASE1_EXPECTED_C.items():
            actual = result.node_temperature_c[node_at(mesh, *point)]
            max_error = max(max_error, abs(actual - expected))
        print(f"P2_THERMAL_KERNEL_CASE1 max_temperature_error_c={max_error:.12f}")
        self.assertLessEqual(max_error, 0.1)
        self.assertEqual(result.boundary_heat_flow_w_per_m, {})
        self.assertEqual(result.validation_scope, VALIDATION_SCOPE)
        self.assertEqual(result.compliance_status, "NUMERICAL_BACKEND_ONLY")

    def test_iso_10211_case2_via_production_kernel(self):
        x_coords = np.concatenate(
            [
                np.linspace(0.0, 0.015, 61),
                np.linspace(0.015, 0.05, 71)[1:],
                np.linspace(0.05, 0.5, 181)[1:],
            ]
        )
        y_coords = np.linspace(0.0, 0.0475, 191)
        mesh = MeshTri.init_tensor(x_coords, y_coords)
        points = mesh.p.T.tolist()
        triangles = mesh.t.T.tolist()

        conductivity = []
        for tri in mesh.t.T:
            centroid_x = float(mesh.p[0, tri].mean())
            centroid_y = float(mesh.p[1, tri].mean())
            aluminum = (
                centroid_y < 0.0015
                or (centroid_x < 0.0015 and centroid_y < 0.0365)
                or (
                    centroid_x < 0.015
                    and centroid_y >= 0.0350
                    and centroid_y < 0.0365
                )
            )
            wood = (
                not aluminum
                and centroid_x < 0.015
                and centroid_y >= 0.0365
                and centroid_y < 0.0415
            )
            concrete = (
                not aluminum and not wood and centroid_y >= 0.0415
            )
            if aluminum:
                conductivity.append(230.0)
            elif wood:
                conductivity.append(0.12)
            elif concrete:
                conductivity.append(1.15)
            else:
                conductivity.append(0.029)

        result = solve_steady_state_2d(
            points_m=points,
            triangles=triangles,
            conductivity_w_mk=conductivity,
            surface_resistance_boundaries=[
                SurfaceResistanceBoundary(
                    "inside",
                    horizontal_boundary_edges(mesh, 0.0),
                    ambient_temperature_c=20.0,
                    surface_resistance_m2k_w=0.11,
                ),
                SurfaceResistanceBoundary(
                    "outside",
                    horizontal_boundary_edges(mesh, 0.0475),
                    ambient_temperature_c=0.0,
                    surface_resistance_m2k_w=0.06,
                ),
            ],
        )

        max_error = 0.0
        for point, expected in CASE2_EXPECTED_C.items():
            actual = result.node_temperature_c[node_at(mesh, *point)]
            max_error = max(max_error, abs(actual - expected))

        heat_flow = result.boundary_heat_flow_w_per_m["inside"]
        relative_error = abs(heat_flow - 9.5) / 9.5
        print(
            "P2_THERMAL_KERNEL_CASE2 "
            f"max_temperature_error_c={max_error:.12f} "
            f"heat_flow_w_per_m={heat_flow:.12f} "
            f"heat_flow_relative_error={relative_error:.12f}"
        )
        self.assertLessEqual(max_error, 0.1)
        self.assertLessEqual(relative_error, 0.001)
        self.assertEqual(result.backend["scikit_fem_version"], "12.0.2")
        self.assertEqual(result.backend["numpy_version"], "2.5.3")
        self.assertEqual(result.backend["scipy_version"], "1.18.1")

    def test_rejects_conflicting_fixed_temperature_corner(self):
        points = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        triangles = [(0, 1, 2), (0, 2, 3)]
        with self.assertRaises(ThermalBridgeInputError):
            solve_steady_state_2d(
                points_m=points,
                triangles=triangles,
                conductivity_w_mk=[1.0, 1.0],
                fixed_temperature_boundaries=[
                    FixedTemperatureBoundary("cold", [0], 0.0),
                    FixedTemperatureBoundary("hot", [0], 20.0),
                ],
            )

    def test_rejects_interior_surface_resistance_edge(self):
        points = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        triangles = [(0, 1, 2), (0, 2, 3)]
        with self.assertRaises(ThermalBridgeInputError):
            solve_steady_state_2d(
                points_m=points,
                triangles=triangles,
                conductivity_w_mk=[1.0, 1.0],
                surface_resistance_boundaries=[
                    SurfaceResistanceBoundary("bad", [(0, 2)], 20.0, 0.11)
                ],
            )

    def test_rejects_nonpositive_conductivity(self):
        with self.assertRaises(ThermalBridgeInputError):
            solve_steady_state_2d(
                points_m=[(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)],
                triangles=[(0, 1, 2)],
                conductivity_w_mk=[0.0],
                fixed_temperature_boundaries=[
                    FixedTemperatureBoundary("anchor", [0, 1], 0.0)
                ],
            )

    def test_rejects_disconnected_mesh(self):
        points = [
            (0.0, 0.0),
            (1.0, 0.0),
            (0.0, 1.0),
            (3.0, 0.0),
            (4.0, 0.0),
            (3.0, 1.0),
        ]
        with self.assertRaises(ThermalBridgeInputError):
            solve_steady_state_2d(
                points_m=points,
                triangles=[(0, 1, 2), (3, 4, 5)],
                conductivity_w_mk=[1.0, 1.0],
                fixed_temperature_boundaries=[
                    FixedTemperatureBoundary("anchor", [0, 1], 0.0)
                ],
            )

    def test_backend_unavailable_is_explicit(self):
        with patch(
            "scripts.engineering_calc.thermal_bridge_2d._load_backend",
            side_effect=ThermalBridgeBackendUnavailable("missing"),
        ):
            with self.assertRaises(ThermalBridgeBackendUnavailable):
                solve_steady_state_2d(
                    points_m=[(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)],
                    triangles=[(0, 1, 2)],
                    conductivity_w_mk=[1.0],
                    fixed_temperature_boundaries=[
                        FixedTemperatureBoundary("anchor", [0, 1], 0.0)
                    ],
                )


if __name__ == "__main__":
    unittest.main()
