"""No-capacity unit checks for bounded uniform-pressure S8R study."""
from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path

from check_u_rib_shell_links import deck as point_deck, mesh, MESHES, CASES
from check_u_rib_shell_pressure import (
    PRESSURE_N_MM2, NOMINAL_RESULTANT_N, SCOPE, pressure_deck,
    pressure_ritz_center, compare, generate,
)


class UPressureTests(unittest.TestCase):
    def test_uniform_resultant_from_exact_area(self):
        self.assertEqual(PRESSURE_N_MM2,1e-6)
        self.assertAlmostEqual(NOMINAL_RESULTANT_N,.36,places=12)

    def test_point_load_replaced_without_changing_any_other_deck_lines(self):
        for n in MESHES:
            for case in CASES:
                with self.subTest(n=n,case=case):
                    old=point_deck(n,case)
                    center=mesh(n)['center']
                    expected=old.replace(f'*CLOAD\n{center},3,-1.00000000\n',
                                         f'*DLOAD\nPLATE,P,{PRESSURE_N_MM2:.9f}\n')
                    self.assertNotEqual(expected,old)
                    self.assertEqual(pressure_deck(n,case),expected)
                    self.assertNotIn('*CLOAD',expected)
                    self.assertEqual(expected.count('*DLOAD'),1)

    def test_model_does_not_tie_or_contact_stud_interface(self):
        for case in CASES:
            x=pressure_deck(16,case)
            self.assertEqual(x.count('*ELEMENT,TYPE=S8R'),2)
            self.assertEqual(x.count('*ELEMENT,TYPE=SPRING2'),int(case!='unlinked'))
            self.assertNotIn('*EQUATION',x)
            self.assertNotIn('*CONTACT',x)
            self.assertNotIn('NLGEOM',x)
            self.assertNotIn('*PLASTIC',x)

    def test_rib_not_directly_pressure_loaded(self):
        x=pressure_deck(16,'soft')
        self.assertIn('*DLOAD\nPLATE,P,0.000001000\n',x)
        self.assertNotIn('RIB,P,',x)

    def test_six_mode_independent_pressure_ritz_is_finite(self):
        for modes in (1,4,6):
            value=pressure_ritz_center(modes)
            self.assertTrue(math.isfinite(value))
            self.assertGreater(value,0)
            self.assertLess(value,.05)
        self.assertNotAlmostEqual(pressure_ritz_center(1),pressure_ritz_center(6),places=8)

    def test_one_term_ritz_generalized_force_uses_surface_area(self):
        # Integral of (1 - s^2)^2 from -1 to 1 is exactly 16/15.
        qgen = PRESSURE_N_MM2 * (1200*300/4) * (16/15)**2
        self.assertAlmostEqual(qgen,.1024,places=12)

    def test_compare_bounded_positive_trend(self):
        ref=pressure_ritz_center()
        observations={(n,c): ref*factor for n in MESHES for c,factor in
                      (('unlinked',1.12 if n==8 else 1.09),
                       ('soft',1.05 if n==8 else 1.03),
                       ('stiff',.82 if n==8 else .80))}
        result=compare(observations)
        self.assertEqual(result['scope'],SCOPE)
        self.assertEqual(result['engineering_acceptance'],'NOT_ADMITTED')
        self.assertEqual(result['real_wind_pressure_admission'],'NOT_ADMITTED')
        self.assertEqual(result['real_contact_shear_slip_and_stud_capacity'],'NOT_ADMITTED')
        self.assertEqual(result['nominal_uniform_pressure_resultant_n'],.36)

    def test_reject_bad_or_incomplete_results(self):
        ref=pressure_ritz_center()
        good={(n,c):ref*f for n in MESHES for c,f in
              (('unlinked',1.1),('soft',1.),('stiff',.8))}
        variants=[
            {k:v for k,v in good.items() if k != (8,'soft')},
            {**good,(16,'soft'):float('nan')},
            {**good,(16,'soft'):good[16,'unlinked']*1.2},
            {**good,(16,'unlinked'):ref*2.0},
            {**good,(8,'stiff'):ref*.05},
            {**good,(16,'stiff'):True},
        ]
        for candidate in variants:
            with self.subTest(candidate=candidate),self.assertRaises(ValueError):
                compare(candidate)

    def test_fail_closed_ritz_and_deck_parameters(self):
        for invalid in (0,2,True,7,8.0):
            with self.subTest(terms=invalid),self.assertRaises(ValueError):
                pressure_ritz_center(invalid)
        for n,c in ((4,'soft'),(0,'soft'),(8,'invalid'),(True,'soft')):
            with self.subTest(n=n,c=c),self.assertRaises(ValueError):
                pressure_deck(n,c)

    def test_fresh_workspace_and_deterministic_deck(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'new_case'
            generate(folder,8,'soft')
            self.assertEqual((folder/'panel.inp').read_text(encoding='utf-8'),pressure_deck(8,'soft'))
            with self.assertRaises(ValueError):generate(folder,8,'soft')


if __name__=='__main__':unittest.main()
