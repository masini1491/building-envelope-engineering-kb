"""Fail-closed tensor parser contract tests; real CCX coverage in workflow."""
import tempfile
import unittest
from pathlib import Path
from aluminum_tensor_observation import read_final_tensors,_read_tensor_line

def row(node,values):
    return " -1"+f"{node:10d}"+"".join(f"{v:12.5E}" for v in values)
def dataset(name,labels,values,node=1,at=1.):
    return (" 100CL      "+f"{at:12.5E}"+"\n"+f" -4  {name} 6 1\n"
            +"".join(f" -5  {x}\n" for x in labels)
            +row(node,values)+"\n -3\n")
class Tests(unittest.TestCase):
    def records(self,stress=None,strain=None):
        s=stress or ("SXX","SYY","SZZ","SXY","SYZ","SZX")
        e=strain or ("EXX","EYY","EZZ","EXY","EYZ","EZX")
        return dataset("STRESS",s,(1.,2.,3.,4.,5.,6.))+dataset("TOSTRAIN",e,(.1,.2,.3,.4,.5,.6))
    def check(self,content):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"panel.frd";p.write_text(content,encoding="ascii")
            return read_final_tensors(p,{1})
    def test_six_components(self):
        fields=self.check(self.records())
        self.assertEqual(fields["STRESS"][1],(1.,2.,3.,4.,5.,6.))
        self.assertAlmostEqual(fields["TOSTRAIN"][1][-1],.6)
    def test_fail_closed(self):
        scenarios=(self.records(strain=("EXX","EYY","EZZ","EXY","EZX","EYZ")),
                   self.records().replace(" -4  STRESS 6 1"," -4  STRESS 5 1"),
                   self.records().replace(" -3\n"," -2\n",1),
                   self.records().replace("1.00000E+00","9.00000E-01"),
                   self.records().replace("1.00000E+00","NaN        ",1),
                   self.records().replace(" -5  SXY\n"," -5  SXY\n -5  SXY\n"),
                   self.records().replace(" -4  TOSTRAIN 6 1"," -4  INVALID 6 1"))
        for data in scenarios:
            with self.subTest(data=data[:70]),self.assertRaises(ValueError):
                self.check(data)
    def test_incomplete_node_coverage(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"a.frd";p.write_text(self.records())
            with self.assertRaisesRegex(ValueError,"COVERAGE"):
                read_final_tensors(p,{1,2})
if __name__=="__main__":unittest.main()
