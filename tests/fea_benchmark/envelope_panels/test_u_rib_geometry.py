"""Bounded, independent geometry and hostile-input tests; no solver admission."""
import json
import math
import tempfile
import unittest
from pathlib import Path

from u_rib_geometry import DEFAULTS, analyze, load, _polygon_properties, SCOPE

class UGeometryTests(unittest.TestCase):
    def test_common_dimensions_reference(self):
        r=analyze(DEFAULTS)
        self.assertEqual(r['scope'],SCOPE)
        self.assertEqual(r['cross_section']['area_mm2'],432.0)
        self.assertAlmostEqual(r['cross_section']['centroid_z_from_panel_back_mm'],17.819444444444443)
        self.assertEqual(r['stud_layout']['status'],'FIRST_STUD_OFFSET_AND_LENGTH_REQUIRED')
        self.assertEqual(r['stud_layout']['positions_mm'],[])
        self.assertEqual(r['engineering_acceptance'],'NOT_ADMITTED')
        self.assertEqual(r['solver_execution'],'NOT_RUN')
    def test_explicit_synthetic_positions(self):
        cfg={**DEFAULTS,'rib_length_mm':900.0,'first_stud_offset_mm':150.0}
        r=analyze(cfg)
        self.assertEqual([p['y_mm'] for p in r['stud_layout']['positions_mm']],[150.,450.,750.])
        self.assertTrue(all(p['x_mm']==0 and p['z_mm']==0 for p in r['stud_layout']['positions_mm']))
        self.assertEqual(r['stud_layout']['last_edge_distance_mm'],150.)
        self.assertEqual(r['stud_layout']['connection_stiffness'],'NOT_MODELED')
    def test_adjustable_dimensions_and_pitch(self):
        cfg={**DEFAULTS,'section_width_mm':65.0,'section_height_mm':40.,
             'rib_thickness_mm':2.5,'panel_thickness_mm':4.,'stud_pitch_mm':250.,
             'rib_length_mm':1050.,'first_stud_offset_mm':100.}
        r=analyze(cfg)
        self.assertAlmostEqual(r['cross_section']['area_mm2'],65*2.5+2*2.5*(40-2.5))
        self.assertEqual([p['y_mm'] for p in r['stud_layout']['positions_mm']],[100.,350.,600.,850.])
        self.assertEqual(r['stud_layout']['last_edge_distance_mm'],200.)
        self.assertEqual(r['inputs_mm']['panel_thickness_mm'],4.)
    def test_polygon_independent_oracle_analytic_rectangle(self):
        poly=[[-2.,0.],[2.,0.],[2.,3.],[-2.,3.]]
        a,x,z,ix,iz=_polygon_properties(poly)
        self.assertAlmostEqual(a,12.)
        self.assertAlmostEqual(x,0.)
        self.assertAlmostEqual(z,1.5)
        self.assertAlmostEqual(ix,4*27/12)
        self.assertAlmostEqual(iz,3*64/12)
    def test_fail_closed_bad_numbers_and_degenerate(self):
        for key,val in [('section_width_mm',3.),('section_height_mm',3.),
                        ('rib_thickness_mm',0.),('panel_thickness_mm',False),
                        ('stud_pitch_mm',math.nan),('section_width_mm',float('inf')),
                        ('stud_pitch_mm',True),('section_height_mm',301.)]:
            with self.subTest(key=key,value=val),self.assertRaises(ValueError):
                analyze({**DEFAULTS,key:val})
    def test_fail_closed_missing_extra_and_layout(self):
        for cfg in ({}, {'section_width_mm':50},
                    {**DEFAULTS,'user_id':'private'},
                    {**DEFAULTS,'rib_length_mm':900},
                    {**DEFAULTS,'first_stud_offset_mm':100},
                    {**DEFAULTS,'rib_length_mm':900,'first_stud_offset_mm':900},
                    {**DEFAULTS,'rib_length_mm':900,'first_stud_offset_mm':-1}):
            with self.subTest(cfg=cfg),self.assertRaises(ValueError):analyze(cfg)
    def test_end_stud_not_invented(self):
        cfg={**DEFAULTS,'rib_length_mm':900.,'first_stud_offset_mm':0.}
        p=analyze(cfg)['stud_layout']['positions_mm']
        self.assertEqual([x['y_mm'] for x in p],[0.,300.,600.])
        self.assertTrue(all(x['y_mm']<900 for x in p))
    def test_bounded_json_and_duplicate_or_nonfinite(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/'geometry.json'
            f.write_text(json.dumps(DEFAULTS))
            self.assertEqual(load(f)['scope'],SCOPE)
            for payload in ('{"section_width_mm":50,"section_width_mm":60}',
                            json.dumps(DEFAULTS).replace('50.0','NaN',1),
                            '{}', ' '*4100):
                f.write_text(payload)
                with self.subTest(payload=payload[:30]),self.assertRaises(ValueError):load(f)
    def test_no_capacity_or_fe_deck_pretence(self):
        r=analyze(DEFAULTS)
        self.assertEqual(r['geometry_conventions']['rib_to_panel_contact'],'NOT_MODELED')
        self.assertEqual(r['fastener_loads'],'NOT_COMPUTED')
        self.assertEqual(r['design_stress_and_buckling'],'NOT_COMPUTED')
        self.assertFalse(r['software_bounds_are_engineering_limits'])

if __name__=='__main__':unittest.main()
