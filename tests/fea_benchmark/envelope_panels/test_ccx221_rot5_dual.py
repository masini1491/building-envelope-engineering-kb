"""Fail-closed no-solver tests for MEANROTBS dual candidate attribution."""
import pathlib, shutil, sys, tempfile, unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from ccx221_rot5_dual_instrument import patch
from verify_ccx221_rot5_dual import (analytic_48, parse_trace, reconstruct,
                                      parse_owner, deck_mode, verify)

EXAMPLE='''KB_ROT_PHASE P 1 10 1.0 100 12 10
KB_ROT_SPC P 7 50 1 -10 0.00002 0.0
KB_ROT_PHASE Q 1 10 1.0 100 12 10
KB_ROT_SPC Q 7 50 1 -10 0.00002 0.0
KB_ROT_MPC 4 1.5
KB_ROT_TERM 4 1 1 3 0.1
KB_ROT_TERM 4 2 1 2 0.2
KB_ROT_TERM 4 3 1 1 0.3
KB_ROT_TERM 4 4 2 3 0.1
KB_ROT_TERM 4 5 2 2 0.2
KB_ROT_TERM 4 6 2 1 0.3
KB_ROT_TERM 4 7 50 1 -2.0
KB_ROT_TERM 4 8 50 2 1.0
'''
OWNER='KB_ROT_OWNER 64 2 2 7 50 1 0.00002 4\n'

class Tests(unittest.TestCase):
    def assertBad(self,fn,code):
        with self.assertRaisesRegex(ValueError,'CCX221_ROT_DUAL_'+code):fn()
    def test_analytic_couple_sign(self):
        a=analytic_48()
        self.assertEqual(a['net_force_n'],0.)
        self.assertAlmostEqual(a['mpc_elimination_signed_nmm'],48.,places=11)
        self.assertAlmostEqual(a['internal_virtual_work_nmm_per_rad'],48.,places=11)
    def test_precise_coefficient_and_owner(self):
        x=parse_trace(EXAMPLE)
        out=reconstruct(parse_owner(OWNER),x,{64:2e-5},{64:1.0})
        self.assertEqual(out['node_count'],1)
        self.assertEqual(out['internal_fmpc_weighted_candidate_nmm'],3.)
        self.assertEqual(out['independent_dual_reaction'],'NOT_ESTABLISHED')
    def test_invalid_sign_coefficient(self):
        self.assertBad(lambda:parse_trace(EXAMPLE.replace('-2.0','2.0')),'ANGLE_COEFFICIENT')
    def test_missing_aux_inhomogeneous_pair(self):
        self.assertBad(lambda:parse_trace(EXAMPLE.replace('KB_ROT_TERM 4 8 50 2 1.0',
                            'KB_ROT_TERM 4 8 51 2 1.0')),'MEANROT_TOPOLOGY')
    def test_inhomogeneous_wrong_scale(self):
        self.assertBad(lambda:parse_trace(EXAMPLE.replace('KB_ROT_TERM 4 8 50 2 1.0',
                            'KB_ROT_TERM 4 8 50 2 0.5')),'ANGLE_COEFFICIENT')
    def test_duplicate_mpc_dof(self):
        self.assertBad(lambda:parse_trace(EXAMPLE.replace('KB_ROT_TERM 4 8 50 2 1.0',
                            'KB_ROT_TERM 4 8 50 1 1.0')),'MEANROT_TOPOLOGY')
    def test_truncated_mpc_terms(self):
        broken=EXAMPLE.split('KB_ROT_TERM 4 4')[0]
        self.assertBad(lambda:parse_trace(broken),'MEANROT_TOPOLOGY')
    def test_missing_second_phase(self):
        self.assertBad(lambda:parse_trace(EXAMPLE.split('KB_ROT_PHASE Q')[0]),'PHASE_COVERAGE')
    def test_duplicate_mpc(self):
        self.assertBad(lambda:parse_trace(EXAMPLE.replace('KB_ROT_TERM 4 1','KB_ROT_MPC 4 2.0\nKB_ROT_TERM 4 1',1)),'MPC_DUPLICATE_OR_SCOPE')
    def test_fmpc_nonfinite(self):
        self.assertBad(lambda:parse_trace(EXAMPLE.replace('KB_ROT_MPC 4 1.5','KB_ROT_MPC 4 NaN')),'NONFINITE')
    def test_creation_spc_slot_is_not_final_identity(self):
        x=parse_trace(EXAMPLE)
        out=reconstruct(parse_owner(OWNER.replace(' 7 50 ',' 9 50 ')),x,{64:2e-5},{64:1.0})
        self.assertEqual(out['node_count'],1)
    def test_aux_spc_mismatch(self):
        x=parse_trace(EXAMPLE)
        self.assertBad(lambda:reconstruct(parse_owner(OWNER.replace(' 7 50 ',' 8 52 ')), x,
                                          {64:2e-5},{64:1.0}),'AUX_SPC_MAPPING')
    def test_mpc_owner_mismatch(self):
        x=parse_trace(EXAMPLE)
        self.assertBad(lambda:reconstruct(parse_owner(OWNER.replace(' 1 0.00002 4',' 1 0.00002 3')),x,
                                          {64:2e-5},{64:1.0}),'AUX_MPC_MAPPING')
    def test_corrupt_owner_duplicate(self):
        self.assertBad(lambda:parse_owner(OWNER+OWNER),'OWNER_DUPLICATE')
    def test_absent_case_zip(self):
        with tempfile.TemporaryDirectory() as t:
            p=pathlib.Path(t)/'dummy.zip';p.write_bytes(b'invalid')
            self.assertBad(lambda:verify(p,p,p),'SOURCE_OR_OWNER_ZIP_SHA')
    def test_patch_invalid_source_is_atomic(self):
        with tempfile.TemporaryDirectory() as t:
            src=pathlib.Path(t)/'src';src.mkdir()
            for f in ('gen3dboun.f','results.c'):(src/f).write_text('not pinned')
            with self.assertRaisesRegex(ValueError,'CCX221_DUAL_SOURCE_PIN_MISMATCH'):
                patch(pathlib.Path(t))
            for f in ('gen3dboun.f','results.c'):self.assertEqual((src/f).read_text(),'not pinned')

if __name__=='__main__':unittest.main()
