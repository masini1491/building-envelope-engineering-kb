"""Scope and exact-deck-delta verification for reversed S8R contact sides."""
import unittest
from check_u_rib_reverse_contact import deck
from check_u_rib_base_contact import deck as source_deck

class Reversal(unittest.TestCase):
    def test_scope_and_exact_pair_only(self):
        old_pair="RIB_BASE_UNDERSIDE,PLATE_TOP"
        new_pair="PLATE_TOP,RIB_BASE_UNDERSIDE"
        old_print="*CONTACT PRINT,SLAVE=RIB_BASE_UNDERSIDE,MASTER=PLATE_TOP"
        new_print="*CONTACT PRINT,SLAVE=PLATE_TOP,MASTER=RIB_BASE_UNDERSIDE"
        for n in (8,16):
            for case in ("toward","away"):
                with self.subTest(n=n,case=case):
                    base=source_deck(n,case)
                    new=deck(n,case)
                    self.assertEqual(base.splitlines().count(old_pair),1)
                    self.assertEqual(base.splitlines().count(old_print),1)
                    self.assertEqual(new.splitlines().count(new_pair),1)
                    self.assertEqual(new.splitlines().count(new_print),1)
                    self.assertNotIn(old_pair+"\n",new)
                    self.assertNotIn(old_print+"\n",new)
                    self.assertNotIn("*CLOAD",new)
                    self.assertNotIn("SPRING2",new)
                    self.assertEqual(base.replace(old_pair+"\n",new_pair+"\n",1).replace(
                        old_print+"\n",new_print+"\n",1),new)
        for n,case in ((4,"toward"),(8,"unlinked"),(True,"away")):
            with self.assertRaises(ValueError):deck(n,case)

if __name__=="__main__":unittest.main()
