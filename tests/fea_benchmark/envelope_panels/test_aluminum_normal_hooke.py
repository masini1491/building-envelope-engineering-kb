import math
import unittest
from check_aluminum_normal_hooke import check_normal_hooke

class HookeTests(unittest.TestCase):
    def test_known_normal_compliance(self):
        e=70000.;nu=.32;s={1:(11.,4.,-2.,8.,1.,-3.),2:(2.,5.,7.,0.,0.,0.)}
        strain={node:tuple([(v[i]-nu*(v[(i+1)%3]+v[(i+2)%3]))/e for i in range(3)]+[0.,0.,0.])
                for node,v in s.items()}
        ans=check_normal_hooke(s,strain,e=e,nu=nu)
        self.assertEqual(ans["nodes_covered"],2)
        self.assertLess(ans["normalized_max_residual"],1.e-12)
        self.assertEqual(ans["shear_components"],"NOT_CHECKED")
    def test_fail_closed(self):
        s={1:(11.,4.,-2.,8.,1.,-3.)}
        valid=(11.-.32*(4.-2.))/70000.
        for epsi in [valid+.01,math.nan]:
            with self.subTest(epsi=epsi),self.assertRaises(ValueError):
                check_normal_hooke(s,{1:(epsi,0.,0.,0.,0.,0.)},e=70000.,nu=.32)
        with self.assertRaises(ValueError):
            check_normal_hooke(s,{2:(0.,)*6},e=70000.,nu=.32)
        with self.assertRaises(ValueError):
            check_normal_hooke({1:(0.,)*6},{1:(0.,)*6},e=70000.,nu=.32)
if __name__=="__main__":unittest.main()
