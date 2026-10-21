"""Deterministic negative and invariant controls for the field-capture deck."""
import unittest
from pressure_contact_trial import deck as canonical_deck
from contact_field_trial import instrument_deck, FIELD_CARD, deck

class FieldDeckTest(unittest.TestCase):
    @staticmethod
    def fixture(n):
        return canonical_deck(n,'toward')

    def test_exact_only_output_change_for_real_16_and_24(self):
        for n in (16,24):
            with self.subTest(mesh=n):
                raw=self.fixture(n);new=instrument_deck(raw)
                self.assertEqual(new.count(FIELD_CARD),1)
                self.assertEqual(new.replace(FIELD_CARD,''),raw)
                self.assertLess(new.index('*CONTACT PRINT'),new.index(FIELD_CARD))
                self.assertLess(new.index(FIELD_CARD),new.index('*END STEP'))

    def test_no_pair_rejected(self):
        for n in (16,24):
            raw=self.fixture(n)
            with self.assertRaisesRegex(ValueError,'DECK_CONTRACT'):
                instrument_deck(raw.replace('*CONTACT PAIR,INTERACTION=NORMAL,TYPE=SURFACE TO SURFACE','*REMOVED'))

    def test_double_instrument_rejected(self):
        raw=instrument_deck(self.fixture(16))
        with self.assertRaisesRegex(ValueError,'DECK_CONTRACT'):
            instrument_deck(raw)

    def test_modified_step_rejected(self):
        with self.assertRaisesRegex(ValueError,'DECK_CONTRACT'):
            instrument_deck(self.fixture(16).replace('*END STEP','*END STEP,NOT-EXACT'))

    def test_invalid_scope(self):
        for args in [(8,'toward'),(32,'toward'),(True,'toward'),(16,'clearance'),(16,'away')]:
            with self.assertRaisesRegex(ValueError,'FIELD_SCOPE'):deck(*args)
        with self.assertRaisesRegex(ValueError,'NO_CONTACT_PAIR'):deck(16,'unlinked')

if __name__=='__main__':unittest.main()
