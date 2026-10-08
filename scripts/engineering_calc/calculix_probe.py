"""Opt-in external CalculiX execution probe; not an engineering acceptance adapter."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import subprocess


class FEAProbeInputError(ValueError):
    pass


@dataclass(frozen=True)
class FEAProbeResult:
    execution_status: str
    exit_code: int | None
    stdout_tail: str
    stderr_tail: str
    result_scope: str = "EXECUTION_ONLY_NOT_NUMERICALLY_VALIDATED"


def probe_calculix(
    *,
    executable: str,
    job_name: str,
    workspace: str | Path,
    timeout_seconds: int = 60,
    execute: bool = False,
) -> FEAProbeResult:
    """Run an explicitly supplied, locally installed solver on an existing deck.

    The input deck and its includes must already have been produced and reviewed
    by the caller. This API neither builds FEA models nor parses results.
    """
    if not isinstance(job_name, str) or not job_name or not all(
        c.isascii() and (c.isalnum() or c in "_-") for c in job_name
    ) or len(job_name) > 64:
        raise FEAProbeInputError("job_name must be a short ASCII identifier")
    if not isinstance(executable, str) or not executable.strip() or "\x00" in executable:
        raise FEAProbeInputError("executable must be an explicit path")
    if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 300:
        raise FEAProbeInputError("timeout_seconds must be 1..300")
    directory = Path(workspace).resolve(strict=True)
    if not directory.is_dir() or directory.is_symlink():
        raise FEAProbeInputError("workspace must be an existing directory")
    deck = directory / (job_name + ".inp")
    if not deck.is_file() or deck.is_symlink():
        raise FEAProbeInputError("input deck must exist as a regular local file")
    if not execute:
        return FEAProbeResult("NOT_EXECUTED_OPT_IN_REQUIRED", None, "", "")
    exe = Path(executable).resolve(strict=True)
    if not exe.is_file():
        raise FEAProbeInputError("solver executable must be a file")
    try:
        finished = subprocess.run(
            [str(exe), "-i", job_name],
            cwd=directory,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return FEAProbeResult("TIMEOUT", None, "", "")
    except OSError as exc:
        return FEAProbeResult("EXECUTION_ERROR", None, "", str(exc)[:2048])
    return FEAProbeResult(
        "PROCESS_EXIT_ZERO_UNVERIFIED" if finished.returncode == 0 else "PROCESS_NONZERO",
        finished.returncode,
        finished.stdout[-2048:],
        finished.stderr[-2048:],
    )
