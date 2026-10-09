"""Synthetic CCX FRD wire-format and expanded-node coverage negative tests."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_expanded_frd import CCX_TO_FRD, read_expanded_frd, _frd_vec


def fixture(*, final_time=1., missing_u=False, bad_kind=False):
    xy = [(0,0),(10,0),(10,20),(0,20),(0,0),(10,0),(10,20),(0,20),
          (5,0),(10,10),(5,20),(0,10),(5,0),(10,10),(5,20),(0,10),
          (0,0),(10,0),(10,20),(0,20)]
    z = [-1]*4 + [1]*4 + [-1]*4 + [1]*4 + [0]*4
    nodes = [(float(x),float(y),float(zz)) for (x,y),zz in zip(xy,z)]
    rows = ['    2C                     20        1']
    for nid, xyz in enumerate(nodes, 1):
        rows.append(f' -1{nid:10d}' + ''.join(f'{v:12.5E}' for v in xyz))
    rows += [' -3', '    3C                      1        1',
             f' -1{1:10d}{(2 if bad_kind else 4):5d}{0:5d}{1:5d}']
    frd_order = [slot+1 for slot in CCX_TO_FRD]
    rows.append(' -2' + ''.join(f'{x:10d}' for x in frd_order[:10]))
    rows.append(' -2' + ''.join(f'{x:10d}' for x in frd_order[10:]))
    rows.append(' -3')
    meta = list(' ' * 80)
    meta[:7] = '  100CL'
    meta[12:24] = f'{final_time:12.5E}'
    rows += [''.join(meta), ' -4  DISP        4    1']
    for nid in range(1, 21 if not missing_u else 20):
        rows.append(f' -1{nid:10d}' + ''.join(f'{0.:12.5E}' for _ in range(3)))
    return '\n'.join(rows + [' -3', ''])


class FrdTests(unittest.TestCase):
    def parse(self, source):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'panel.frd'
            path.write_text(source, encoding='ascii')
            return read_expanded_frd(path)

    def test_wire_format_and_slot_permutation(self):
        xyz, elems, disp = self.parse(fixture())
        self.assertEqual(len(xyz), 20)
        self.assertEqual(elems[1], tuple(range(1,21)))
        self.assertEqual(len(disp), 20)
        self.assertEqual(xyz[1], (0.0, 0.0, -1.0))

    def test_fixed_width_adjacent_negative(self):
        row = ' -1' + f'{1:10d}' + ''.join(f'{x:12.5E}' for x in (12.5,-2.5,0.0))
        self.assertEqual(_frd_vec(row), (1, (12.5, -2.5, 0.0)))

    def test_missing_expanded_displacement_fails(self):
        with self.assertRaisesRegex(ValueError, 'EXPANDED_FACE_COVERAGE_UNRESOLVED'):
            self.parse(fixture(missing_u=True))

    def test_not_3d_c3d20_fails(self):
        with self.assertRaisesRegex(ValueError, 'NOT_EXPANDED_C3D20_ELEMENT'):
            self.parse(fixture(bad_kind=True))

    def test_incomplete_step_fails(self):
        with self.assertRaisesRegex(ValueError, 'MISSING_FINAL_FRD_TIME'):
            self.parse(fixture(final_time=0.9))

    def test_duplicate_and_nonfinite_fail(self):
        old = f' -1{1:10d}' + ''.join(f'{v:12.5E}' for v in (0.,0.,-1.))
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_FRD_COORDINATE'):
            self.parse(fixture().replace(old, old + '\n' + old, 1))
        with self.assertRaisesRegex(ValueError, 'NONFINITE_OR_BAD_FRD_VECTOR'):
            self.parse(fixture().replace(old, old.replace(f'{0.:12.5E}', f'{float("nan"):12.5E}',1),1))

    def test_missing_file_blocks(self):
        with self.assertRaisesRegex(ValueError, 'MISSING_OR_BINARY_FRD'):
            self.parse('')
        with self.assertRaisesRegex(ValueError, 'MISSING_FRD_COORDINATES'):
            self.parse('  100CL       .10000E+01\n')


if __name__ == '__main__':
    unittest.main()
