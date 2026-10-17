"""Run an exact-source, isolated MPC bookkeeping smoke against CalculiX 2.21.

The original GPL source is USER-SUPPLIED and never committed to this repository.
The compiled test executable is temporary; this does not run the whole solver
and makes NO assertions about contact, MPC ownership in S8R, or engineering
capacity. It only tests the unchanged upstream resultsforc() transformation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

SOURCE_ARCHIVE_SHA256 = "51d229aee320cf685216d360f7c04f9a57af0148fbe840483a964c86c315da82"
SOURCE_FILES = {
    "CalculiX.h": "c6753dd5750190a6020f4e080a31cd928d406576de9af4cffe151e7f7207642b",
    "resultsforc.c": "d1de9498ac715a7f08da0b7beba3c92c7c2f1030c85c37122d2708f2f480cad0",
}
SOURCE_PREFIX = "CalculiX/ccx_2.21/src/"
MARKER = "CCX221_MPC_FORCE_BOOKKEEPING_ISOLATED_PASS_NOT_ENGINEERING_ORACLE"
SCOPE = "CALCULIX_221_RESULTSFORC_ISOLATED_MPC_BOOKKEEPING"


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verified_source(archive: Path) -> dict[str, bytes]:
    if archive.is_symlink() or not archive.is_file() or not 0 < archive.stat().st_size <= 3_000_000:
        raise ValueError("CCX221_SOURCE_ARCHIVE_MISSING_OR_INVALID")
    raw = archive.read_bytes()
    if sha256(raw) != SOURCE_ARCHIVE_SHA256:
        raise ValueError("CCX221_SOURCE_ARCHIVE_SHA256_MISMATCH")
    result = {}
    with tarfile.open(fileobj=__import__("io").BytesIO(raw), mode="r:bz2") as tf:
        for filename, expected in SOURCE_FILES.items():
            member = tf.getmember(SOURCE_PREFIX + filename)
            if not member.isfile() or member.size <= 0 or member.size > 1_000_000:
                raise ValueError("CCX221_SOURCE_MEMBER_INVALID")
            fileobj = tf.extractfile(member)
            if fileobj is None:
                raise ValueError("CCX221_SOURCE_MEMBER_MISSING")
            contents = fileobj.read(1_000_001)
            if sha256(contents) != expected:
                raise ValueError("CCX221_SOURCE_MEMBER_SHA256_MISMATCH_" + filename)
            result[filename] = contents
    return result


def audit(archive: Path, harness: Path) -> dict:
    source = verified_source(archive)
    if harness.is_symlink() or not harness.is_file() or harness.stat().st_size > 50_000:
        raise ValueError("CCX221_HARNESS_INVALID")
    compiler = shutil.which("cc")
    if not compiler:
        raise RuntimeError("CCX221_C_COMPILER_UNAVAILABLE")
    with tempfile.TemporaryDirectory(prefix="kb131-ccx221-") as tmp:
        directory = Path(tmp)
        origin = directory / "original"
        origin.mkdir()
        for name, data in source.items():
            (origin / name).write_bytes(data)
        executable = directory / "isolated_mpc_check"
        args = [compiler, "-std=c11", "-O2", "-DARCH=Linux", "-I", str(origin),
                str(origin / "resultsforc.c"), str(harness), "-pthread", "-lm", "-o", str(executable)]
        build = subprocess.run(args, text=True, capture_output=True, timeout=60, check=False)
        if build.returncode != 0:
            raise RuntimeError("CCX221_ISOLATED_COMPILE_FAILED: " + build.stderr[-2000:])
        run = subprocess.run([str(executable)], text=True, capture_output=True, timeout=15, check=False)
        if run.returncode != 0 or run.stdout.strip() != MARKER:
            raise RuntimeError("CCX221_ISOLATED_MPC_FIXTURE_FAILED: " + run.stdout[-1000:] + run.stderr[-1000:])
    return {
        "scope": SCOPE,
        "source_archive_sha256": SOURCE_ARCHIVE_SHA256,
        "source_files_sha256": SOURCE_FILES,
        "harness_sha256": sha256(harness.read_bytes()),
        "isolated_execution_status": MARKER,
        "actual_s8r_contact_mpc_balance": "NOT_ESTABLISHED",
        "full_calculix_build": "NOT_EXECUTED",
        "engineering_acceptance": "NOT_ADMITTED",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_tar_bz2", type=Path, help="Externally supplied original CalculiX 2.21 Debian archive")
    args = parser.parse_args()
    harness = Path(__file__).with_name("ccx221_resultsforc_mpc_harness.c")
    print(json.dumps(audit(args.source_tar_bz2, harness), sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
