"""Source-free regional CSTR audit positive and negative contracts."""
import unittest
from verify_c3d20r_contact_ip import (
    HEADER, parse_input, parse_cstr_final, regional_stats, zone,
)


def sample_deck():
    return ('*NODE\n'
            '1,0.,-25.,3.\n2,150.,-25.,3.\n3,150.,-22.,3.\n4,0.,-22.,3.\n'
            '*ELEMENT,TYPE=C3D20R,ELSET=RIB\n'
            '257,'+','.join(str(i) for i in range(1,16))+',\n'
            +','.join(str(i) for i in range(16,21))+'\n'
            '*SURFACE,NAME=RIB_BASE_UNDERSIDE,TYPE=ELEMENT\n257,S1\n')


def sample_dat(*, rows=2, count=2, eid=257):
    prefix=('total number of contact elements for time  0.1000000E+01\n\n'
            f'   {count}\n\n'+HEADER+'\n\n')
    return (prefix+''.join(f'{eid:10d}          1  2.500000E-02  0.000000E+00  0.000000E+00\n'
                           for _ in range(rows))+'\n statistics for slave set RIB_BASE_UNDERSIDE\n')


class ContactIPAuditTest(unittest.TestCase):
    def test_parse_input_centroid(self):
        self.assertEqual(parse_input(sample_deck()),{257:(75.,-23.5)})
    def test_final_sample_record_count(self):
        groups,count=parse_cstr_final(sample_dat(),{257:(75.,-23.5)})
        self.assertEqual(count,2)
        self.assertEqual(groups[257],[0.025,0.025])
    def test_reject_missing_gauss_rows(self):
        with self.assertRaisesRegex(ValueError,'CSTR_COUNT_MISMATCH'):
            parse_cstr_final(sample_dat(rows=1),{257:(75.,-23.5)})
    def test_reject_unlisted_face(self):
        with self.assertRaisesRegex(ValueError,'CSTR_FACE_VALUE'):
            parse_cstr_final(sample_dat(eid=999),{257:(75.,-23.5)})
    def test_reject_duplicate_final_block(self):
        with self.assertRaisesRegex(ValueError,'CSTR_FINAL_HEADER'):
            parse_cstr_final(sample_dat()+sample_dat(),{257:(75.,-23.5)})
    def test_reject_bad_slave_face(self):
        with self.assertRaisesRegex(ValueError,'SLAVE_FACE'):
            parse_input(sample_deck().replace('257,S1','257,S2'))
    def test_regions_are_physical_mm_not_mesh_index(self):
        self.assertEqual(zone(20),'end_0_150_mm')
        self.assertEqual(zone(1180),'end_0_150_mm')
        self.assertEqual(zone(150),'transition_150_300_mm')
        self.assertEqual(zone(850),'interior_300_600_mm')
        s=regional_stats({1:[0.08,0.03],2:[0.02],3:[0.001]},
                         {1:(75.,-23.5),2:(225.,-23.5),3:(600.,-23.5)})
        self.assertEqual(s['end_0_150_mm']['cstr_rows'],2)
        self.assertAlmostEqual(s['interior_300_600_mm']['max_cpress_n_mm2'],0.001)
    def test_unrepresented_zone_rejected(self):
        with self.assertRaisesRegex(ValueError,'ZONE_MISSING'):
            regional_stats({1:[0.01]},{1:(75.,-23.5)})


if __name__=='__main__':unittest.main()
