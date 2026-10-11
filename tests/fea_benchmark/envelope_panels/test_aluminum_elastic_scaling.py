import math
import unittest
from check_aluminum_elastic_scaling import validate_response_scaling

class ScalingTests(unittest.TestCase):
    def test_six_component_tensor_and_displacements(self):
        a={1:(1.,-2.,3.,.5,-.25,.125),2:(.2,.3,.4,.5,.6,.7)}
        b={k:tuple(2*x for x in v) for k,v in a.items()}
        self.assertEqual(validate_response_scaling(a,b,label="STRESS")["nodes"],2)
        self.assertEqual(validate_response_scaling(a,b,label="TOSTRAIN")["relative_max_component_deviation"],0)
        self.assertEqual(validate_response_scaling({1:(.1,.2,.3)},{1:(.2,.4,.6)},label="displacement")["nodes"],1)
    def test_reject_mismatch_and_nonfinite(self):
        a={1:(1.,2.,3.,4.,5.,6.)}
        cases=[{}, {2:(2.,4.,6.,8.,10.,12.)},
               {1:(2.,4.,6.,8.,10.)},
               {1:(2.,4.,6.,8.,10.,math.inf)},
               {1:(2.,4.,6.,8.,10.,30.)}]
        for b in cases:
            with self.subTest(b=b),self.assertRaises(ValueError):
                validate_response_scaling(a,b,label="STRESS")
    def test_reject_near_zero_reference(self):
        with self.assertRaisesRegex(ValueError,"TOO_SMALL"):
            validate_response_scaling({1:(0.,)*6},{1:(0.,)*6},label="TOSTRAIN")
if __name__=="__main__":unittest.main()
