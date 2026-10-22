"""Deterministic distributed pressure input contract and negative controls."""
import unittest
from pressure_contact_trial import deck, APPLIED_TOTAL_Z_N
from quadratic_contact_trial import deck as base_deck


class PressureTrial(unittest.TestCase):
    def test_6_decks_and_external_load_contract(self):
        self.assertAlmostEqual(APPLIED_TOTAL_Z_N, 36.0)
        for n in (8, 16, 24):
            for kind in ('toward', 'unlinked', 'clearance'):
                with self.subTest(n=n, kind=kind):
                    inp = deck(n, kind)
                    source = base_deck(n, kind)
                    self.assertEqual(inp.count('*DLOAD\nPLATE,P1,0.00010000\n'), 1)
                    self.assertNotIn('CENTER_RF,3,3,', inp)
                    self.assertEqual(inp.count('*NODE PRINT'), 3)
                    self.assertEqual(inp.count('*CONTACT PAIR'), int(kind != 'unlinked'))
                    self.assertEqual(inp.count('*ELEMENT,TYPE=C3D20R'), 2)
                    self.assertEqual(inp.count('*NODE'), source.count('*NODE'))
                    self.assertEqual(inp.count('*NSET'), source.count('*NSET'))
                    self.assertEqual(inp.count('*STEP'), 1)
    def test_invalid_scope(self):
        for n,kind in ((32,'toward'),(4,'toward'),(True,'toward'),(8,'away'),(8,'unknown')):
            with self.assertRaisesRegex(ValueError,'C3D20R_PRESSURE_SCOPE'):
                deck(n,kind)
    def test_preserve_boundary_and_material(self):
        for case in ('toward','unlinked','clearance'):
            inp=deck(8,case)
            self.assertIn('PLATE_EDGE_RF,1,3,0.',inp)
            self.assertIn('RIB_END_RF,1,3,0.',inp)
            self.assertIn('*ELASTIC\n69000.,0.33',inp)
            self.assertNotIn('*CLOAD',inp)
            self.assertNotIn('*DSLOAD',inp)

if __name__ == '__main__': unittest.main()
