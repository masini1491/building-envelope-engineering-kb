"""Bounded independent analytical check for a prescribed-displacement NLGEOM T3D2 truss.

Checks in-plane x/y reaction and imposed y displacement only; this is not a
shell, panel, contact, or glass engineering validation.
"""
from __future__ import annotations
import math
import re
from pathlib import Path

E, A, L, DY = 210000.0, 1.0, 100.0, 30.0
# Green-Lagrange axial strain under prescribed transverse displacement;
# reference-configuration engineering stress P=E*epsilon, directional force:
strain = 0.5 * (DY / L) ** 2
fx = E * A * strain
fy = fx * DY / L
print(f"INDEPENDENT_GREEN_LAGRANGE_ORACLE: U2={DY:.6f}, tip RF1={fx:.6f}, RF2={fy:.6f}")

dat = Path("geometric_truss.dat")
sta = Path("geometric_truss.sta")
if not dat.is_file() or not sta.is_file():
    raise SystemExit("INCOMPLETE_EVIDENCE: .dat or .sta missing")
source = dat.read_text(errors="replace")
status = sta.read_text(errors="replace")
pattern = re.compile(
    r"(?P<quantity>displacements|forces) \([^)]*\) for set "
    r"(?P<set>TIP|BASE) and time\s+(?P<time>[\d.Ee+-]+)\s*"
    r"(?P<node>[12])\s+(?P<x>[\d.Ee+-]+)\s+"
    r"(?P<y>[\d.Ee+-]+)\s+(?P<z>[\d.Ee+-]+)", re.I
)
records = {}
for match in pattern.finditer(source):
    if math.isclose(float(match["time"]), 1.0, abs_tol=1e-8):
        records[(match["quantity"].lower(), match["set"])] = tuple(
            float(match[n]) for n in ("x", "y", "z")
        )
required = [("displacements", "TIP"), ("forces", "TIP"), ("forces", "BASE")]
if any(key not in records for key in required):
    raise SystemExit(f"INCOMPLETE_EVIDENCE: final displacement/reaction records absent: {records}")
u = records[("displacements", "TIP")]
tip = records[("forces", "TIP")]
base = records[("forces", "BASE")]
def check(label, actual, expected, tolerance):
    if not math.isfinite(actual) or abs(actual - expected) > tolerance:
        raise SystemExit(f"NUMERIC_MISMATCH: {label} actual={actual} expected={expected} tol={tolerance}")
check("tip U1", u[0], 0.0, 1e-5)
check("tip U2", u[1], DY, 1e-5)
check("tip RF1", tip[0], fx, 0.05)
check("tip RF2", tip[1], fy, 0.05)
check("base RF1", base[0], -fx, 0.05)
check("base RF2", base[1], -fy, 0.05)
check("sum RF1", tip[0] + base[0], 0.0, 0.05)
check("sum RF2", tip[1] + base[1], 0.0, 0.05)
if not re.search(r"INCREMENT\s+10", source):
    raise SystemExit("INCOMPLETE_EVIDENCE: no final nonlinear increment")
print("ANALYTIC_2D_REACTION_CHECK_PASS: NLGEOM truss only; no shell or panel admission")
print("STATUS_LOG_TAIL:\n" + status[-1500:])
