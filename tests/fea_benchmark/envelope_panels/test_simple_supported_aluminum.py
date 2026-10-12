"""Pure Navier-series reference and fail-closed fixture assessment tests."""
import math
import unittest
from check_simple_supported_aluminum import navier_center,assess

class Tests(unittest.TestCase):
    def test_known_classical_square_factor(self):
        w=navier_center()
        d=69000*2**3/(12*(1-.33**2))
        self.assertAlmostEqual(w*d/(.0001*100**4),.0040623526749,places=9)
        self.assertLess(abs(w-navier_center(order=41))/w,1e-6)
        self.assertAlmostEqual(navier_center(q=.0002),2*w,places=12)
        self.assertAlmostEqual(navier_center(e=138000.),w/2,places=12)
        self.assertNotEqual(navier_center(b=80.),w)

    def test_assess_and_scope(self):
        w=navier_center()
        result=assess({4:.20*w,8:.23*w,16:.25*w},
                      {4:.84*w,8:.95*w,16:.99*w})
        self.assertEqual(result["engineering_acceptance"],"NOT_ADMITTED")
        self.assertEqual(result["attachment_contact"],"NOT_MODELED")
        with self.assertRaisesRegex(ValueError,"NOT_DISTINCT"):
            assess({4:w,8:w,16:w},{4:w,8:w,16:w})
        with self.assertRaisesRegex(ValueError,"NONMONOTONIC"):
            assess({4:.20*w,8:.23*w,16:.25*w},{4:.95*w,8:.84*w,16:.99*w})
        with self.assertRaisesRegex(ValueError,"DISAGREEMENT"):
            assess({4:.20*w,8:.23*w,16:.25*w},{4:.60*w,8:.75*w,16:.80*w})
        with self.assertRaises(ValueError):
            assess({4:.20*w,8:.23*w,16:.25*w},{4:.84*w,8:.95*w,16:math.nan})

    def test_invalid_reference(self):
        for kwargs in (dict(nu=.5),dict(t=100),dict(q=float("nan")),
                       dict(e=0),dict(order=6)):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                navier_center(**kwargs)

if __name__=="__main__":
    unittest.main()
