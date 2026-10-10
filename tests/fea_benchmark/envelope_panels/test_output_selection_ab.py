"""Output-selection A/B gate: deck mutation must be exactly isolated."""
import tempfile
import unittest
from pathlib import Path

from check_output_selection_ab import verify_pair


class ABTests(unittest.TestCase):
    def test_rejects_nonisolated_deck_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/"a.inp",Path(tmp)/"b.inp"
            a.write_text("*STEP,NLGEOM\n*NODE PRINT,NSET=NALL\nU,RF\n*END STEP\n")
            b.write_text("*STEP,NLGEOM\n*NODE PRINT,NSET=NALL\nU\n*DLOAD\n*END STEP\n")
            with self.assertRaisesRegex(ValueError,"NOT_ISOLATED_NALL_RF_OUTPUT_CHANGE"):
                verify_pair(a,Path(tmp)/"a.dat",b,Path(tmp)/"b.dat")

    def test_rejects_missing_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/"a.inp",Path(tmp)/"b.inp"
            a.write_text("*STEP,NLGEOM\n*END STEP\n")
            b.write_text(a.read_text())
            with self.assertRaisesRegex(ValueError,"NOT_ISOLATED_NALL_RF_OUTPUT_CHANGE"):
                verify_pair(a,Path(tmp)/"a.dat",b,Path(tmp)/"b.dat")


if __name__=="__main__":
    unittest.main()
