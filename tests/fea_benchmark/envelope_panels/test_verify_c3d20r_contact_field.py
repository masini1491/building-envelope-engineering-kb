"""Bounded FRD fixed-format regression and negative tests."""
import unittest
from verify_c3d20r_contact_field import parse_frd


def fake_frd(pressure=' 3.13159E-02', negative='-3.13159E-07', nblocks=10, drop=False, fields=True):
    node = ' -1' + f'{579:10d}' + ' 1.00000E+02 0.00000E+00 1.50000E+00'
    header = (' -4  CONTACT     6    1\n' +
              ''.join(f' -5  {n:<12}1    1    0    0\n' for n in
                      ['COPEN','CSLIP1','CSLIP2','CPRESS','CSHEAR1','CSHEAR2']))
    row = (' -1' + f'{579:10d}' + negative + ' 0.00000E+00 0.00000E+00' +
           pressure + ' 0.00000E+00 0.00000E+00\n')
    body = header + ('' if drop else row) + ' -3\n'
    if not fields:body=body.replace('CPRESS','NOTPRES')
    return '    2C   1 1\n'+node+'\n -3\n' + body*nblocks

class TestFieldFRD(unittest.TestCase):
    def test_glued_negative_node_and_six_values(self):
        coords,blocks=parse_frd(fake_frd())
        self.assertEqual(coords[579],(100.,0.,1.5))
        self.assertEqual(len(blocks),10)
        self.assertAlmostEqual(blocks[-1][579][0],-3.13159e-7)
        self.assertAlmostEqual(blocks[-1][579][3],3.13159e-2)
    def test_missing_block(self):
        with self.assertRaisesRegex(ValueError,'FRD_CONTACT_STEPS'):
            parse_frd(fake_frd(nblocks=9))
    def test_missing_row(self):
        with self.assertRaisesRegex(ValueError,'FRD_CONTACT_COVERAGE'):
            parse_frd(fake_frd(drop=True))
    def test_wrong_field_order(self):
        with self.assertRaisesRegex(ValueError,'FRD_CONTACT_HEADERS'):
            parse_frd(fake_frd(fields=False))
    def test_duplicate_coordinate_node(self):
        bad=fake_frd().replace(' -3\n', ' -1       579 1.00000E+02 0.00000E+00 1.50000E+00\n -3\n',1)
        with self.assertRaisesRegex(ValueError,'FRD_NODE_FORMAT'):
            parse_frd(bad)
if __name__=='__main__':unittest.main()
