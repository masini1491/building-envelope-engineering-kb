"""Bounded source-level regression guards for the Chinese report renderer."""
import unittest
from pathlib import Path
class TestReportSource(unittest.TestCase):
 def test_fail_closed_evidence_contract(self):
  source=(Path(__file__).parent/'render_stud_position_report.py').read_text()
  for required in ("assert D['sha256']==", "assert seen==", "assert key not in seen", "assert len(D['cases'])==8", "assert D['engineering_acceptance']=='NOT_ADMITTED'", "abs(x['rib_reaction_residual_n'])<.002", "sum(x['station_forces_n'])"):
   with self.subTest(required=required):self.assertIn(required,source)
if __name__=='__main__':unittest.main()
