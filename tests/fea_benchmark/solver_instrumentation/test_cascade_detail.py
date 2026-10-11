"""Stage 31 per-MPC cascade transition diagnostic tests."""
import unittest
import tempfile
from pathlib import Path
from check_cascade_detail import examine

class DetailTests(unittest.TestCase):
    summary="CASCADE_V1,1,IN,2,16,8\nCASCADE_V1,1,OUT,2,8,4\n"
    detail=("CASCADE_DETAIL_V1,1,IN,1,8\nCASCADE_DETAIL_V1,1,IN,2,8\n"
            "CASCADE_DETAIL_V1,1,OUT,1,4\nCASCADE_DETAIL_V1,1,OUT,2,4\n")
    def sample(self,d,details=None):
        a=Path(d)/"summary";b=Path(d)/"details"
        a.write_text(self.summary);b.write_text(details if details is not None else self.detail)
        return a,b
    def test_8_to_4_observed_but_not_admitted(self):
        with tempfile.TemporaryDirectory() as d:
            result=examine(*self.sample(d))
            self.assertEqual(result["observed_8_to_4_transitions"],2)
            self.assertEqual(result["moment_reaction"],"UNOBSERVED")
    def test_missing_exit_mpc_fails(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=self.sample(d,self.detail.replace("CASCADE_DETAIL_V1,1,OUT,2,4\n",""))
            with self.assertRaisesRegex(ValueError,"UNMATCHED_MPC_IDS"):examine(a,b)
    def test_duplicate_mpc_fails(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=self.sample(d,self.detail+"CASCADE_DETAIL_V1,1,OUT,1,4\n")
            with self.assertRaisesRegex(ValueError,"DUPLICATE_MPC"):examine(a,b)
    def test_invalid_chain_fails(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=self.sample(d,self.detail.replace("IN,1,8","IN,1,200"))
            with self.assertRaisesRegex(ValueError,"INVALID_VALUE"):examine(a,b)
    def test_stable_case_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=self.sample(d,self.detail.replace(",OUT,1,4",",OUT,1,8").replace(",OUT,2,4",",OUT,2,8"))
            a.write_text("CASCADE_V1,1,IN,2,16,8\nCASCADE_V1,1,OUT,2,16,8\n")
            result=examine(a,b)
            self.assertEqual(result["changed_mpc_term_count_pairs"],0)

if __name__=="__main__":unittest.main()
