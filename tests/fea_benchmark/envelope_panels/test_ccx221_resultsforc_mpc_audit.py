"""Fail-closed tests; positive exact-source execution needs external official archive."""
import tempfile
import unittest
from pathlib import Path
from ccx221_resultsforc_mpc_audit import SOURCE_ARCHIVE_SHA256, SOURCE_FILES, audit, verified_source


class Ccx221OwnershipContract(unittest.TestCase):
    def test_known_source_identity(self):
        self.assertEqual(len(SOURCE_ARCHIVE_SHA256),64)
        self.assertEqual(set(SOURCE_FILES),{"CalculiX.h","resultsforc.c"})
        self.assertTrue(all(len(x)==64 for x in SOURCE_FILES.values()))
    def test_missing_source_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"ARCHIVE_MISSING_OR_INVALID"):
                verified_source(Path(td)/"missing.tar.bz2")
    def test_mismatched_source_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"invalid.tar.bz2"
            path.write_bytes(b"not the original source")
            with self.assertRaisesRegex(ValueError,"ARCHIVE_SHA256_MISMATCH"):
                verified_source(path)
    def test_bad_harness_rejected_before_compilation(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"missing.tar.bz2"
            with self.assertRaises(ValueError):
                audit(path,Path(td)/"missing.c")
    def test_symlink_source_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            x=Path(td)/"actual.tar.bz2";x.write_bytes(b"stub")
            alias=Path(td)/"alias.tar.bz2";alias.symlink_to(x)
            with self.assertRaisesRegex(ValueError,"ARCHIVE_MISSING_OR_INVALID"):
                verified_source(alias)


if __name__=="__main__":unittest.main()
