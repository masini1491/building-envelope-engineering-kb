"""Source-free pinned position comparator and reaction negative tests."""
import io,json,tempfile,unittest,zipfile
from pathlib import Path
from verify_stud_position_evidence import open_pinned, verify_result, stop

class PositionEvidenceTest(unittest.TestCase):
 def test_missing_artifact(self):
  with self.assertRaisesRegex(ValueError,'PINNED_SOURCE'):open_pinned('/nonexistent/foo.zip','moved')
 def test_bad_hash(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'sample.zip';p.write_bytes(b'tamper')
   with self.assertRaisesRegex(ValueError,'SHA256'):open_pinned(p,'moved')
 def test_bad_label(self):
  with self.assertRaisesRegex(ValueError,'PINNED_SOURCE'):open_pinned('/nonexistent/foo.zip','unknown')
 def test_input_mismatch(self):
  with self.assertRaisesRegex(ValueError,'INPUT_PROVENANCE'):
   verify_result(b'bad',b'',b'', 'good',((1,2),),8,50.)
 def test_stop_status(self):
  with self.assertRaisesRegex(ValueError,'CONTROL_VIOLATION'):stop('CONTROL_VIOLATION')
if __name__=='__main__':unittest.main()
