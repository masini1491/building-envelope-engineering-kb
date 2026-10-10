"""Positive and adversarial cases for CCX 3D-to-shell RF projection."""
import tempfile
import unittest
from pathlib import Path

from check_rf_3d_projection import NODE8_GROUPS, project_expanded_rf, read_final_expanded_rf


def block(time="1.00000E+00", force=None):
    force = force or [(1, (1.0, 0.0, -1.0))]
    header = " " * 12 + f"{float(time):12.5E}" + " " * 40
    rows = [f" -1{node:10d}" + "".join(f"{v:12.5E}" for v in xyz) for node, xyz in force]
    return "  100CL" + header[7:] + "\n -4  FORC        4    1\n" + "\n".join(rows) + "\n -3\n"


class RFProjectionTests(unittest.TestCase):
    def read(self, text, expected={1}):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "sample.frd"
            path.write_text(text)
            return read_final_expanded_rf(path, expected)

    def test_expanded_force_fixed_fields(self):
        got = self.read(block(force=[(1, (1.5, -3.25, 0.0))]))
        self.assertEqual(got[1], (1.5, -3.25, 0.0))

    def test_projection_thickness_groups(self):
        original = [tuple(range(1, 9))]
        expanded = {1: tuple(range(21, 41))}
        values = {i: (1.0, 2.0, -3.0) for i in range(21, 41)}
        mapped, incidence = project_expanded_rf(original, expanded, values)
        self.assertEqual([mapped[i][0] for i in range(1, 9)], [3, 3, 3, 3, 2, 2, 2, 2])
        self.assertEqual(set(incidence.values()), {1})
        self.assertEqual(NODE8_GROUPS[0], (0, 16, 4))

    def test_shared_original_node_counts_and_unique_3d(self):
        a = list(range(1, 9))
        b = list(range(9, 17))
        b[0] = a[1]
        first = tuple(range(21, 41))
        second = list(range(41, 61))
        for slot in NODE8_GROUPS[0]:
            second[slot] = first[NODE8_GROUPS[1][NODE8_GROUPS[0].index(slot)]]
        forces = {i: (1.0, 0.0, 0.0) for i in set(first) | set(second)}
        mapped, incidence = project_expanded_rf([tuple(a), tuple(b)], {1:first, 2:tuple(second)}, forces)
        self.assertEqual(incidence[a[1]], 2)
        self.assertEqual(mapped[a[1]][0], 3.0 / 2.0)

    def test_reject_partial_and_ambiguous_connectivity(self):
        original = [tuple(range(1,9))]
        expanded = {1: tuple(range(21,41))}
        force = {i:(1.,0.,0.) for i in range(21,41)}
        with self.assertRaisesRegex(ValueError,"INCOMPLETE_OR_NONFINITE_EXPANDED_RF"):
            project_expanded_rf(original, expanded, {k:v for k,v in force.items() if k != 40})
        bad = list(expanded[1]); bad[4] = bad[1]
        with self.assertRaisesRegex(ValueError,"BAD_S8R_OR_C3D20_CONNECTIVITY"):
            project_expanded_rf(original,{1:tuple(bad)},force)

    def test_missing_final_or_nonfinite_frd_rejected(self):
        with self.assertRaisesRegex(ValueError,"MISSING_FINAL_EXPANDED_RF"):
            self.read(block(time="0.9"))
        with self.assertRaisesRegex(ValueError,"DUPLICATE_OR_NONFINITE_FRD_RF"):
            self.read(block(force=[(1,(float("nan"),0.,0.))]))
        with self.assertRaisesRegex(ValueError,"EXPANDED_RF_COVERAGE_MISMATCH"):
            self.read(block(), {1,2})


if __name__ == "__main__":
    unittest.main()
