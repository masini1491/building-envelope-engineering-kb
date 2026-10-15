"""Only synthetic scalar-spring station equations, no physical stud admission."""
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import check_u_rib_stud_link as m

class TestDiscreteSyntheticLink(unittest.TestCase):
    def test_known_canonical_stations(self):
        self.assertEqual(m.positions(),(150.,450.,750.,1050.))
        self.assertEqual(len(m.edges('soft')[1]),18)

    def test_case_deck_and_restrictions(self):
        for case in m.CASES:
            with self.subTest(case=case):
                deck=m.deck(case)
                self.assertEqual(deck.count('*CLOAD'),1)
                self.assertEqual(deck.count('*ELEMENT,TYPE=SPRING1'),2)
                self.assertEqual(deck.count('*NODE PRINT,NSET='),2)
                self.assertIn('2,3,1.00000000',deck)
                self.assertNotIn('S8R',deck)
                self.assertEqual(deck.count('*ELEMENT,TYPE=SPRING2'),2 if case=='unlinked' else 3)
        with self.assertRaises(ValueError):m.deck('production')

    def test_oracle_independent_nodal_balance(self):
        for case in m.CASES:
            x=m.oracle(case);A,f=m.make_matrix(case)
            self.assertEqual(len(x),8)
            for i in range(8):
                self.assertAlmostEqual(sum(A[i][j]*x[j] for j in range(8)),f[i],places=10)
            self.assertAlmostEqual(sum(m.P_GROUND*x[i]+m.R_GROUND*x[4+i] for i in range(4)),m.LOAD,places=10)

    def test_monotone_stiffening_and_zero_uncoupled_rib(self):
        u=[m.oracle(c)[1] for c in m.CASES]
        self.assertGreater(u[0],u[1]);self.assertGreater(u[1],u[2]);self.assertGreater(u[2],0)
        self.assertTrue(all(v==0 for v in m.oracle('unlinked')[4:]))
        self.assertGreater(max(abs(v) for v in m.oracle('soft')[4:]),0)

    def test_stiffness_and_energy_oracle(self):
        for c in m.CASES:
            x=m.oracle(c)
            E=sum(.5*k*(x[ns[0]-1] if len(ns)==1 else x[ns[0]-1]-x[ns[1]-1])**2 for ns,k,g in m.edges(c)[1])
            self.assertAlmostEqual(2*E,m.LOAD*x[1],places=10)

    def test_fresh_workspaces(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'trial';m.generate(path,'soft')
            self.assertEqual((path/'panel.inp').read_text(),m.deck('soft'))
            with self.assertRaises(ValueError):m.generate(path,'soft')
            with self.assertRaises(ValueError):m.generate(Path(d)/'bad','bogus')

    def test_field_parser_rejects_missing_or_duplicate(self):
        content=(' displacements (vx,vy,vz) for set PLATE and time 1.0000000E+00\n\n'+
                 ''.join(f'{i} 0. 0. {i*.001:.8f}\n' for i in range(1,5))+'\n')
        self.assertEqual(m._printed(content,'PLATE'),{i:i*.001 for i in range(1,5)})
        with self.assertRaises(ValueError):m._printed(content,'RIB')
        with self.assertRaises(ValueError):m._printed(content.replace('1 0. 0. 0.00100000','1 0. 0. NaN'),'PLATE')

    def test_no_artifact_claim_before_solver(self):
        with tempfile.TemporaryDirectory() as d:
            m.generate(Path(d)/'stud_link_soft','soft')
            with self.assertRaisesRegex(ValueError,'ARTIFACT_MISSING'):m.verify(Path(d),'soft')

    def test_incomplete_study_is_rejected(self):
        mock={'scope':'synthetic','plate_loaded_station_u3_mm':0.1,'derived_k_relative_u_link_n':{'150.0':0.0}}
        with patch.object(m,'verify',return_value=mock):
            with self.assertRaisesRegex(ValueError,'COMPLIANCE_TREND'):m.assess(Path('/irrelevant'))

if __name__=='__main__':unittest.main()
