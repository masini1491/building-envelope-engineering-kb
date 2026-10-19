"""Synthetic corruption controls; real six-case coverage is in CI."""
import unittest
from verify_ccx221_output_fn import check_trace

def fixture(nk=2, mt=2):
    lines = []
    for inc in range(1, 11):
        lines.append(f"KB_OUTPUT_FN_BEGIN 1 {inc} {nk} {mt}")
        for n in range(1, nk + 1):
            for d in range(mt):
                lines.append(f"KB_OUTPUT_FN {n} {d} 1.5 {-2 if d == 0 else 1}")
        lines.append("KB_OUTPUT_FN_END")
    return lines

class TraceTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(check_trace(fixture())["blocks"], 10)
    def test_truncated(self):
        with self.assertRaises(ValueError):
            check_trace(fixture()[:-1])
    def test_index_swap(self):
        x = fixture(); x[1] = "KB_OUTPUT_FN 2 0 1.5 -2"
        with self.assertRaises(ValueError):
            check_trace(x)
    def test_nan(self):
        x = fixture(); x[1] = "KB_OUTPUT_FN 1 0 nan -2"
        with self.assertRaises(ValueError):
            check_trace(x)
    def test_owner_drift(self):
        x = fixture(); x[7] = "KB_OUTPUT_FN 1 0 1.5 1"
        with self.assertRaises(ValueError):
            check_trace(x)
    def test_increment_gap(self):
        x = fixture(); x[6] = "KB_OUTPUT_FN_BEGIN 1 12 2 2"
        with self.assertRaises(ValueError):
            check_trace(x)

if __name__ == "__main__":
    unittest.main()
