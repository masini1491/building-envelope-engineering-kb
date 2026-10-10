"""NALL/EDGE RF source-projection parsing and fail-closed coverage tests."""
import unittest

from audit_rf_projection import rf_block


def block(name, rows, time="1.0000000E+00"):
    return f" forces (fx,fy,fz) for set {name} and time {time}\n\n" + "".join(
        f" {nid} {x:.6E} {y:.6E} {z:.6E}\n" for nid,x,y,z in rows) + "\n"


class RfProjectionTests(unittest.TestCase):
    def test_exact_nall_coverage(self):
        src = block("NALL", [(1,0.,0.,-3.), (2,0.,0.,4.)])
        self.assertEqual(rf_block(src,"NALL",{1,2})[2], (0.,0.,4.))

    def test_missing_and_wrong_time_rejected(self):
        for source in ("", block("NALL", [(1,0.,0.,0.)], time="9.0000000E-01")):
            with self.assertRaisesRegex(ValueError,"MISSING_FINAL_NALL_RF"):
                rf_block(source,"NALL",{1})

    def test_missing_node_and_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError,"INCOMPLETE_NALL_RF_COVERAGE"):
            rf_block(block("NALL",[(1,0.,0.,0.)]),"NALL",{1,2})
        with self.assertRaisesRegex(ValueError,"DUPLICATE_OR_NONFINITE_RF"):
            rf_block(block("NALL",[(1,0.,0.,0.),(1,0.,0.,0.)]),"NALL",{1})

    def test_nonfinite_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_OR_NONFINITE_RF"):
            rf_block(" forces (fx,fy,fz) for set NALL and time 1.0000000E+00\n\n 1 1.000000E+999 0.000000E+00 0.000000E+00\n\n","NALL",{1})


if __name__ == "__main__":
    unittest.main()
