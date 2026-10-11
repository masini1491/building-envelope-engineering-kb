import tempfile
import unittest
from pathlib import Path
from aluminum_result_summary import summarize
from test_aluminum_research import example
from generate import build

class SummaryTests(unittest.TestCase):
    def fixture(self, root):
        c=example()
        build("aluminum",4,"large",root,research=c)
        source=(root/"panel.inp").read_text()
        start=source.index("*NSET,NSET=NALL")
        self.assertGreater(start,0)
        from check_pressure_equilibrium import parse_deck
        nodes,_,edge,_=parse_deck(root/"panel.inp")
        center=next(k for k,(x,y,z) in nodes.items() if x==50 and y==50)
        block="displacements (vx,vy,vz) for set NALL and time 1.000000\n"
        block+="".join(f" {nid} {0.0:.6E} {0.0:.6E} {(0.02 if nid==center else 0.001):.6E}\n" for nid in nodes)
        (root/"panel.dat").write_text(block)
        balance=dict(pressure=(0.,0.,6000.),reconstructed_support=(0.,0.,-6000.),
                     residual=(0.,0.,0.),relative_global_residual=0.)
        return c,balance,center
    def test_observation_and_no_capacity(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);c,balance,center=self.fixture(root)
            result=summarize(deck=root/"panel.inp",dat=root/"panel.dat",inputs=c,
                             translational_balance=balance)
            self.assertEqual(result["displacement"]["center_node_id"],center)
            self.assertAlmostEqual(result["displacement"]["max_abs_nodal_transverse_mm"],.02)
            self.assertEqual(result["translational_support"]["independent_support_measurement"],"NOT_OBSERVED")
            self.assertEqual(result["stress"],"NOT_OBSERVED")
            self.assertEqual(result["engineering_acceptance"],"NOT_ADMITTED")
    def test_refuse_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);c,balance,center=self.fixture(root)
            c["thickness_mm"]=3.
            with self.assertRaisesRegex(ValueError,"MATERIAL_MISMATCH"):
                summarize(deck=root/"panel.inp",dat=root/"panel.dat",inputs=c,translational_balance=balance)
            c["thickness_mm"]=2.
            balance["reconstructed_support"]=(0.,0.,-5900.)
            with self.assertRaisesRegex(ValueError,"VECTOR_MISMATCH"):
                summarize(deck=root/"panel.inp",dat=root/"panel.dat",inputs=c,translational_balance=balance)
            balance["reconstructed_support"]=(0.,0.,-6000.)
            (root/"panel.dat").write_text("missing")
            with self.assertRaises(ValueError):
                summarize(deck=root/"panel.inp",dat=root/"panel.dat",inputs=c,translational_balance=balance)
if __name__=="__main__":unittest.main()
