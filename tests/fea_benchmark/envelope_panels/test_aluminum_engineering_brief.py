"""Fail-closed presentation-only tests for existing aluminum parametric results."""
import math
import unittest
from aluminum_engineering_brief import render


def fixture():
    u=dict(width_mm=100.,height_mm=100.,thickness_mm=2.,youngs_modulus_mpa=69000.,
           poisson_ratio=.33,pressure_n_mm2=0.0001,mesh=4,
           support='four_edges_clamped',units='N-mm-MPa',material_provenance='synthetic')
    h='a'*64
    return {'execution_status':'ALUMINUM_PARAMETRIC_RESEARCH_EVIDENCE_PASS',
      'model_scope':'RECTANGULAR_FOUR_EDGE_CLAMPED_LINEAR_ELASTIC_S8R_NLGEOM_P1',
      'inputs':u, 'engineering_acceptance':'NOT_ADMITTED',
      'global_six_component_balance':'NOT_ADMITTED',
      'aluminum_design_manual_capacity':'NOT_COMPUTED',
      'rotational_support_reaction':'UNOBSERVED',
      'artifact_provenance':{k:h for k in ('input_sha256','solver_sha256','dat_sha256','frd_sha256','sta_sha256')},
      'research_observations':{'engineering_acceptance':'NOT_ADMITTED',
        'displacement':{'observed_source':'CCX_DAT_FINAL_NALL_U',
          'nodes_covered':25,'center_xyz_mm':[0,0,.003],
          'max_abs_nodal_transverse_mm':.003,'max_nodal_magnitude_mm':.003},
        'stress':{'evidence_type':'CCX_FRD_EXTRAPOLATED_AVERAGED_EXPANDED_NODE_TENSOR',
          'units':'MPa','design_capacity':'NOT_COMPUTED',
          'integration_point_extreme':'NOT_OBSERVED','independent_numerical_oracle':'NOT_ESTABLISHED',
          'max_abs_component_label':'SXX','max_abs_component':3.,'max_abs_component_signed_value':-3.},
        'translational_support':{'evidence_type':'RECONSTRUCTED_FROM_INTERNAL_MINUS_FOLLOWER_PRESSURE',
          'independent_support_measurement':'NOT_OBSERVED',
          'external_pressure_resultant_N':[0,0,1], 'inferred_support_resultant_N':[0,0,-1],
          'residual_N':[0,0,0], 'relative_force_residual':0.}}}

class EngineeringBriefTests(unittest.TestCase):
    def test_report_and_limited_interpretation(self):
        result=render(fixture())
        self.assertIn('0.0001 N/mm²',result)
        self.assertIn('qA=1 N',result)
        self.assertIn('SXX = -3 MPa',result)
        self.assertIn('NOT_ADMITTED',result)
        self.assertIn('不是**獨立量得',result)
        self.assertIn('材料來源標籤',result)
        self.assertNotIn('synthetic',result)
    def test_reject_solver_or_scope_or_acceptance(self):
        for key,val in [('execution_status','NOT_EXECUTED_OPT_IN_REQUIRED'),
                        ('model_scope','RANDOM_FEA'),('engineering_acceptance','ADMITTED'),
                        ('rotational_support_reaction','OBSERVED')]:
            with self.subTest(key=key):
                data=fixture();data[key]=val
                with self.assertRaises(ValueError):render(data)
    def test_reject_field_relabeling_and_nonfinite(self):
        for key,val in [('integration_point_extreme','OBSERVED'),
                        ('evidence_type','GAUSS_STRESS'),('max_abs_component',math.nan),
                        ('max_abs_component_signed_value',5.)]:
            data=fixture();data['research_observations']['stress'][key]=val
            with self.subTest(key=key),self.assertRaises(ValueError):render(data)
    def test_reject_fake_independent_reaction(self):
        for key,val in [('independent_support_measurement','OBSERVED'),
                        ('relative_force_residual',1.),
                        ('inferred_support_resultant_N',[0,0,-.7])]:
            data=fixture();data['research_observations']['translational_support'][key]=val
            with self.subTest(key=key),self.assertRaises(ValueError):render(data)
    def test_reject_missing_or_modified_provenance_and_dimensions(self):
        data=fixture();data['artifact_provenance']['frd_sha256']='not a digest'
        with self.assertRaises(ValueError):render(data)
        data=fixture();data['inputs']['support']='simply_supported'
        with self.assertRaises(ValueError):render(data)
    def test_reject_displacement_claims(self):
        data=fixture();data['research_observations']['displacement']['max_abs_nodal_transverse_mm']=.001
        with self.assertRaises(ValueError):render(data)

if __name__=='__main__':unittest.main()