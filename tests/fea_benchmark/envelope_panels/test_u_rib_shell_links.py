"""Topology, analytic plate screen and fail-closed synthetic U shell link checks."""
from __future__ import annotations
import math
import tempfile
import unittest
from pathlib import Path
from check_u_rib_shell_links import (
    CASES,MESHES,STUD_STIFFNESS,SCOPE,LENGTH,PANEL_WIDTH,
    mesh,deck,generate,compare,ritz_point_load_center,
)


class ShellLinkTests(unittest.TestCase):
    def test_two_disjoint_s8r_shells(self):
        for n in MESHES:
            with self.subTest(n=n):
                m=mesh(n)
                self.assertEqual(len(m['plate']),n*8)
                self.assertEqual(len(m['rib']),4*n)
                self.assertFalse(set(m['panel_studs']) & set(m['rib_studs']))
                self.assertEqual(len(m['clamped_plate']),4*(n+8))
                self.assertEqual(len(m['clamped_rib_end']),18)
                self.assertEqual(len(set(m['coords'])),len(m['coords']))
                self.assertFalse(set(m['clamped_plate'])&set(m['panel_studs']))

    def test_nominal_dimensions_and_stud_positions(self):
        for n in MESHES:
            m=mesh(n)
            for name in ('plate','rib'):
                self.assertEqual(m['coords'][m[('panel' if name=='plate' else name)+'_studs'][0]][0],150.)
            for a,b,x in zip(m['panel_studs'],m['rib_studs'],(150.,450.,750.,1050.)):
                self.assertEqual(m['coords'][a],(x,0.,0.))
                self.assertEqual(m['coords'][b],(x,0.,3.))
            yz={(y,z) for x,y,z in m['coords'].values()}
            self.assertIn((-23.5,50.),yz)
            self.assertIn((23.5,50.),yz)
            self.assertIn((-23.5,3.),yz)
            self.assertIn((23.5,3.),yz)
            self.assertEqual(LENGTH,1200.)
            self.assertEqual(PANEL_WIDTH,300.)

    def test_exactly_four_synthetic_links_and_no_fictitious_contact(self):
        a=deck(8,'unlinked');b=deck(8,'soft');c=deck(8,'stiff')
        for text in (a,b,c):
            self.assertEqual(text.count('*ELEMENT,TYPE=S8R'),2)
            self.assertEqual(text.count('*STEP'),1)
            self.assertEqual(text.count('*CLOAD'),1)
            self.assertNotIn('*EQUATION',text)
            self.assertNotIn('*CONTACT',text)
            self.assertNotIn('NLGEOM',text)
        self.assertNotIn('*ELEMENT,TYPE=SPRING2',a)
        for text in (b,c):
            section=text.split('*ELEMENT,TYPE=SPRING2,ELSET=STUD_Z\n')[1].split('*MATERIAL,NAME=')[0]
            self.assertEqual(len(section.splitlines()),4)
            self.assertIn('*SPRING,ELSET=STUD_Z\n3,3\n',text)
        self.assertIn('50.00000000',b)
        self.assertIn('5000.00000000',c)

    def test_nominal_ritz_reference_positive(self):
        v=ritz_point_load_center()
        self.assertGreater(v,0.0005)
        self.assertLess(v,.01)

    def test_bounded_generation_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'test'
            generate(path,8,'soft')
            self.assertEqual((path/'panel.inp').read_text(),deck(8,'soft'))
            with self.assertRaises(ValueError):generate(path,8,'soft')

    def test_reject_bad_model_inputs(self):
        for n,c in ((0,'soft'),(4,'soft'),(True,'soft'),(8,'other'),(16,'x')):
            with self.subTest(n=n,c=c),self.assertRaises(ValueError):deck(n,c)

    def test_bounded_compliance_screen(self):
        ref=ritz_point_load_center()
        valid={(n,c):ref*scale for n in MESHES for c,scale in (
            ('unlinked',1.15 if n==8 else 1.12),
            ('soft',.97 if n==8 else .95),
            ('stiff',.70 if n==8 else .69))}
        s=compare(valid)
        self.assertEqual(s['scope'],SCOPE)
        self.assertEqual(s['engineering_acceptance'],'NOT_ADMITTED')
        self.assertEqual(s['real_stud_shear_bending_and_capacity'],'NOT_ADMITTED')
        self.assertEqual(s['synthetic_stud_k_n_per_mm'],STUD_STIFFNESS)

    def test_reject_spurious_claims_or_missing_observations(self):
        ref=ritz_point_load_center()
        good={(n,c):ref*scale for n in MESHES for c,scale in (
             ('unlinked',1.1),('soft',1.0),('stiff',.85))}
        bad=[{**good,(16,'stiff'):float('nan')},
             {**good,(16,'stiff'):good[16,'soft']*1.01},
             {**good,(8,'unlinked'):20*ref},
             {**good,(16,'unlinked'):9*ref},
             {**good,(16,'soft'):good[16,'soft']*.1}]
        for data in bad:
            with self.assertRaises(ValueError):compare(data)
        with self.assertRaises(ValueError):compare({k:v for k,v in good.items() if k!=(8,'soft')})

    def test_no_measured_stud_stiffness_or_capacity(self):
        for k in STUD_STIFFNESS.values():self.assertGreaterEqual(k,0.)
        a=deck(16,'soft')
        self.assertNotIn('*PLASTIC',a)
        self.assertNotIn('*RIGID BODY',a)
        self.assertNotIn('U_RIB_REAL_STUD_CAPACITY',a)


if __name__=='__main__':unittest.main()
