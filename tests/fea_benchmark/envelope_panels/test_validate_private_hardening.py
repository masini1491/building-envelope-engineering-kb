"""Synthetic-only checks for private hardening table input schema."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from validate_private_hardening import validate, read


def example(grade="3004-O"):
    return {
        "alloy_temper": grade,
        "product_id": "SYNTHETIC-ONLY",
        "manufacturer": "CS Aluminum",
        "state": "AS_SUPPLIED",
        "data_origin": "PRIVATE_USER_SUPPLIED_MANUFACTURER_DECLARATION",
        "units": "N-mm-MPa",
        "curve_type": "TRUE_VON_MISES_STRESS_EQUIVALENT_PLASTIC_STRAIN",
        "elastic_modulus_mpa": 70000.0,
        "poisson_ratio": 0.30,
        "points": [[100.0, 0.0], [103.0, 0.003], [110.0, 0.01]],
    }


class Tests(unittest.TestCase):
    def test_three_alloys_are_bounded_research_only(self):
        for grade in ("3003-H14", "3004-H12", "3004-O"):
            with self.subTest(grade=grade):
                result = validate(example(grade))
                self.assertEqual(result["point_count"], 3)
                self.assertEqual(result["engineering_capacity"], "NOT_ADMITTED")
                self.assertNotIn("product_id", result)
                self.assertNotIn("points", result)

    def test_rejects_nonphysical_and_ambiguous_input(self):
        variants = [
            ("alloy_temper", "3004-H24"), ("manufacturer", "Other"),
            ("product_id", "../../secret.pdf"), ("state", "AFTER_COATING"),
            ("data_origin", "INFERRED_FROM_YIELD_AND_ULTIMATE"),
            ("curve_type", "ENGINEERING_STRESS_STRAIN"), ("units", "ksi"),
            ("elastic_modulus_mpa", True), ("poisson_ratio", 0.5),
            ("points", [[100,0],[101,0],[103,.1]]),
            ("points", [[100,0],[99,.01],[103,.02]]),
            ("points", [[100,.001],[101,.003],[103,.01]]),
            ("points", [[100,0],[101,.01]]),
            ("points", [[100,0],[101,float("nan")],[103,.01]]),
        ]
        for key, replacement in variants:
            with self.subTest(key=key,replacement=str(replacement)):
                data=example()
                data[key]=replacement
                with self.assertRaises(ValueError):validate(data)

    def test_file_rejects_duplicate_keys_and_nonfinite_values(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"material.json"
            p.write_text(json.dumps(example()),encoding="utf-8")
            self.assertEqual(read(p)["point_count"],3)
            p.write_text('{"points":[],"points":[]}')
            with self.assertRaisesRegex(ValueError,"DUPLICATE"):
                read(p)
            p.write_text('{"points":NaN}')
            with self.assertRaises(ValueError):read(p)

    def test_reject_implicit_or_overspecified_fields(self):
        x=example()
        x["yield_strength_mpa"] = 100
        with self.assertRaisesRegex(ValueError,"SCHEMA"):
            validate(x)
        x=example()
        del x["curve_type"]
        with self.assertRaisesRegex(ValueError,"SCHEMA"):
            validate(x)

if __name__ == "__main__":
    unittest.main()
