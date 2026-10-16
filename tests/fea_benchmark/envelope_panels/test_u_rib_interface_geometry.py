"""Independent geometry invariant regressions; no CalculiX contact pass claim."""
import copy
import unittest
from check_u_rib_shell_links import MESHES, mesh
from check_u_rib_interface_geometry import _inspect, audit, _face

class InterfaceGeometryTests(unittest.TestCase):
    def test_two_mesh_face_offsets_and_nonconforming_edges(self):
        for n in MESHES:
            with self.subTest(n=n):
                value=audit(n)
                self.assertEqual(value["scope"],"SYNTHETIC_OPEN_U_S8R_INTERFACE_GEOMETRY_ONLY")
                self.assertEqual(value["plate_positive_normal_face_z_mm"],1.5)
                self.assertEqual(value["rib_base_negative_normal_face_z_mm"],1.5)
                self.assertEqual(value["geometric_interface_gap_mm"],0.)
                self.assertEqual(value["rib_base_s8r_midsurface_strip_width_mm"],47.)
                self.assertEqual(value["u_nominal_outer_width_mm"],50.)
                self.assertEqual(value["projected_base_strip_area_mm2"],56400.)
                self.assertEqual(value["bottom_rib_s8r_element_count"],2*n)
                self.assertEqual(value["transverse_contact_mesh"],"NONCONFORMING")
                self.assertEqual(value["engineering_acceptance"],"NOT_ADMITTED")
                self.assertEqual(value["contact_keyword_and_pressure_transfer"],"NOT_VALIDATED")

    def test_normal_reversed_plate_fails(self):
        topology=copy.deepcopy(mesh(8))
        e=list(topology["plate"][0])
        e[1],e[3]=e[3],e[1]
        topology["plate"][0]=tuple(e)
        with self.assertRaisesRegex(ValueError,"NORMAL"):
            _inspect(8,topology)

    def test_normal_reversed_base_fails(self):
        topology=copy.deepcopy(mesh(8))
        e=list(topology["rib"][1])
        e[1],e[3]=e[3],e[1]
        topology["rib"][1]=tuple(e)
        with self.assertRaisesRegex(ValueError,"NORMAL"):
            _inspect(8,topology)

    def test_unphysical_surface_offset_fails(self):
        topology=copy.deepcopy(mesh(8))
        rib_nodes=set(k for e in topology["rib"] for k in e)
        topology["coords"].update({k:(p[0],p[1],p[2]+.3)
            for k,p in topology["coords"].items() if k in rib_nodes})
        with self.assertRaisesRegex(ValueError,"OFFSET"):
            _inspect(8,topology)

    def test_corrupt_stud_or_footprint_fails(self):
        topology=copy.deepcopy(mesh(8))
        topology["panel_studs"]=tuple(topology["rib_studs"])
        with self.assertRaisesRegex(ValueError,"STUD_NODE_IDENTITY"):
            _inspect(8,topology)
        topology=copy.deepcopy(mesh(8))
        a=topology["rib"][1][0]
        p=topology["coords"][a]
        topology["coords"][a]=(p[0],p[1]+2.,p[2])
        with self.assertRaises(ValueError):
            _inspect(8,topology)

    def test_reject_bad_mesh_values_and_connectivity(self):
        for n in (0,4,True,8.0):
            with self.assertRaises(ValueError):
                audit(n)
        topology=copy.deepcopy(mesh(8))
        topology["rib"][1]=tuple(topology["rib"][1][0] for _ in range(8))
        with self.assertRaisesRegex(ValueError,"CONNECTIVITY"):
            _inspect(8,topology)

if __name__=="__main__":
    unittest.main()
