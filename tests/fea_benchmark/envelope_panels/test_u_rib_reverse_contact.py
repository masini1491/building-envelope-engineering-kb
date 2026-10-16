import unittest
from check_u_rib_reverse_contact import deck
class Reversal(unittest.TestCase):
    def test_scope_and_exact_pair_only(self):
        for n in (8,16):
            for case in ("toward","away"):
                s=deck(n,case)
                self.assertIn("PLATE_TOP,RIB_BASE_UNDERSIDE",s)
                self.assertIn("*CONTACT PRINT,SLAVE=PLATE_TOP,MASTER=RIB_BASE_UNDERSIDE",s)
                self.assertNotIn("*CLOAD",s)
                self.assertNotIn("SPRING2",s)
        for n,case in ((4,"toward"),(8,"unlinked"),(True,"away")):
            with self.assertRaises(ValueError):deck(n,case)
if __name__=="__main__":unittest.main()
