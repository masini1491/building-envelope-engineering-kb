"""Parser fixtures only. These tests do not replace real CalculiX execution."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from check_c3d8_clearance_gap import observe


def fixture(root):
    records = {}
    for n in (8,16):
        folder = Path(root)/f'u_c3d8_control_n{n}_clearance'
        folder.mkdir()
        nodes = [(i,0. if i<=8 else 1.,0.,1.5 if i<=8 else 1.6) for i in range(1,17)]
        inp = ('*HEADING\n*NODE\n' + ''.join(
            f'{i},{x},{y},{z}\n' for i,x,y,z in nodes) +
            '*ELEMENT,TYPE=C3D8,ELSET=PLATE\n1,1,2,3,4,5,6,7,8\n' +
            '*ELEMENT,TYPE=C3D8,ELSET=RIB\n2,9,10,11,12,13,14,15,16\n' +
            '*END STEP\n').encode('ascii')
        rows = ''.join(f' -1{i:10d}{0.:12.5E}{0.:12.5E}{0.:12.5E}\n' for i in range(1,17))
        frd = ('  100CL  110 1.00000E+00       16    0   10    1\n'
               ' -4  DISP        4    1\n -5  D1\n -5  D2\n -5  D3\n'
               + rows + ' -3\n').encode('ascii')
        (folder/'panel.inp').write_bytes(inp)
        (folder/'panel.frd').write_bytes(frd)
        records[str(n)] = {
            'contact_separation':'INACTIVE_CONTACT_OBSERVED_FOR_CLEARANCE_CONTROL',
            'engineering_acceptance':'NOT_ADMITTED',
            'raw_rf3_balance_state':'OBSERVED_WITHIN_BOUNDED_TOLERANCE',
            'sha256':{'inp':hashlib.sha256(inp).hexdigest(),'frd':hashlib.sha256(frd).hexdigest()}}
    doc={'scope':'SYNTHETIC_C3D8_INITIAL_CLEARANCE_NO_ACTIVE_CONTACT_CONTROL',
         'engineering_acceptance':'NOT_ADMITTED','cases':records}
    (Path(root)/'u_c3d8_clearance_observations.json').write_text(json.dumps(doc))
    return doc


def replace_frd(root,doc,n,func):
    file = Path(root)/f'u_c3d8_control_n{n}_clearance/panel.frd'
    original=file.read_text()
    modified=func(original)
    assert modified != original
    file.write_text(modified)
    doc['cases'][str(n)]['sha256']['frd']=hashlib.sha256(file.read_bytes()).hexdigest()
    (Path(root)/'u_c3d8_clearance_observations.json').write_text(json.dumps(doc))


class ClearanceGapTests(unittest.TestCase):
    def test_positive_separate_body_envelopes(self):
        with tempfile.TemporaryDirectory() as d:
            fixture(d)
            result=observe(d)
            self.assertEqual(set(result['cases']),{'8','16'})
            for r in result['cases'].values():
                self.assertAlmostEqual(r['final_global_vertical_separation_lower_bound_mm'],0.1)
            self.assertEqual(result['engineering_acceptance'],'NOT_ADMITTED')

    def test_negative_overlap(self):
        with tempfile.TemporaryDirectory() as d:
            doc=fixture(d)
            replace_frd(d,doc,8,lambda s:s.replace(
                f' -1{9:10d}{0.:12.5E}{0.:12.5E}{0.:12.5E}',
                f' -1{9:10d}{0.:12.5E}{0.:12.5E}{-0.2:12.5E}',1))
            with self.assertRaisesRegex(ValueError,'C3D8_GAP_NOT_POSITIVE'):observe(d)

    def test_reject_node_identity_and_nonfinite(self):
        for replacement,error in ((999,'C3D8_GAP_NODE_COVERAGE'),('nan','C3D8_GAP_DUPLICATE_OR_NONFINITE_DISPLACEMENT')):
            with self.subTest(replacement=replacement),tempfile.TemporaryDirectory() as d:
                doc=fixture(d)
                old=f' -1{9:10d}{0.:12.5E}{0.:12.5E}{0.:12.5E}'
                new=(f' -1{replacement:10d}{0.:12.5E}{0.:12.5E}{0.:12.5E}' if isinstance(replacement,int)
                     else f' -1{9:10d}{0.:12.5E}{0.:12.5E}{"NaN":>12s}')
                replace_frd(d,doc,8,lambda s:s.replace(old,new,1))
                with self.assertRaisesRegex(ValueError,error):observe(d)

    def test_reject_time_and_hash(self):
        with tempfile.TemporaryDirectory() as d:
            doc=fixture(d)
            replace_frd(d,doc,16,lambda s:s.replace('1.00000E+00','9.00000E-01',1))
            with self.assertRaisesRegex(ValueError,'C3D8_GAP_INVALID_FINAL_TIME'):observe(d)
            (Path(d)/'u_c3d8_control_n16_clearance/panel.frd').write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError,'C3D8_GAP_PROVENANCE_MISMATCH'):observe(d)

    def test_reject_bad_partition(self):
        with tempfile.TemporaryDirectory() as d:
            doc=fixture(d)
            inp=Path(d)/'u_c3d8_control_n8_clearance/panel.inp'
            inp.write_bytes(inp.read_bytes().replace(b'2,9,10,11,12,13,14,15,16',b'2,1,10,11,12,13,14,15,16'))
            doc['cases']['8']['sha256']['inp']=hashlib.sha256(inp.read_bytes()).hexdigest()
            (Path(d)/'u_c3d8_clearance_observations.json').write_text(json.dumps(doc))
            with self.assertRaisesRegex(ValueError,'C3D8_GAP_INVALID_BODY_PARTITION'):observe(d)

if __name__=='__main__':unittest.main()
