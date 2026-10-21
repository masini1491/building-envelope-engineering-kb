"""Negative/positive mutation contracts for C3D20R face contact integration output."""
import unittest
from contact_ip_trial import ORIGINAL,INSTRUMENTED,instrument_deck,deck
from pressure_contact_trial import deck as base_deck

class ContactIPTest(unittest.TestCase):
    def test_deck_is_output_only(self):
        for n in (16,24):
            base=base_deck(n,'toward')
            changed=deck(n,'toward')
            self.assertEqual(changed.count(INSTRUMENTED),1)
            self.assertEqual(changed.replace(INSTRUMENTED,ORIGINAL),base)
            self.assertEqual(changed.count('*CONTACT PAIR'),1)
    def test_does_not_double_instrument(self):
        with self.assertRaisesRegex(ValueError,'DECK_CONTRACT'):
            instrument_deck(deck(16,'toward'))
    def test_refuses_missing_print(self):
        with self.assertRaisesRegex(ValueError,'DECK_CONTRACT'):
            instrument_deck(base_deck(16,'toward').replace(ORIGINAL,''))
    def test_refuses_missing_pressure(self):
        with self.assertRaisesRegex(ValueError,'DECK_CONTRACT'):
            instrument_deck(base_deck(16,'toward').replace('PLATE,P1,0.00010000','PLATE,P1,0.00020000'))
    def test_rejects_invalid_scope(self):
        for n,c in ((8,'toward'),(32,'toward'),(16,'unlinked'),(16,'clearance'),(True,'toward')):
            with self.assertRaisesRegex(ValueError,'IP_SCOPE'):deck(n,c)
if __name__=='__main__':unittest.main()
