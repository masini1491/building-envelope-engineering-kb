import unittest

from scripts.engineering_calc.thermal_bridge_2d import (
    ThermalBridge2DResult,
    ThermalBridgeInputError,
    VALIDATION_SCOPE,
)
from scripts.engineering_calc.thermal_bridge_postprocess import (
    compute_temperature_factor_frsi,
    compute_linear_transmittance_psi,
)


def synthetic_result(temperatures=(15.0, 12.0, 17.0), flows=None):
    return ThermalBridge2DResult(
        node_temperature_c=temperatures,
        boundary_heat_flow_w_per_m={"inside": 20.0, "extra": 10.0} if flows is None else flows,
        backend={"engine": "fixture"}, validation_scope=VALIDATION_SCOPE,
        compliance_status="NUMERICAL_BACKEND_ONLY",
    )


class ThermalPostprocessTests(unittest.TestCase):
    def test_frsi_analytic(self):
        v = compute_temperature_factor_frsi(
            synthetic_result(), interior_surface_node_indices=[0, 1],
            indoor_temperature_c=20.0, outdoor_temperature_c=0.0)
        self.assertAlmostEqual(v.minimum_surface_temperature_c, 12.0)
        self.assertEqual(v.minimum_surface_node_index, 1)
        self.assertAlmostEqual(v.temperature_factor_frsi, 0.6)
        self.assertEqual(v.engineering_acceptance, "NOT_ADMITTED")

    def test_psi_analytic_and_negative_allowed(self):
        params=dict(interior_heat_flow_boundary_names=["inside"], indoor_temperature_c=20.0,
                    outdoor_temperature_c=0.0, dimension_reference="external")
        positive = compute_linear_transmittance_psi(
            synthetic_result(), reference_u_length_pairs=[(0.4, 2.0)], **params)
        self.assertAlmostEqual(positive.coupling_coefficient_l2d_w_mk, 1.0)
        self.assertAlmostEqual(positive.linear_transmittance_psi_w_mk, 0.2)
        self.assertEqual(positive.dimension_reference, "external")
        negative = compute_linear_transmittance_psi(
            synthetic_result(), reference_u_length_pairs=[(1.5, 1.0)], **params)
        self.assertAlmostEqual(negative.linear_transmittance_psi_w_mk, -0.5)
        self.assertEqual(negative.engineering_acceptance, "NOT_ADMITTED")

    def test_multiple_heat_flow_components(self):
        v = compute_linear_transmittance_psi(
            synthetic_result(), interior_heat_flow_boundary_names=["inside", "extra"],
            indoor_temperature_c=20, outdoor_temperature_c=0,
            reference_u_length_pairs=[(0.5, 1.0)], dimension_reference="internal")
        self.assertAlmostEqual(v.coupling_coefficient_l2d_w_mk, 1.5)
        self.assertAlmostEqual(v.linear_transmittance_psi_w_mk, 1.0)

    def test_frsi_rejects_invalid_nodes_or_temperature(self):
        for indices in [[], [-1], [3], [1, 1], [True], [1.5]]:
            with self.subTest(indices=indices), self.assertRaises(ThermalBridgeInputError):
                compute_temperature_factor_frsi(
                    synthetic_result(), interior_surface_node_indices=indices,
                    indoor_temperature_c=20, outdoor_temperature_c=0)
        for indoor, outside in [(0, 0), (0, 20), (float("nan"), 0), (20, float("inf"))]:
            with self.subTest(temperature=(indoor, outside)), self.assertRaises(ThermalBridgeInputError):
                compute_temperature_factor_frsi(
                    synthetic_result(), interior_surface_node_indices=[0],
                    indoor_temperature_c=indoor, outdoor_temperature_c=outside)

    def test_psi_rejects_invalid_inputs(self):
        base=dict(result=synthetic_result(), interior_heat_flow_boundary_names=["inside"],
                  indoor_temperature_c=20, outdoor_temperature_c=0,
                  reference_u_length_pairs=[(1, 1)], dimension_reference="internal")
        overrides=[
            {"interior_heat_flow_boundary_names": []},
            {"interior_heat_flow_boundary_names": ["unknown"]},
            {"interior_heat_flow_boundary_names": ["inside", "inside"]},
            {"reference_u_length_pairs": []},
            {"reference_u_length_pairs": [(0, 1)]},
            {"reference_u_length_pairs": [(1, -1)]},
            {"reference_u_length_pairs": [(float("inf"), 1)]},
            {"dimension_reference": "unknown"},
            {"indoor_temperature_c": 0},
            {"result": synthetic_result(flows={"inside": -1.0})},
            {"result": synthetic_result(flows={"inside": float("nan")})},
        ]
        for override in overrides:
            with self.subTest(override=override), self.assertRaises(ThermalBridgeInputError):
                compute_linear_transmittance_psi(**(base | override))

    def test_source_scope_gate(self):
        bad=ThermalBridge2DResult(
            node_temperature_c=(15.0,), boundary_heat_flow_w_per_m={"inside": 1.0},
            backend={}, validation_scope="OTHER", compliance_status="NUMERICAL_BACKEND_ONLY")
        with self.assertRaises(ThermalBridgeInputError):
            compute_temperature_factor_frsi(
                bad, interior_surface_node_indices=[0],
                indoor_temperature_c=20, outdoor_temperature_c=0)


if __name__ == "__main__":
    unittest.main()
