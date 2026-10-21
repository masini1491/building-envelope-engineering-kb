"""Negative controls for CSTR sampling bias and fake contact-force integration."""
import unittest
from contact_ip_sampling_guard import geometric_face_proxy

class SamplingGuardTests(unittest.TestCase):
    def fixture(self):
        c={1:(93.75,-23.5),2:(168.75,0.),3:(393.75,23.5)}
        return c,{1:[.01]*2,2:[.02]*40,3:[.03]*3}
    def test_distinct_area_and_force_counters(self):
        c,g=self.fixture();z=geometric_face_proxy(c,g,16,1.,2.)
        self.assertFalse(z['proxy_is_contact_force'])
        self.assertAlmostEqual(z['all_active_faces_geometric_area_mm2'],37.5*50)
        self.assertEqual(z['zones']['transition_150_300_mm']['cstr_record_count'],40)
        self.assertAlmostEqual(z['zones']['transition_150_300_mm']['whole_face_area_weighted_sample_mean_n_mm2'],.02)
    def test_reject_bad_membership(self):
        c,g=self.fixture()
        with self.assertRaisesRegex(ValueError,'INPUT_MEMBERSHIP'):
            geometric_face_proxy(c,{**g,4:[.04]},16,1.,2.)
    def test_reject_negative_record(self):
        c,g=self.fixture()
        with self.assertRaisesRegex(ValueError,'CSTR_VALUE'):
            geometric_face_proxy(c,{**g,2:[-.01]},16,1.,2.)
    def test_reject_off_mesh_point(self):
        c,g=self.fixture();c[1]=(100.,-23.5)
        with self.assertRaisesRegex(ValueError,'X_NOT_MESH_MIDPOINT'):
            geometric_face_proxy(c,g,16,1.,2.)
    def test_reject_mesh_scope(self):
        c,g=self.fixture()
        with self.assertRaisesRegex(ValueError,'SCOPE'):
            geometric_face_proxy(c,g,8,1.,2.)
    def test_matching_proxy_still_not_oracle(self):
        c,g=self.fixture()
        z=geometric_face_proxy(c,g,16,37.5*(3*.01+44*.02+3*.03),2.)
        self.assertAlmostEqual(z['invalid_proxy_to_solver_force_ratio'],1.)
        self.assertFalse(z['proxy_is_contact_force'])
        self.assertEqual(z['CSTR_point_coordinates_weights'],'NOT_AVAILABLE')

if __name__=='__main__':unittest.main()
