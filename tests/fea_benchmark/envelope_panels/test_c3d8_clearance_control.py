"""Strict synthetic initial-clearance diagnostic contract (not engineering acceptance)."""
import tempfile
import unittest
from pathlib import Path
from probe_c3d8_u_contact import deck, model, MESHES, CASES, CLEARANCE_MM, CLEARANCE_CASE
from check_c3d8_u_contact_observations import evaluate, observe_clearance

CONTACT_STATS = """statistics for slave set RIB_BASE_UNDERSIDE, master set PLATE_TOP and time 0.1000000E+01

 total surface force (fx,fy,fz) and moment about the origin (mx,my,mz)

 {force}

 center of gravity and mean normal

 0. 0. 0. 0. 0. -1.

 area,  normal force (+ = tension) and shear force (size)

 {area}
"""


def fixture(root,n):
    """Parser-only fake files: never represent a successful CalculiX execution."""
    folder=Path(root)/f"u_c3d8_control_n{n}_clearance"
    folder.mkdir()
    (folder/"panel.inp").write_bytes(deck(n,CLEARANCE_CASE).encode())
    (folder/"panel.sta").write_text("1 1 1 1 1.0 1 1\n",encoding="ascii")
    (folder/"panel.frd").write_bytes(b"synthetic parser stub, not a solver output\n")
    _,_,_,_,plate,rib,center=model(n,CLEARANCE_CASE)
    groups={"PLATE_EDGE_RF":plate,"RIB_END_RF":rib,"CENTER_RF":center}
    rf="".join(
        f"forces (fx,fy,fz) for set {name} and time 0.1000000E+01\n\n"+
        "".join(f" {node} 0. 0. 0.\n" for node in ids)+"\n"
        for name,ids in groups.items()
    )
    stats=CONTACT_STATS.format(force="0. 0. 0. 0. 0. 0.",area="0. NaN NaN")
    (folder/"panel.dat").write_text(rf+stats,encoding="ascii")
    return folder,groups,rf,stats

class ClearanceControl(unittest.TestCase):
    def test_geometry_deck_and_original_six_scenarios(self):
        for n in MESHES:
            for case in CASES:
                self.assertEqual(deck(n,case).count("*CONTACT PAIR"),int(case!="unlinked"))
            nodes,els,plate,base,ps,rs,center=model(n,CLEARANCE_CASE)
            plate_nodes={node for body,conn in els.values() if body=="PLATE" for node in conn}
            rib_nodes={node for body,conn in els.values() if body=="RIB" for node in conn}
            self.assertEqual(len(els),n*n+14*n)
            self.assertEqual(len(base),6*n)
            self.assertTrue(plate_nodes.isdisjoint(rib_nodes))
            self.assertAlmostEqual(min(nodes[k][2] for k in rib_nodes)-max(nodes[k][2] for k in plate_nodes),CLEARANCE_MM)
            s=deck(n,CLEARANCE_CASE)
            self.assertIn("CENTER_RF,3,3,-0.02000000",s)
            self.assertEqual(s.count("*CONTACT PAIR"),1)
            self.assertNotIn("*ELEMENT,TYPE=S8R",s)
            self.assertNotIn("*EQUATION",s)
        with self.assertRaises(ValueError):deck(8,"clearance-unknown")

    def test_positive_parser_only_and_artifact_sha(self):
        with tempfile.TemporaryDirectory() as d:
            for n in MESHES:fixture(d,n)
            result=observe_clearance(d)
            self.assertEqual(result["engineering_acceptance"],"NOT_ADMITTED")
            self.assertEqual(result["initial_rib_clearance_mm"],0.1)
            for n in MESHES:
                case=result["cases"][str(n)]
                self.assertEqual(case["raw_rf3_balance_n"],0.)
                self.assertEqual(case["contact_print"]["contact_area_mm2"],0.)
                self.assertEqual(case["contact_separation"],"INACTIVE_CONTACT_OBSERVED_FOR_CLEARANCE_CONTROL")
                self.assertEqual(len(case["sha256"]),4)

    def test_reject_active_contact_and_fake_surface(self):
        with tempfile.TemporaryDirectory() as d:
            folder,_,rf,stats=fixture(d,8)
            dat=folder/"panel.dat"
            dat.write_text(rf+CONTACT_STATS.format(force="0. 0. 1. 0. 0. 0.",area="1. -1. 0."),encoding="ascii")
            with self.assertRaisesRegex(ValueError,"C3D8_CLEARANCE_CONTACT_ACTIVE_OR_AMBIGUOUS"):
                evaluate(d,8,CLEARANCE_CASE)
            dat.write_text(rf+CONTACT_STATS.format(force="0. 0. 0. 0. 0. 0.",area="0. 0. 0."),encoding="ascii")
            with self.assertRaisesRegex(ValueError,"C3D8_CLEARANCE_CONTACT_ACTIVE_OR_AMBIGUOUS"):
                evaluate(d,8,CLEARANCE_CASE)
            dat.write_text(rf,encoding="ascii")
            with self.assertRaisesRegex(ValueError,"U_CONTACT_DIAG_FINAL_SURFACE_MISSING"):
                evaluate(d,8,CLEARANCE_CASE)

    def test_reject_rf_imbalance_input_drift_and_coverage(self):
        with tempfile.TemporaryDirectory() as d:
            folder,groups,rf,stats=fixture(d,8)
            dat=folder/"panel.dat"
            node=groups["PLATE_EDGE_RF"][0]
            line=f" {node} 0. 0. 0.\n"
            self.assertIn(line,rf)
            dat.write_text(rf.replace(line,f" {node} 0. 0. 1.\n",1)+stats,encoding="ascii")
            with self.assertRaisesRegex(ValueError,"C3D8_RAW_RF3_IMBALANCE"):
                evaluate(d,8,CLEARANCE_CASE)
            dat.write_text(rf.replace(line," 999999 0. 0. 0.\n",1)+stats,encoding="ascii")
            with self.assertRaisesRegex(ValueError,"U_CONTACT_DIAG_RF_NODE_IDS_PLATE_EDGE_RF"):
                evaluate(d,8,CLEARANCE_CASE)
            dat.write_text(rf+stats,encoding="ascii")
            (folder/"panel.inp").write_bytes(deck(8,CLEARANCE_CASE).encode()+b"#")
            with self.assertRaisesRegex(ValueError,"C3D8_INPUT_PROVENANCE"):
                evaluate(d,8,CLEARANCE_CASE)

    def test_reject_incomplete_solver_state(self):
        with tempfile.TemporaryDirectory() as d:
            folder,*_=fixture(d,8)
            (folder/"panel.sta").write_text("1 1 1 1 0.9 1 1\n",encoding="ascii")
            with self.assertRaisesRegex(ValueError,"C3D8_INCOMPLETE"):
                evaluate(d,8,CLEARANCE_CASE)
            (folder/"panel.sta").write_text("1 1 1 1 1.0 1 1\n",encoding="ascii")
            (folder/"panel.frd").unlink()
            with self.assertRaisesRegex(ValueError,"C3D8_ARTIFACT_frd"):
                evaluate(d,8,CLEARANCE_CASE)

if __name__=="__main__":unittest.main()
