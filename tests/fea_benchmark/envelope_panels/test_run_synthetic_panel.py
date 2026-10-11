"""Synthetic-only execution adapter negative and positive-contract checks."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from run_synthetic_panel import run_synthetic_panel,SyntheticPanelEvidenceError,_completed_step, FEAProbeResult

class Tests(unittest.TestCase):
    def test_opt_in_required_before_any_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            got=run_synthetic_panel(material="glass",mesh=4,workspace=d,executable="not-there")
            self.assertEqual(got["execution_status"],"NOT_EXECUTED_OPT_IN_REQUIRED")
            self.assertFalse(list(Path(d).iterdir()))
    def test_only_canonical_cases(self):
        for material,mesh in (("steel",4),("glass",3),("aluminum",True)):
            with self.subTest(material=material,mesh=mesh),self.assertRaises(ValueError):
                run_synthetic_panel(material=material,mesh=mesh,workspace="irrelevant",executable="x")
    def test_reject_nonempty_workspace_before_solver(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,"old.txt").write_text("old")
            with self.assertRaisesRegex(ValueError,"WORKSPACE_MUST_BE_EXISTING_AND_EMPTY"):
                run_synthetic_panel(material="glass",mesh=4,workspace=d,executable="x",execute=True)
    def test_zero_exit_does_not_pass_without_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            with patch("run_synthetic_panel.probe_calculix",return_value=FEAProbeResult(
                    "PROCESS_EXIT_ZERO_UNVERIFIED",0,"","")):
                with self.assertRaisesRegex(SyntheticPanelEvidenceError,"REQUIRED_OUTPUT"):
                    run_synthetic_panel(material="glass",mesh=4,workspace=d,executable="unused",execute=True)
    def test_nonzero_and_timeout_fail_closed(self):
        for status in ("PROCESS_NONZERO","TIMEOUT","EXECUTION_ERROR"):
            with tempfile.TemporaryDirectory() as d:
                with patch("run_synthetic_panel.probe_calculix",return_value=FEAProbeResult(status,None,"","")):
                    with self.assertRaisesRegex(SyntheticPanelEvidenceError,"SOLVER_DID_NOT_EXIT_ZERO"):
                        run_synthetic_panel(material="glass",mesh=4,workspace=d,executable="unused",execute=True)
    def test_partial_step_not_complete(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"panel.sta";p.write_text("1 1 1 1 0.5 1 1\n")
            with self.assertRaisesRegex(SyntheticPanelEvidenceError,"NONLINEAR_STEP_NOT_COMPLETE"):
                _completed_step(p)
    def test_symlink_workspace_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);real=base/"real";real.mkdir()
            link=base/"link"
            try:link.symlink_to(real,target_is_directory=True)
            except (OSError,NotImplementedError):self.skipTest("symlink unavailable")
            with self.assertRaisesRegex(ValueError,"WORKSPACE_SYMLINK"):
                run_synthetic_panel(material="glass",mesh=4,workspace=link,executable="x",execute=True)

if __name__=="__main__":unittest.main()
