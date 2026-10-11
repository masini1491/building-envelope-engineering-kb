"""Stage 30 bounded cascade diagnostics synthetic checks."""
import tempfile
from pathlib import Path
import unittest
from check_cascade_trace import parse
from ccx_cascade_probe import patch

class Checks(unittest.TestCase):
    def test_change_is_observation_not_admission(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"audit"
            p.write_text("CASCADE_V1,1,IN,2,16,8\nCASCADE_V1,1,OUT,2,8,4\n")
            got=parse(p)
            self.assertEqual(got["changed_total_term_count_calls"],1)
            self.assertEqual(got["specific_8_to_4_causality"],"NOT_ESTABLISHED")
    def test_stable_counts_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"audit"
            p.write_text("CASCADE_V1,1,IN,1,8,8\nCASCADE_V1,1,OUT,1,8,8\n")
            self.assertEqual(parse(p)["changed_total_term_count_calls"],0)
    def test_orphan_exit_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"audit";p.write_text("CASCADE_V1,1,OUT,1,8,8\n")
            with self.assertRaisesRegex(ValueError,"INCOMPLETE_PAIR"):parse(p)
    def test_empty_meanrot_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"audit";p.write_text("CASCADE_V1,1,IN,0,0,0\nCASCADE_V1,1,OUT,0,0,0\n")
            with self.assertRaisesRegex(ValueError,"NO_MEANROT"):parse(p)
    def test_malformed_counts_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"audit";p.write_text("CASCADE_V1,1,IN,2,1,8\nCASCADE_V1,1,OUT,2,1,8\n")
            with self.assertRaisesRegex(ValueError,"INVALID_VALUE"):parse(p)
    def test_unknown_source_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNKNOWN_CASCADE_SOURCE"):patch("unexpected")

if __name__=="__main__":unittest.main()
