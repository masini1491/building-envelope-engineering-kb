"""Synthetic metadata only: never expose actual client documents or material data."""
import json
import tempfile
import unittest
from pathlib import Path

from check_aluminum_material_evidence import check, read_metadata
from prepare_aluminum_material_input import read_selection
from aluminum_research_input import load
from test_prepare_aluminum_material_input import selection


def declared(grade="3004-O"):
    return {
        "manufacturer": "CS Aluminum", "alloy_temper": grade,
        "product_id": "SYNTHETIC-PRODUCT", "product_form": "sheet",
        "material_condition": "AS_SUPPLIED", "source_visibility": "PRIVATE",
        "evidence_claim": "USER_DECLARED_NOT_VERIFIED",
        "thickness_range_mm": [2.0, 3.0],
        "elastic_properties": {
            "youngs_modulus_mpa": 70000.0, "poisson_ratio": 0.32,
        },
    }


class EvidenceTests(unittest.TestCase):
    def test_three_grades_private_and_public(self):
        for grade in ("3003-H14", "3004-H12", "3004-O"):
            raw = dict(selection(grade), product_id="SYNTHETIC-PRODUCT")
            obj = declared(grade)
            for visibility in ("PUBLIC", "PRIVATE"):
                obj["source_visibility"] = visibility
                with self.subTest(grade=grade, visibility=visibility):
                    self.assertEqual(check(raw, obj), "DECLARED_METADATA_CONSISTENCY_ONLY")
                    with tempfile.TemporaryDirectory() as d:
                        root = Path(d)
                        (root/"selection.json").write_text(json.dumps(raw))
                        (root/"evidence.json").write_text(json.dumps(obj))
                        out = read_selection(root/"selection.json", root/"evidence.json")
                        (root/"out.json").write_text(json.dumps(out))
                        self.assertEqual(load(root/"out.json"), out)
                        self.assertNotIn("SYNTHETIC-PRODUCT", json.dumps(out))
                        self.assertEqual(len(out), 10)

    def test_explicit_manufacturer_declaration_trusted_not_independently_certified(self):
        for grade in ("3003-H14", "3004-H12", "3004-O"):
            chosen = dict(selection(grade), product_id="SYNTHETIC-PRODUCT",
                          property_evidence_status="MANUFACTURER_DECLARATION_ACCEPTED_BY_USER")
            record = dict(declared(grade), evidence_claim="MANUFACTURER_DECLARATION_ACCEPTED_BY_USER")
            self.assertEqual(check(chosen, record),
                             "USER_ACCEPTED_MANUFACTURER_METADATA_CONSISTENCY_ONLY")
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                (root / "selection.json").write_text(json.dumps(chosen))
                (root / "evidence.json").write_text(json.dumps(record))
                actual = read_selection(root / "selection.json", root / "evidence.json")
                self.assertIn("MANUFACTURER_DECLARATION_ACCEPTED_BY_USER:",
                              actual["material_provenance"])
                self.assertEqual(len(actual), 10)
                self.assertEqual(actual["youngs_modulus_mpa"], 70000.0)
                self.assertNotIn("SYNTHETIC-PRODUCT", json.dumps(actual))
                with self.assertRaises(ValueError):
                    read_selection(root / "selection.json")

    def test_trust_requires_matching_explicit_claim(self):
        chosen = dict(selection(), product_id="SYNTHETIC-PRODUCT",
                      property_evidence_status="MANUFACTURER_DECLARATION_ACCEPTED_BY_USER")
        with self.assertRaisesRegex(ValueError, "STATUS_NOT_ADMITTED"):
            check(chosen, declared())
        ordinary = dict(selection(), product_id="SYNTHETIC-PRODUCT")
        elevated = dict(declared(), evidence_claim="MANUFACTURER_DECLARATION_ACCEPTED_BY_USER")
        with self.assertRaisesRegex(ValueError, "STATUS_NOT_ADMITTED"):
            check(ordinary, elevated)

    def test_mismatched_identity_process_range_and_properties_reject(self):
        raw = dict(selection(), product_id="SYNTHETIC-PRODUCT")
        edits = [
            ("product_id", "DIFFERENT"),
            ("manufacturer", "other"),
            ("alloy_temper", "3004-H12"),
            ("product_form", "extrusion"),
            ("material_condition", "AFTER_COATING"),
            ("source_visibility", "UNKNOWN"),
            ("source_visibility", ["PUBLIC"]),
            ("evidence_claim", "VERIFIED_PRIMARY"),
            ("thickness_range_mm", [2.6, 3.0]),
            ("thickness_range_mm", [3.0, 2.0]),
            ("thickness_range_mm", [float('nan'), 3.0]),
            ("elastic_properties", {"youngs_modulus_mpa": 68000., "poisson_ratio": .32}),
            ("elastic_properties", {"youngs_modulus_mpa": 70000.}),
        ]
        for k, v in edits:
            record = declared()
            record[k] = v
            with self.subTest(key=k, v=v), self.assertRaises(ValueError):
                check(raw, record)
        with self.assertRaises(ValueError):
            check(dict(raw, product_id="../../secret.pdf"), declared())

    def test_malformed_and_missing_evidence_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            evidence = root/"evidence.json"
            evidence.write_text('{"alloy_temper":"3004-O","alloy_temper":"3003-H14"}')
            with self.assertRaisesRegex(ValueError, "DUPLICATE"):
                read_metadata(evidence)
            evidence.write_text('{"thickness_range_mm":[NaN,3]}')
            with self.assertRaises(ValueError):
                read_metadata(evidence)
            selected = root/"selection.json"
            selected.write_text(json.dumps(selection()))
            evidence.write_text(json.dumps(declared()))
            with self.assertRaisesRegex(ValueError, "PRODUCT_ID_REQUIRED"):
                read_selection(selected, evidence)
            # Legacy selector remains backward-compatible without evidence.
            self.assertEqual(len(read_selection(selected)), 10)
            selected.write_text(json.dumps(dict(selection(), product_id="SYNTHETIC-PRODUCT")))
            with self.assertRaises(ValueError):
                read_selection(selected)  # Cannot silently omit product identity.

if __name__ == "__main__":
    unittest.main()
