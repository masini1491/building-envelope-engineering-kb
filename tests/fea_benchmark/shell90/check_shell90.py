"""Fail closed on incomplete 90-degree shell NLGEOM execution.

An exit-zero shell run with FRD output is *not* engineering numerical validation.
"""
from pathlib import Path
import math
import re

sta = Path("shell90.sta")
frd = Path("shell90.frd")
if not sta.is_file() or not frd.is_file() or frd.stat().st_size == 0:
    raise SystemExit("SHELL90_INCOMPLETE: missing solver result files")
lines = [x.strip() for x in sta.read_text(errors="replace").splitlines() if x.strip()]
records = []
for line in lines:
    parts = line.split()
    if len(parts) != 7 or parts[0] != "1":
        continue
    try:
        increment = int(parts[1])
        attempt = parts[2]
        total_time = float(parts[4])
    except ValueError:
        continue
    if not math.isfinite(total_time):
        raise SystemExit("SHELL90_INCOMPLETE: nonfinite increment progress")
    records.append((increment, attempt, total_time))
if not records or abs(records[-1][2] - 1.0) > 1e-7:
    raise SystemExit(f"SHELL90_INCOMPLETE: step failed to reach full applied rotation; records={records}")
if "U" in records[-1][1]:
    raise SystemExit("SHELL90_INCOMPLETE: last increment rejected")
print(f"SHELL90_EXECUTION_COMPLETED: {len(records)} increment attempts, final time={records[-1][2]}")
print("NO_SHELL_NUMERICAL_ADMISSION: independent displacement/reaction and mesh convergence pending")
