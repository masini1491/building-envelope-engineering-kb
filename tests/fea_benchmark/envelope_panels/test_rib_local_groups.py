"""Stage 66 bounded paired rib-end displacement and derived load tests."""
import unittest
from check_rib_local_groups import local_groups,assess,K_PER_NODE
class Stage66Tests(unittest.TestCase):
    def fixtures(self):
        coords={}
        vec={}
        selected=set()
        for x,offset,sign in ((0.,0,1.),(100.,100,-1.)):
            for z in range(1,9):
                nid=offset+z
                coords[nid]=(x,50.,float(z))
                vec[nid]=(sign*z*.00001,0.,.000001)
                if z<=4:selected.add(nid)
        return coords,vec,selected
    def test_opposite_local_loads_not_zero(self):
        c,v,s=self.fixtures()
        out=local_groups(c,s,v)
        self.assertAlmostEqual(out["derived_total_signed_k_u_n"],0.)
        self.assertAlmostEqual(out["derived_total_signed_z_k_u_n_mm"],0.)
        self.assertGreater(out["derived_total_abs_k_u_n"],0.)
        self.assertGreater(out["per_end"]["x0"]["derived_signed_k_u_n"],0.)
        self.assertLess(out["per_end"]["x100"]["derived_signed_k_u_n"],0.)
        self.assertEqual(len(out["per_height"]),8)
    def test_stiffness_energy_identity(self):
        c,v,s=self.fixtures()
        expected=sum(.5*K_PER_NODE*v[n][0]**2 for n in s)
        self.assertAlmostEqual(local_groups(c,s,v,expected)["derived_spring_energy_n_mm"],expected)
        with self.assertRaisesRegex(ValueError,"ENERGY_IDENTITY"):
            local_groups(c,s,v,expected*3)
    def test_reject_asymmetric_or_incomplete(self):
        c,v,s=self.fixtures()
        v[101]=(0.001,0.,.000001)
        with self.assertRaisesRegex(ValueError,"ASYMMETRY"):
            local_groups(c,s,v)
        c,v,s=self.fixtures()
        del v[1]
        with self.assertRaisesRegex(ValueError,"COVERAGE"):
            local_groups(c,s,v)
        c,v,s=self.fixtures()
        s.remove(1)
        with self.assertRaisesRegex(ValueError,"COVERAGE|DISTRIBUTION"):
            local_groups(c,s,v)
    def test_reject_false_local_signal(self):
        c,v,s=self.fixtures()
        for i in s:v[i]=(0.,0.,0.)
        with self.assertRaisesRegex(ValueError,"LOCAL_SPRING_RESPONSE"):
            local_groups(c,s,v)
if __name__=="__main__":unittest.main()
