"""Stage 69 fail-closed synthetic MPC force and independent oracle tests."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from check_mpc_reaction import (CASES,K_N_PER_MM,LOAD_N,EXPECTED_U_MM,deck,
                                generate,read_field,near,crosscheck,completed)

class MPCReactionTests(unittest.TestCase):
    def test_analytic_oracle(self):
        self.assertAlmostEqual(K_N_PER_MM*EXPECTED_U_MM, LOAD_N)
        self.assertAlmostEqual(EXPECTED_U_MM,0.005)
    def test_isolated_generator(self):
        for case in CASES:
            s=deck(case)
            self.assertEqual(s.count('*EQUATION'),int(case=='equation'))
            self.assertIn('2,3,1.0,3,3,-1.0',s) if case=='equation' else self.assertNotIn('*EQUATION',s)
            self.assertNotIn('*RIGID BODY',s)
            self.assertNotIn('NLGEOM',s)
            with tempfile.TemporaryDirectory() as p:
                d=Path(p)/'new'
                generate(d,case)
                self.assertEqual((d/'panel.inp').read_text(),s)
                with self.assertRaisesRegex(ValueError,'FRESH_DIRECTORY'):
                    generate(d,case)
    def test_unknown_case_rejected(self):
        with self.assertRaisesRegex(ValueError,'OUTSIDE_SCOPE'):
            deck('rigid_body')
    def test_data_parser_failclosed(self):
        s='displacements (vx,vy,vz) for set SLAVE and time  0.1000000E+01\n\n 2 0 0 0.005\n\n'
        self.assertEqual(read_field(s,'displacements','SLAVE')[2][2],.005)
        with self.assertRaisesRegex(ValueError,'FINAL_HEADER'):
            read_field(s,'forces','SLAVE')
        self.assertEqual(read_field(s,'forces','SLAVE',optional=True),{})
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):
            read_field(s.replace('2 0 0 0.005','2 0 0 0.005\n 2 0 0 0.005'),'displacements','SLAVE')
    def test_solver_completion_required(self):
        with tempfile.TemporaryDirectory() as p:
            f=Path(p)/'a.sta';f.write_text('partial progress')
            with self.assertRaisesRegex(ValueError,'COMPLETION'):
                completed(f)
            f.write_text('1 1 1 1 1.0 1 1')
            completed(f)
    def test_control_comparison_and_corruption(self):
        a={'signed_external_and_clean_support_sum_n':0.,'observed_slave_u3_mm':.005,
           'raw_solver_spc_rf3_n':-1.25}
        self.assertEqual(crosscheck({'control':a,'equation':a})['engineering_capacity'],'NOT_ADMITTED')
        with self.assertRaisesRegex(ValueError,'FORCE_BALANCE'):
            crosscheck({'control':a,'equation':{**a,'signed_external_and_clean_support_sum_n':.4}})
        with self.assertRaisesRegex(ValueError,'SUPPORT_FORCE'):
            crosscheck({'control':a,'equation':{**a,'raw_solver_spc_rf3_n':-.8}})
        with self.assertRaisesRegex(ValueError,'COVERAGE'):
            crosscheck({'control':a})

if __name__=='__main__':unittest.main()
