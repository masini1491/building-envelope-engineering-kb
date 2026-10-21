"""3/4/5 pinned comparison negative gates; source-free unit cases."""
import io,json,tempfile,unittest,zipfile
from pathlib import Path
from verify_stud_pitch_evidence import pinned,baseline_report,fail

class EvidenceTest(unittest.TestCase):
    def base(self):
        data={'scope':'SYNTHETIC_C3D20R_FOUR_STATION_Z_SPRING_ONLY','cases':[
            {'mesh':n,'case':c,'center_u3_mm':.011 if c=='unlinked' else .009}
            for n in (8,16) for c in ('unlinked','soft','stiff')]}
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:z.writestr('stud-report.json',json.dumps(data))
        b.seek(0)
        return b
    def test_complete_baseline(self):
        with zipfile.ZipFile(self.base()) as z:
            self.assertEqual(len(baseline_report(z)),6)
    def test_duplicate_case_reject(self):
        with zipfile.ZipFile(self.base()) as z:
            d=json.loads(z.read('stud-report.json'))
        d['cases'].append(d['cases'][0])
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:z.writestr('stud-report.json',json.dumps(d))
        b.seek(0)
        with zipfile.ZipFile(b) as z,self.assertRaisesRegex(ValueError,'BASELINE_CASE_COVERAGE'):
            baseline_report(z)
    def test_corrupt_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'p.zip';p.write_bytes(b'BAD')
            with self.assertRaisesRegex(ValueError,'SHA256_MISMATCH'):pinned(p,'abc')
    def test_missing_pinned_file(self):
        with self.assertRaisesRegex(ValueError,'PINNED_FILE'):
            pinned('/does/not/exist','abc')
    def test_bad_scope(self):
        with zipfile.ZipFile(self.base()) as z:
            d=json.loads(z.read('stud-report.json'))
        d['scope']='WRONG'
        b=io.BytesIO()
        with zipfile.ZipFile(b,'w') as z:z.writestr('stud-report.json',json.dumps(d))
        b.seek(0)
        with zipfile.ZipFile(b) as z,self.assertRaisesRegex(ValueError,'BASELINE_SCOPE'):
            baseline_report(z)
if __name__=='__main__':unittest.main()
