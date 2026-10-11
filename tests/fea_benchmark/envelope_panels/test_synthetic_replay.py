"""Synthetic replay comparison contract tests."""
import json
import tempfile
import unittest
from pathlib import Path
from check_synthetic_replay import load,compare

class ReplayTests(unittest.TestCase):
    def fixture(self):
        return {
            "execution_status":"SYNTHETIC_BENCHMARK_EVIDENCE_PASS",
            "engineering_acceptance":"NOT_ADMITTED",
            "six_component_global_balance":"NOT_ADMITTED",
            "design_capacity":"NOT_COMPUTED",
            "model_scope":"FIXED_SYNTHETIC_S8R_NLGEOM_P1",
            "material_proxy":"glass","mesh":4,
            "translational_balance":{"relative_global_residual":0.0},
            "expanded_moment_partition":{"internal":{"max_moment_partition_residual_Nmm":0.0}},
            "artifact_provenance":{x:"a"*64 for x in (
                "input_deck_sha256","solver_executable_sha256","final_dat_sha256",
                "final_frd_sha256","final_sta_sha256")}
        }
    def test_same_numeric_different_output_bytes_valid(self):
        a=self.fixture();b=self.fixture()
        b["artifact_provenance"]["final_dat_sha256"]="b"*64
        self.assertEqual(compare(a,b)["execution_status"],"INDEPENDENT_WORKSPACE_SYNTHETIC_REPLAY_PASS")
    def test_mismatch_numeric_rejected(self):
        a=self.fixture();b=self.fixture()
        b["translational_balance"]["relative_global_residual"]=1e-8
        with self.assertRaisesRegex(ValueError,"REPLAY_BOUNDED_NUMERIC_MISMATCH"):compare(a,b)
    def test_changed_deck_rejected(self):
        a=self.fixture();b=self.fixture()
        b["artifact_provenance"]["input_deck_sha256"]="b"*64
        with self.assertRaisesRegex(ValueError,"REPLAY_INPUT_OR_SOLVER_IDENTITY_MISMATCH"):compare(a,b)
    def test_missing_provenance_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"evidence.json";obj=self.fixture()
            del obj["artifact_provenance"]["final_frd_sha256"]
            p.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError,"REPLAY_INCOMPLETE_PROVENANCE"):load(p)
    def test_invalid_scope_or_nonfinite_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"evidence.json";obj=self.fixture()
            obj["engineering_acceptance"]="PASS"
            p.write_text(json.dumps(obj))
            with self.assertRaisesRegex(ValueError,"REPLAY_ADMISSION_SCOPE_DRIFT"):load(p)
            p.write_text('{"calculation":NaN}')
            with self.assertRaisesRegex(ValueError,"INVALID_JSON_NONFINITE"):load(p)
    def test_valid_evidence_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"evidence.json";obj=self.fixture()
            p.write_text(json.dumps(obj))
            self.assertEqual(load(p),obj)

if __name__=="__main__":unittest.main()
