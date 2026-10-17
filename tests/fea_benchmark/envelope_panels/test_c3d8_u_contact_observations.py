"""Scope / negative input checks for C3D8 control."""
import tempfile,unittest
from pathlib import Path
from check_c3d8_u_contact_observations import evaluate,observe
from probe_c3d8_u_contact import deck,model
class SolidObservations(unittest.TestCase):
    def test_requires_real_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):observe(d)
    def test_out_of_scope(self):
        with tempfile.TemporaryDirectory() as d:
            for n,c in ((4,"toward"),(8,"unknown"),(True,"away")):
                with self.assertRaises(ValueError):evaluate(d,n,c)
    def _unlinked_parser_fixture(self,root,n):
        # Controlled parser fixture, NOT a real solver or engineering result.
        folder=Path(root)/f"u_c3d8_control_n{n}_unlinked"
        folder.mkdir()
        (folder/"panel.inp").write_bytes(deck(n,"unlinked").encode("utf-8"))
        (folder/"panel.sta").write_text("1 1 1 1 1.0 1 1\n",encoding="ascii")
        (folder/"panel.frd").write_bytes(b"parser-only synthetic fixture\n")
        _,_,_,_,plate,rib,center=model(n,"unlinked")
        groups={"PLATE_EDGE_RF":plate,"RIB_END_RF":rib,"CENTER_RF":center}
        blocks=[]
        for name,ids in groups.items():
            blocks.append(
                f"forces (fx,fy,fz) for set {name} and time 0.1000000E+01\n\n"+
                "".join(f" {node} 0. 0. 0.\n" for node in ids)+"\n"
            )
        (folder/"panel.dat").write_text("".join(blocks),encoding="ascii")
        return folder,groups

    def test_exact_node_id_membership_on_both_meshes(self):
        for n in (8,16):
            with self.subTest(n=n),tempfile.TemporaryDirectory() as d:
                folder,groups=self._unlinked_parser_fixture(d,n)
                self.assertEqual(evaluate(d,n,"unlinked")["raw_rf3_balance_n"],0.)
                path=folder/"panel.dat"
                dat=path.read_text(encoding="ascii")
                original=groups["PLATE_EDGE_RF"][0]
                changed=dat.replace(f" {original} 0. 0. 0.\n",
                                    " 999999 0. 0. 0.\n",1)
                self.assertNotEqual(changed,dat)
                path.write_text(changed,encoding="ascii")
                with self.assertRaisesRegex(ValueError,"U_CONTACT_DIAG_RF_NODE_IDS_PLATE_EDGE_RF"):
                    evaluate(d,n,"unlinked")

    def test_reject_duplicate_node_and_bad_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            folder,groups=self._unlinked_parser_fixture(d,8)
            data=folder/"panel.dat"
            original=data.read_text(encoding="ascii")
            node=groups["PLATE_EDGE_RF"][0]
            line=f" {node} 0. 0. 0.\n"
            self.assertIn(line,original)
            data.write_text(original.replace(line,line+line,1),encoding="ascii")
            with self.assertRaisesRegex(ValueError,"U_CONTACT_DIAG_DUPLICATE_NODE_PLATE_EDGE_RF"):
                evaluate(d,8,"unlinked")
            data.write_text(original,encoding="ascii")
            inp=folder/"panel.inp"
            inp.write_bytes(inp.read_bytes()+b"#")
            with self.assertRaisesRegex(ValueError,"C3D8_INPUT_PROVENANCE"):
                evaluate(d,8,"unlinked")

    def test_reject_nonfinite_unbalanced_and_incomplete_time(self):
        with tempfile.TemporaryDirectory() as d:
            folder,groups=self._unlinked_parser_fixture(d,8)
            data=folder/"panel.dat"
            original=data.read_text(encoding="ascii")
            node=groups["PLATE_EDGE_RF"][0]
            line=f" {node} 0. 0. 0.\n"
            data.write_text(original.replace(line,f" {node} 0. 0. NaN\n",1),encoding="ascii")
            with self.assertRaises(ValueError):
                evaluate(d,8,"unlinked")
            data.write_text(original.replace(line,f" {node} 0. 0. 1.\n",1),encoding="ascii")
            with self.assertRaisesRegex(ValueError,"C3D8_RAW_RF3_IMBALANCE"):
                evaluate(d,8,"unlinked")
            data.write_text(original,encoding="ascii")
            (folder/"panel.sta").write_text("1 1 1 1 0.9 1 1\n",encoding="ascii")
            with self.assertRaisesRegex(ValueError,"C3D8_INCOMPLETE"):
                evaluate(d,8,"unlinked")
if __name__=="__main__":unittest.main()
