"""Independent geometry oracle for a geometrically nonlinear two-node truss.

This is an installation/runtime benchmark only, not a glass or plate validation.
"""
from __future__ import annotations
import math
import re
from pathlib import Path

E, A, L0, DY = 210000.0, 1.0, 100.0, 30.0
final_length = math.hypot(L0, DY)
axial = E * A * (final_length - L0) / L0
expected_vertical = axial * DY / final_length
expected_horizontal = axial * L0 / final_length
print(f"INDEPENDENT_ORACLE: tip U2={DY:.8f} mm; support RF2={-expected_vertical:.8f} N; support RF1={-expected_horizontal:.8f} N")
dat = Path("geometric_truss.dat")
sta = Path("geometric_truss.sta")
if not dat.exists() or not sta.exists():
    raise SystemExit("INCOMPLETE_EVIDENCE: CalculiX .dat or .sta absent")
text = dat.read_text(errors="replace")
progress = sta.read_text(errors="replace")
print("STATUS_LOG_TAIL:\n" + progress[-2500:])
print("RESULT_LOG_TAIL:\n" + text[-5000:])
if re.search(r"(error|divergen|not converg)", progress, re.I):
    raise SystemExit("UNVALIDATED: convergence error in .sta")
if not re.search(r"RF|forces", text, re.I):
    raise SystemExit("INCOMPLETE_EVIDENCE: no reaction-force output in .dat")
print("EXECUTED_WITH_OUTPUT_NOT_YET_INDEPENDENTLY_ADMITTED")
