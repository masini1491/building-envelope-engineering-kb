"""Synthetic-only Hot-3 intake tests; never embed real SGS or client data."""
import copy
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from stud_engineering_intake_report import (
    SCOPE, fixture, inspect, read_request, replay_zip, render,
)


class Intake(unittest.TestCase):
    def test_valid_exact_fixture(self):
        for mesh in (8,16,24):
            for case in ("unlinked","soft","stiff"):
                for direction in ("positive","negative"):
                    with self.subTest(mesh=mesh,case=case,direction=direction):
                        x=inspect(fixture(mesh,case,direction))
                        self.assertEqual(x["calculation_status"],"SUPPORTED_SYNTHETIC_SCOPE")
                        self.assertFalse(x["solver_evidence_replayed"])
    def test_missing_pressure(self):
        x=fixture();del x["load"]["signed_pressure_n_mm2"]
        result=inspect(x)
        self.assertEqual(result["calculation_status"],"INCOMPLETE_INPUT")
        self.assertIn("load.signed_pressure_n_mm2",result["missing_fields"])
    def test_missing_support(self):
        x=fixture();x["support"]=None
        self.assertEqual(inspect(x)["calculation_status"],"INCOMPLETE_INPUT")
    def test_changed_span_is_unsupported(self):
        x=fixture();x["geometry"]["panel_length_mm"]=1600.
        y=inspect(x)
        self.assertEqual(y["calculation_status"],"UNSUPPORTED_MODEL")
        self.assertIn("geometry.panel_length_mm",y["unsupported_fields"])
    def test_changed_wind_pressure_is_unsupported(self):
        x=fixture();x["load"]["signed_pressure_n_mm2"]=.0002
        self.assertEqual(inspect(x)["calculation_status"],"UNSUPPORTED_MODEL")
    def test_changed_connection_stiffness_unsupported(self):
        x=fixture();x["connection"]["k_per_station_n_mm"]=900.
        self.assertEqual(inspect(x)["calculation_status"],"UNSUPPORTED_MODEL")
    def test_changed_site_and_support_unsupported(self):
        x=fixture();x["connection"]["station_x_mm"]=[150.,450.,700.,1050.]
        x["support"]["rib"]="END_FIXED_WITH_ANGLE_BRACKETS"
        r=inspect(x)
        self.assertIn("connection.station_x_mm",r["unsupported_fields"])
        self.assertIn("support.rib",r["unsupported_fields"])
    def test_actual_material_unsupported(self):
        x=fixture();x["material"]["model"]="3004-H12"
        self.assertEqual(inspect(x)["calculation_status"],"UNSUPPORTED_MODEL")
    def test_load_sign_inconsistent(self):
        x=fixture(direction="negative");x["load"]["signed_pressure_n_mm2"]=.0001
        self.assertIn("load.signed_pressure_n_mm2",inspect(x)["unsupported_fields"])
    def test_unknown_case_is_not_coerced(self):
        x=fixture();x["connection"]["case"]="actual_m6_weld"
        self.assertEqual(inspect(x)["calculation_status"],"UNSUPPORTED_MODEL")
    def test_unknown_mesh_is_not_coerced(self):
        x=fixture();x["mesh"]=32
        self.assertEqual(inspect(x)["calculation_status"],"UNSUPPORTED_MODEL")
    def test_unhashable_case_and_direction_are_incomplete(self):
        bad = fixture()
        bad["connection"]["case"] = ["soft"]
        bad["load"]["direction"] = {"unexpected": "positive"}
        result = inspect(bad)
        self.assertEqual(result["calculation_status"], "INCOMPLETE_INPUT")
        self.assertIn("connection.case", result["invalid_fields"])
        self.assertIn("load.direction", result["invalid_fields"])
    def test_null_case_and_direction_are_missing(self):
        bad = fixture()
        bad["connection"]["case"] = None
        bad["load"]["direction"] = None
        result = inspect(bad)
        self.assertEqual(result["calculation_status"], "INCOMPLETE_INPUT")
        self.assertIn("connection.case", result["missing_fields"])
        self.assertIn("load.direction", result["missing_fields"])
    def test_wrong_units_rejected(self):
        x=fixture();x["units"]["pressure"]="kPa"
        self.assertEqual(inspect(x)["calculation_status"],"UNSUPPORTED_MODEL")
    def test_nan_boolean_rejected(self):
        x=fixture();x["geometry"]["panel_length_mm"]=float("nan")
        self.assertEqual(inspect(x)["calculation_status"],"INCOMPLETE_INPUT")
        x=fixture();x["mesh"]=True
        self.assertEqual(inspect(x)["calculation_status"],"INCOMPLETE_INPUT")
    def test_no_derived_report_without_artifact(self):
        r=render(fixture(),None)
        self.assertEqual(r["calculation_status"],"EVIDENCE_REQUIRED")
        self.assertEqual(r["engineering_acceptance"],"NOT_ADMITTED")
    def test_fake_artifact_digest_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"evidence.zip";p.write_bytes(b"fake zip")
            with self.assertRaisesRegex(ValueError,"ARTIFACT_DIGEST"):replay_zip(p)
    def test_duplicate_json_and_nan_parse_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"request.json";p.write_text('{"scope":"x","scope":"y"}')
            with self.assertRaisesRegex(ValueError,"DUPLICATE_KEY"):read_request(p)
            p.write_text('{"load":NaN}')
            with self.assertRaisesRegex(ValueError,"NONFINITE_JSON"):read_request(p)
    def test_cli_missing_evidence_safely_returns_status(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"request.json";p.write_text(json.dumps(fixture()))
            script=Path(__file__).with_name("stud_engineering_intake_report.py")
            result=subprocess.run([sys.executable,"-B",str(script),str(p)],
                                  capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)
            output=json.loads(result.stdout)
            self.assertEqual(output["calculation_status"],"EVIDENCE_REQUIRED")
            self.assertEqual(output["engineering_acceptance"],"NOT_ADMITTED")
    def test_cli_unsupported_does_not_need_solver(self):
        with tempfile.TemporaryDirectory() as d:
            x=fixture();x["geometry"]["panel_length_mm"]=1600
            p=Path(d)/"request.json";p.write_text(json.dumps(x))
            script=Path(__file__).with_name("stud_engineering_intake_report.py")
            result=subprocess.run([sys.executable,"-B",str(script),str(p)],
                                  capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)
            output=json.loads(result.stdout)
            self.assertEqual(output["calculation_status"],"UNSUPPORTED_MODEL")
            self.assertNotIn("1600",result.stdout)


if __name__=="__main__":
    unittest.main()
