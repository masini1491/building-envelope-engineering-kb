"""Fully synthetic fixtures: guards for cross-grade replay and attribution."""
import json
from pathlib import Path
import tempfile
import unittest
from check_aluminum_grade_replay import GRADES, verify
from prepare_aluminum_material_input import prepare


def choice(grade):
    return {
        "alloy_temper": grade, "manufacturer": "CS Aluminum",
        "property_evidence_status": "USER_DECLARED_UNVERIFIED",
        "width_mm": 120.0, "height_mm": 80.0, "thickness_mm": 2.5,
        "youngs_modulus_mpa": 70000.0, "poisson_ratio": 0.32,
        "pressure_n_mm2": 0.0002, "mesh": 4,
        "support": "four_edges_clamped", "units": "N-mm-MPa",
    }


def fabricate(root):
    for grade in GRADES:
        selected = choice(grade)
        prepared = prepare(selected)
        result = {
            "execution_status": "ALUMINUM_PARAMETRIC_RESEARCH_EVIDENCE_PASS",
            "model_scope": "RECTANGULAR_FOUR_EDGE_CLAMPED_LINEAR_ELASTIC_S8R_NLGEOM_P1",
            "engineering_acceptance": "NOT_ADMITTED",
            "global_six_component_balance": "NOT_ADMITTED",
            "aluminum_design_manual_capacity": "NOT_COMPUTED",
            "rotational_support_reaction": "UNOBSERVED",
            "inputs": prepared,
            "artifact_provenance": {"input_sha256": "a" * 64, "solver_sha256": "b" * 64},
            "translational_balance": {"residual": [0, 0, 0]},
            "research_observations": {"displacement": {"center_deflection": 0.123}},
            "expanded_moment_partition": {"six_component_balance": "NOT_ADMITTED"},
        }
        for name, obj in (("selection", selected), ("input", prepared), ("result", result)):
            (root / f"{name}_{grade}.json").write_text(json.dumps(obj), encoding="utf-8")


class Tests(unittest.TestCase):
    def test_three_grade_synthetic_replay(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)
            fabricate(path)
            result = verify(path)
            self.assertTrue(result["identical_observation_payload"])
            self.assertEqual(result["manufacturer_material_equivalence"], "NOT_TESTED")
            self.assertEqual(result["engineering_acceptance"], "NOT_ADMITTED")

    def test_reject_changed_explicit_e(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fabricate(root)
            path = root / "selection_3004-H12.json"
            obj = json.loads(path.read_text())
            obj["youngs_modulus_mpa"] = 68000.0
            path.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError, "INPUT_CHANGED"):
                verify(root)

    def test_reject_forged_physics_or_capacity(self):
        for key, value, code in (
            ("research_observations", {"displacement": 777}, "PHYSICS_OUTPUT_DIFFERENT"),
            ("engineering_acceptance", "PASS", "EVIDENCE_SCOPE_CHANGED"),
            ("global_six_component_balance", "PASS", "EVIDENCE_SCOPE_CHANGED"),
            ("artifact_provenance", {"input_sha256": "f" * 64, "solver_sha256": "b" * 64}, "DECK_OR_SOLVER_DIFFERENT"),
        ):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                fabricate(root)
                path = root / "result_3004-O.json"
                obj = json.loads(path.read_text())
                obj[key] = value
                path.write_text(json.dumps(obj))
                with self.subTest(key=key), self.assertRaisesRegex(ValueError, code):
                    verify(root)

    def test_reject_wrong_identity_and_missing(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fabricate(root)
            path = root / "selection_3003-H14.json"
            obj = json.loads(path.read_text())
            obj["alloy_temper"] = "3004-H12"
            path.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError, "NOT_EXPLICIT"):
                verify(root)
            path.unlink()
            with self.assertRaisesRegex(ValueError, "MISSING_OR_UNBOUNDED"):
                verify(root)

    def test_reject_duplicate_output_json_keys(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fabricate(root)
            (root / "result_3004-O.json").write_text('{"inputs":{},"inputs":{}}')
            with self.assertRaisesRegex(ValueError, "DUPLICATE"):
                verify(root)

if __name__ == "__main__":
    unittest.main()
