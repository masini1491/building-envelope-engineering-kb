import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from subprocess import CompletedProcess, TimeoutExpired

from scripts.engineering_calc.calculix_probe import (
    FEAProbeInputError, probe_calculix,
)


class CalculixProbeTests(unittest.TestCase):
    def test_requires_opt_in_and_never_runs_by_default(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "case.inp").write_text("*HEADING\n", encoding="utf-8")
            with patch("scripts.engineering_calc.calculix_probe.subprocess.run") as run:
                result = probe_calculix(
                    executable="/nonexistent/ccx", job_name="case", workspace=d
                )
                self.assertEqual(result.execution_status, "NOT_EXECUTED_OPT_IN_REQUIRED")
                run.assert_not_called()

    def test_rejects_bad_input(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "case.inp").write_text("*HEADING\n", encoding="utf-8")
            for name in ("../case", "bad name", "-x", ""):
                with self.subTest(name=name), self.assertRaises(FEAProbeInputError):
                    probe_calculix(executable="ccx", job_name=name, workspace=d)
            with self.assertRaises(FEAProbeInputError):
                probe_calculix(executable="ccx", job_name="missing", workspace=d)
            with self.assertRaises(FEAProbeInputError):
                probe_calculix(executable="ccx", job_name="case", workspace=d, timeout_seconds=0)

    def test_zero_exit_is_not_nonlinear_validation(self):
        with tempfile.TemporaryDirectory() as d:
            exe = Path(d, "ccx")
            exe.write_text("not executed", encoding="utf-8")
            Path(d, "case.inp").write_text("*HEADING\n", encoding="utf-8")
            with patch("scripts.engineering_calc.calculix_probe.subprocess.run",
                       return_value=CompletedProcess([], 0, "solver output", "")):
                result = probe_calculix(
                    executable=str(exe), job_name="case", workspace=d, execute=True
                )
                self.assertEqual(result.execution_status, "PROCESS_EXIT_ZERO_UNVERIFIED")
                self.assertEqual(result.result_scope, "EXECUTION_ONLY_NOT_NUMERICALLY_VALIDATED")

    def test_timeout_is_not_a_pass(self):
        with tempfile.TemporaryDirectory() as d:
            exe = Path(d, "ccx")
            exe.write_text("not executed", encoding="utf-8")
            Path(d, "case.inp").write_text("*HEADING\n", encoding="utf-8")
            with patch("scripts.engineering_calc.calculix_probe.subprocess.run",
                       side_effect=TimeoutExpired("ccx", 3)):
                result = probe_calculix(
                    executable=str(exe), job_name="case", workspace=d, execute=True
                )
                self.assertEqual(result.execution_status, "TIMEOUT")
