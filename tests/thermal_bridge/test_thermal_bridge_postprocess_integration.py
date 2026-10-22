"""End-to-end two-triangle slab: 1D analytic heat-flow reference.

k=1 W/(m K), slab thickness=1 m, indoor film R=1 m2 K/W,
Ti=20 C, Te=0 C; expected Ti surface=10 C,
q'=10 W/m, fRsi=0.5, L2D=0.5 W/(m K), Psi=0.
"""
import unittest

from scripts.engineering_calc.thermal_bridge_2d import (
    FixedTemperatureBoundary,
    SurfaceResistanceBoundary,
    solve_steady_state_2d,
)
from scripts.engineering_calc.thermal_bridge_postprocess import (
    compute_linear_transmittance_psi,
    compute_temperature_factor_frsi,
)


class ThermalPostprocessIntegrationTests(unittest.TestCase):
    def test_real_backend_analytic_slab(self):
        solved = solve_steady_state_2d(
            points_m=[(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)],
            triangles=[(0, 1, 2), (1, 3, 2)],
            conductivity_w_mk=[1.0, 1.0],
            fixed_temperature_boundaries=[
                FixedTemperatureBoundary("outdoor", [1, 3], 0.0)
            ],
            surface_resistance_boundaries=[
                SurfaceResistanceBoundary(
                    "indoor", [(0, 2)],
                    ambient_temperature_c=20.0,
                    surface_resistance_m2k_w=1.0,
                )
            ],
        )
        self.assertAlmostEqual(solved.boundary_heat_flow_w_per_m["indoor"], 10.0, places=8)
        factor = compute_temperature_factor_frsi(
            solved, interior_surface_node_indices=[0, 2],
            indoor_temperature_c=20.0, outdoor_temperature_c=0.0,
        )
        self.assertAlmostEqual(factor.minimum_surface_temperature_c, 10.0, places=8)
        self.assertAlmostEqual(factor.temperature_factor_frsi, 0.5, places=8)
        psi = compute_linear_transmittance_psi(
            solved, interior_heat_flow_boundary_names=["indoor"],
            indoor_temperature_c=20.0, outdoor_temperature_c=0.0,
            reference_u_length_pairs=[(0.5, 1.0)],
            dimension_reference="internal",
        )
        self.assertAlmostEqual(psi.coupling_coefficient_l2d_w_mk, 0.5, places=8)
        self.assertAlmostEqual(psi.linear_transmittance_psi_w_mk, 0.0, places=8)
        self.assertEqual(psi.engineering_acceptance, "NOT_ADMITTED")
