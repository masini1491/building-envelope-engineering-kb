"""Synthetic negative tests and pinned real-output regression for increment mapping."""
import os
import unittest
from verify_u_base_contact_increments import audit_archive, audit_case, dat_increments

STAT = """ statistics for slave set RIB_BASE_UNDERSIDE, master set PLATE_TOP and time  {time}

   total surface force (fx,fy,fz) and moment about the origin (mx,my,mz)

    0 0 {force:.7E} 0 0 0

   center of gravity and mean normal

    0 0 1.5 0 0 -1

   moment about the center of gravity(mx,my,mz)

    0 0 0

   area,  normal force (+ = tension) and shear force (size)

    1 -1 0
"""

def synthetic_dat(increments=((1, '0.1000000E+00', 1.0),), linked=True):
    text = '                        S T E P       1\n\n'
    for inc, time, fz in increments:
        text += f'                                INCREMENT    {inc}\n\n'
        for label, nid, rf in [('PLATE_EDGE_RF', 1, -2.), ('RIB_END_RF', 2, 1.), ('CENTER_RF', 3, 1.)]:
            text += f' forces (fx,fy,fz) for set {label} and time  {time}\n\n'
            text += f'         {nid}  0. 0. {rf:.7E}\n\n'
        if linked:
            text += f' total number of contact elements for time  {time}\n\n               1\n\n'
            text += STAT.format(time=time, force=fz) * 2
    return text

def synthetic_sta(increments=((1, 0.1),)):
    text = '  STEP      INC     ATT  ITRS     TOT TIME     STEP TIME      INC TIME\n'
    last = 0.
    for inc, time in increments:
        text += f'     1     {inc}  1  12 {time:.6E} {time:.6E} {time - last:.6E}\n'
        last = time
    return text

class FakeZip:
    def __init__(self, sta, dat):
        self.data = {'stem.sta': sta.encode(), 'stem.dat': dat.encode()}
    def read(self, key):
        return self.data[key] if key in self.data else self.data["stem." + key.rsplit(".", 1)[-1]]

def run_case(dat=None, sta=None):
    return audit_case(FakeZip(sta or synthetic_sta(), dat or synthetic_dat()), 'stem')

class IncrementParserTests(unittest.TestCase):
    def test_valid_single_increment(self):
        row = run_case()['last_increment']
        self.assertEqual((row['step'], row['increment']), (1, 1))
        self.assertEqual(row['contact_pairs'][0]['copies'], 2)
        self.assertEqual(row['summed_support_rf3_n'], 0.)
    def test_duplicate_printed_time_distinct_increments_not_merged(self):
        sta = synthetic_sta(((1, 0.1), (2, 0.1000001)))
        dat = synthetic_dat(((1, '0.1000000E+00', 1.), (2, '0.1000000E+00', 2.)))
        report = run_case(dat, sta)
        self.assertEqual(report['increment_count'], 2)
        self.assertEqual(report['last_increment']['contact_pairs'][0]['force_fz_n'], 2.)
        self.assertEqual(len(report['printed_total_time_collisions']), 1)
    def test_same_increment_conflicting_duplicates_rejected(self):
        dat = synthetic_dat()
        index = dat.rfind('0 0 1.0000000E+00 0 0 0')
        self.assertGreater(index, 0)
        dat = dat[:index] + dat[index:].replace('1.0000000E+00', '2.0000000E+00', 1)
        with self.assertRaisesRegex(ValueError, 'SAME_INCREMENT_DUPLICATE_CONFLICT'):
            run_case(dat)
    def test_sta_dat_increment_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, 'STA_DAT_INCREMENT_SET_MISMATCH'):
            run_case(synthetic_dat(((1, '0.1000000E+00', 1.), (2, '0.2000000E+00', 2.))))
    def test_time_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError, 'STA_DAT_TIME_MISMATCH'):
            run_case(synthetic_dat(((1, '0.5000000E+00', 1.),)))
    def test_missing_step_rejected(self):
        with self.assertRaisesRegex(ValueError, 'INCREMENT_BEFORE_STEP'):
            dat_increments(synthetic_dat().replace('S T E P       1', 'header'))
    def test_duplicate_increment_number_rejected(self):
        with self.assertRaisesRegex(ValueError, 'DUPLICATE_DAT_INCREMENT'):
            dat_increments(synthetic_dat(((1, '0.1000000E+00', 1.), (1, '0.2000000E+00', 2.))))
    def test_support_node_overlap_rejected(self):
        dat = synthetic_dat().replace('         2  0. 0.', '         1  0. 0.')
        with self.assertRaisesRegex(ValueError, 'SUPPORT_NODE_OVERLAP'):
            run_case(dat)
    def test_nonfinite_force_rejected(self):
        dat = synthetic_dat().replace('1.0000000E+00 0 0 0', 'NaN 0 0 0')
        with self.assertRaisesRegex(ValueError, 'force_and_origin_moment_SHAPE_OR_NONFINITE'):
            run_case(dat)
    def test_unlinked_has_no_contact(self):
        dat = synthetic_dat(linked=False)
        report = audit_case(FakeZip(synthetic_sta(), dat), 'n8_unlinked/panel')
        self.assertEqual(report['statistics_count'], 0)
        with self.assertRaisesRegex(ValueError, 'UNLINKED_HAS_CONTACT_STATISTICS'):
            audit_case(FakeZip(synthetic_sta(), synthetic_dat()), 'n8_unlinked/panel')
    def test_pinned_artifact_six_cases(self):
        path = os.environ.get('CCX221_U_BASE_CONTACT_ZIP')
        if not path:
            self.skipTest('Pinned artifact not supplied; synthetic negatives still run')
        report = audit_archive(path)
        self.assertEqual(report['source_artifact_sha256'], '11804b4f6c419c2fc12134cf952770497ad40fcb701f74ac4ee262d10f433265')
        expected = [(10,20,-44.43746453),(11,22,0.63992538),(10,0,1.56e-6),
                    (10,20,-17.86643756),(10,20,-0.01928915544),(10,0,-1.118e-6)]
        for case, (ninc, nstats, rf) in zip(report['cases'], expected):
            self.assertEqual((case['increment_count'],case['statistics_count']), (ninc,nstats))
            self.assertAlmostEqual(case['last_increment']['summed_support_rf3_n'], rf, places=5)
        away = report['cases'][1]
        self.assertEqual(away['last_increment']['increment'],11)
        self.assertAlmostEqual(away['last_increment']['contact_pairs'][0]['force_fz_n'],0.6890661)
        self.assertEqual(away['printed_total_time_collisions'][0]['increments'],[10,11])
        self.assertEqual(report['engineering_acceptance'],'NOT_ADMITTED')

if __name__ == '__main__':
    unittest.main()
