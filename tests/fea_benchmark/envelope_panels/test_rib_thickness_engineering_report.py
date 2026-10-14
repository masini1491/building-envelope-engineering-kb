"""Bounded report acceptance and negative cases; no solver impersonation."""
import copy
import math
import tempfile
import unittest
from pathlib import Path

from rib_thickness_engineering_report import _observations, render, main, THICKNESSES, MESHES, HEIGHTS


def fixture():
    # Public synthetic reference observations from PR #114, not actual output
    # artifacts; test-only SHA placeholders have no solver provenance claim.
    measured={
        2.0: {8: (0.0002296706,0.0001741728,0.0001035602),
              16:(0.0002382199,0.0001840568,0.0001079533)},
        3.0: {8: (0.00006875382,0.00005839943,0.00004222735),
              16:(0.00007121307,0.00006176400,0.00004421178)}
    }
    fields={str(t):{str(n):{str(h):measured[t][n][i] for i,h in enumerate(HEIGHTS)}
                   for n in MESHES} for t in THICKNESSES}
    cases={f't{t}_n{n}_h{h}':{
          'center_mm':measured[t][n][i], 'thickness_mm':t, 'height_mm':h, 'mesh':n,
          'sha256':{k: 'a'*64 for k in ('inp','dat','sta','frd')}}
          for t in THICKNESSES for n in MESHES for i,h in enumerate(HEIGHTS)}
    ritz={"2.0":0.00025749110714824876,"3.0":7.629366137725889e-05}
    return {
      'scope':'SYNTHETIC_CENTER_RIB_TWO_DISCRETE_THICKNESSES_ONLY',
      'plate_width_mm':100.0,'plate_height_mm':100.0,
      'pressure_n_mm2':.0001,'youngs_modulus_mpa':69000.0,'poisson_ratio':.33,
      'center_displacement_mm':fields,
      'flat_ritz_by_thickness':{t:{'ritz_center_mm':v,
          'relative_difference':abs(fields[t]['16']['0']-v)/v} for t,v in ritz.items()},
      'flat_plate_Kirchhoff_t_cubed_ratio':(2/3)**3,
      'flat_plate_solver_t3_over_t2_ratio':measured[3.0][16][0]/measured[2.0][16][0],
      'two_mesh_differences':{f't{t}_h{h}':abs(measured[t][16][i]-measured[t][8][i])/measured[t][16][i]
                            for t in THICKNESSES for i,h in enumerate(HEIGHTS)},
      'rib_web_connection':'IDEAL_SHARED_S8R_NODES',
      'rigid_rotation_or_fastener_force':'NOT_ADMITTED',
      'pressure_balance_six_components':'NOT_ADMITTED',
      'material_capacity':'NOT_ADMITTED',
      'engineering_acceptance':'NOT_ADMITTED','cases':cases}


class EngineeringReportTests(unittest.TestCase):
    def test_reports_two_distinct_benefits_and_limits(self):
        out = render(fixture())
        self.assertIn('增厚後中心撓度降幅',out)
        self.assertIn('2 mm 加肋降幅',out)
        self.assertIn('3 mm 加肋降幅',out)
        self.assertIn('0.298938376',out)
        self.assertIn('NOT_ADMITTED',out)
        self.assertIn('不重新讀取或驗證原始求解器檔案',out)
    def test_rejects_wrong_scope_or_status(self):
        for key,value in [('scope','UNKNOWN'),('engineering_acceptance','ADMITTED'),
                          ('material_capacity','ADMITTED'),('rib_web_connection','BOLTED'),
                          ('pressure_balance_six_components','ADMITTED')]:
            with self.subTest(key=key):
                x=fixture();x[key]=value
                with self.assertRaises(ValueError):render(x)
    def test_rejects_missing_or_extra_case(self):
        x=fixture();x['cases'].pop('t2.0_n8_h0')
        with self.assertRaisesRegex(ValueError,'SCHEMA'):render(x)
        x=fixture();x['cases']['unverified']={}
        with self.assertRaisesRegex(ValueError,'SCHEMA'):render(x)
    def test_rejects_fabricated_or_swapped_observation(self):
        x=fixture();x['cases']['t3.0_n16_h4']['center_mm']=x['cases']['t2.0_n16_h4']['center_mm']
        with self.assertRaisesRegex(ValueError,'CASE_CENTER'):render(x)
        x=fixture();x['cases']['t3.0_n16_h4']['mesh']=8
        with self.assertRaisesRegex(ValueError,'CASE_MESH'):render(x)
    def test_rejects_corrupt_artifact_digest(self):
        x=fixture();x['cases']['t3.0_n16_h8']['sha256']['dat']='deadbeef'
        with self.assertRaisesRegex(ValueError,'DIGEST'):render(x)
    def test_rejects_nonfinite_or_false_numerics(self):
        x=fixture();x['center_displacement_mm']['2.0']['16']['8']=math.nan
        with self.assertRaises(ValueError):render(x)
        x=fixture();x['flat_plate_solver_t3_over_t2_ratio']=True
        with self.assertRaises(ValueError):render(x)
    def test_rejects_wrong_mesh_and_ritz(self):
        x=fixture();x['two_mesh_differences']['t2.0_h4']=.0
        with self.assertRaisesRegex(ValueError,'MESH_DIFFERENCE'):render(x)
        x=fixture();x['flat_ritz_by_thickness']['3.0']['ritz_center_mm']*=2
        with self.assertRaises(ValueError):render(x)
    def test_rejects_fake_thickness_and_height_trends(self):
        x=fixture();x['center_displacement_mm']['3.0']['16']['4']*=4
        x['cases']['t3.0_n16_h4']['center_mm']=x['center_displacement_mm']['3.0']['16']['4']
        with self.assertRaises(ValueError):render(x)
    def test_cli_rejects_malicious_json_or_invalid_file(self):
        import json
        import sys
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as folder:
            src = Path(folder)/'in.json'
            src.write_text('{"scope":"one","scope":"two"}', encoding='utf8')
            with patch.object(sys,'argv',['report',str(src)]),self.assertRaises(SystemExit):main()
            src.write_text('{"x":NaN}', encoding='utf8')
            with patch.object(sys,'argv',['report',str(src)]),self.assertRaises(SystemExit):main()
            src.write_text(json.dumps(fixture()), encoding='utf8')
            with patch.object(sys,'argv',['report',str(src)]),patch('builtins.print') as m:
                self.assertEqual(main(),0)
                self.assertIn('來源 JSON SHA-256',m.call_args.args[0])
            with patch.object(sys,'argv',['report',str(src)+'_missing']),self.assertRaises(SystemExit):main()


if __name__ == '__main__': unittest.main()
