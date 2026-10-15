"""Independent Fourier/support geometry regression, research-only."""
from __future__ import annotations
import math
import tempfile
import unittest
from pathlib import Path
from check_u_rib_shell_links import MESHES, CASES, mesh
from check_u_rib_shell_pressure import pressure_deck
from check_u_rib_support_sensitivity import (
    _corners, simply_supported_deck, four_edges_simply_supported_series,
    compare, generate, SCOPE,
)


class UPlateSupportTests(unittest.TestCase):
    def test_fourier_three_orders_stabilize(self):
        a,b,c=[four_edges_simply_supported_series(n) for n in (19,39,79)]
        self.assertGreater(a,0)
        self.assertLess(abs(b-c)/c,.003)
        self.assertAlmostEqual(c,.0005959667,delta=.000003)

    def test_all_six_decks_only_change_boundary(self):
        old='*BOUNDARY\nPLATE_CLAMP,1,6,0.\nRIB_END_CLAMP,1,6,0.\n*STEP'
        for n in MESHES:
            for scenario in CASES:
                with self.subTest(n=n,scenario=scenario):
                    clamped=pressure_deck(n,scenario)
                    simple=simply_supported_deck(n,scenario)
                    self.assertEqual(clamped.count(old),1)
                    self.assertEqual(simple.count('*ELEMENT,TYPE=S8R'),2)
                    self.assertEqual(simple.count('*DLOAD'),1)
                    self.assertEqual(simple.count('*ELEMENT,TYPE=SPRING2'),int(scenario!='unlinked'))
                    self.assertIn('PLATE_CLAMP,3,3,0.',simple)
                    self.assertNotIn('PLATE_CLAMP,1,6,0.',simple)
                    self.assertIn('RIB_END_CLAMP,1,6,0.',simple)
                    self.assertNotIn('*CONTACT',simple)
                    self.assertNotIn('*CLOAD',simple)
                    a,b=_corners(n)
                    expected=(f'*NSET,NSET=PLATE_INPLANE_A\n{a}\n'
                              f'*NSET,NSET=PLATE_INPLANE_B\n{b}\n'
                              '*BOUNDARY\nPLATE_CLAMP,3,3,0.\n'
                              'PLATE_INPLANE_A,1,2,0.\n'
                              'PLATE_INPLANE_B,2,2,0.\n'
                              'RIB_END_CLAMP,1,6,0.\n*STEP')
                    self.assertEqual(simple.replace(expected,old),clamped)
                    self.assertEqual(simple.count('*NODE PRINT,NSET=PLATE_CENTER'),1)

    def test_explicit_two_corner_pins_both_plate_nodes(self):
        for n in MESHES:
            a,b=_corners(n)
            topo=mesh(n)
            self.assertEqual(topo['coords'][a],(0.,-150.,0.))
            self.assertEqual(topo['coords'][b],(1200.,-150.,0.))
            self.assertIn(f'*NSET,NSET=PLATE_INPLANE_A\n{a}\n',simply_supported_deck(n,'soft'))
            self.assertIn(f'*NSET,NSET=PLATE_INPLANE_B\n{b}\n',simply_supported_deck(n,'soft'))

    def test_no_unclaimed_contact_or_buckling(self):
        for case in CASES:
            x=simply_supported_deck(16,case)
            for keyword in ('*CONTACT','*PLASTIC','NLGEOM','*RIGID BODY','*EQUATION'):
                self.assertNotIn(keyword,x)

    def test_compare_allow_only_physically_ordered_synthetic_data(self):
        reference=four_edges_simply_supported_series()
        clamped={(n,c):reference*v for n in MESHES for c,v in
                 (('unlinked',.25),('soft',.24),('stiff',.23))}
        simple={(n,c):reference*v for n in MESHES for c,v in
                (('unlinked',1.05 if n==8 else 1.02),
                 ('soft',.91 if n==8 else .9),
                 ('stiff',.81 if n==8 else .8))}
        result=compare(clamped,simple)
        self.assertEqual(result['scope'],SCOPE)
        self.assertEqual(result['engineering_acceptance'],'NOT_ADMITTED')
        self.assertEqual(result['rib_end_condition_in_both'],'SYNTHETIC_FIXED_RIB_ENDS')
        self.assertGreater(result['center_deflection_mm']['16']['unlinked']['simple_to_clamped_ratio'],1)

    def test_fail_closed_data_matrix_missing_nan_or_bool(self):
        r=four_edges_simply_supported_series()
        clamped={(n,c):r*.2 for n in MESHES for c in CASES}
        simple={(n,c):r*v for n in MESHES for c,v in [('unlinked',1.1),('soft',.9),('stiff',.8)]}
        bad=[{**simple,(8,'soft'):float('nan')},
             {**simple,(8,'stiff'):True},
             {**simple,(16,'unlinked'):r*2},
             {**simple,(16,'soft'):simple[16,'unlinked']*1.2},
             {**simple,(16,'stiff'):r*.1},
             {key:val for key,val in simple.items() if key!=(8,'unlinked')}]
        for values in bad:
            with self.subTest(values=values),self.assertRaises(ValueError):
                compare(clamped,values)

    def test_reject_unadmitted_fourier_orders(self):
        for order in (0,3,12,21,40,80,True,79.0):
            with self.subTest(order=order),self.assertRaises(ValueError):
                four_edges_simply_supported_series(order)

    def test_deck_reject_invalid_mesh_or_scenario(self):
        for n,c in ((4,'soft'),(True,'soft'),(8,'bad'),(0,'unlinked')):
            with self.subTest(n=n,c=c),self.assertRaises(ValueError):
                simply_supported_deck(n,c)

    def test_fresh_workspace(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'candidate'
            generate(p,8,'soft')
            self.assertEqual((p/'panel.inp').read_text(),simply_supported_deck(8,'soft'))
            with self.assertRaises(ValueError):generate(p,8,'soft')


if __name__=='__main__':unittest.main()
