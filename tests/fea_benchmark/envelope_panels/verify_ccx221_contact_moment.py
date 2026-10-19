"""CCX 2.21 contact-resultant moment identities and an analytic couple oracle.

Only geometric moments and linearized rigid-body virtual work are admitted.
This NEVER admits S8R rotational SPC/MPC reaction moments or full equilibrium.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Sequence

EXPECTED_DAT_SHA256 = {
    8: "143a780738984d1f2819ef0e33ca9db3c0911cfdeb583ab1008dfefca4c1a9f1",
    16: "680f2b64a2ddce81437000d2cc28027660d5abf0eef91bbc69f81640595de068",
}
STATS = re.compile(
    r"(?m)^\s*statistics for slave set RIB_BASE_UNDERSIDE, "
    r"master set PLATE_TOP and time\s+([^\n]+)\s*$"
)
SCI = re.compile(r"^[+-]?\d\.\d{6}E[+-]\d{2}$")
FORCE_HEADER = "total surface force (fx,fy,fz) and moment about the origin (mx,my,mz)"
CENTER_HEADER = "center of gravity and mean normal"
MOMENT_HEADER = "moment about the center of gravity(mx,my,mz)"
COMPONENTS = ("Mx", "My", "Mz")


def reject(code: str) -> None:
    raise ValueError("CCX221_MOMENT_" + code)


def cross(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return (
        math.fsum((a[1] * b[2], -a[2] * b[1])),
        math.fsum((a[2] * b[0], -a[0] * b[2])),
        math.fsum((a[0] * b[1], -a[1] * b[0])),
    )


def plus(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float]:
    return tuple(x + y for x, y in zip(a, b))


def take_row(section: str, label: str, count: int) -> tuple[list[float], list[float]]:
    match = re.search(r"(?m)^\s*" + re.escape(label) + r"\s*\n\s*([^\n]+)", section)
    if match is None:
        reject("HEADER_MISSING")
    tokens = match.group(1).strip().split()
    if len(tokens) != count or any(not SCI.fullmatch(tok) for tok in tokens):
        reject("ROW_FORMAT")
    values = [float(tok) for tok in tokens]
    if not all(math.isfinite(x) for x in values):
        reject("NONFINITE")
    # Half of the last significant printed decimal unit, not a tuned tolerance.
    bound = [0.5 * 10 ** (int(tok[-3:]) - 6) for tok in tokens]
    return values, bound


def parse_dat(text: str) -> tuple[dict, int]:
    starts = list(STATS.finditer(text))
    if len(starts) < 2:
        reject("NO_CONTACT_STATISTICS")
    finals = []
    for i, start in enumerate(starts):
        try:
            t = float(start.group(1))
        except ValueError:
            reject("BAD_TIME")
        if not math.isfinite(t):
            reject("NONFINITE_TIME")
        if abs(t - 1.0) > 1e-8:
            continue
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        section = text[start.end():end]
        f_and_m, f_and_m_err = take_row(section, FORCE_HEADER, 6)
        cg_and_normal, cg_err = take_row(section, CENTER_HEADER, 6)
        mc, mc_err = take_row(section, MOMENT_HEADER, 3)
        finals.append({
            "force": f_and_m[:3], "origin_moment": f_and_m[3:],
            "cg": cg_and_normal[:3], "cg_moment": mc,
            "force_err": f_and_m_err[:3], "origin_err": f_and_m_err[3:],
            "cg_err": cg_err[:3], "cg_moment_err": mc_err,
        })
    if len(finals) != 2 or finals[0] != finals[1]:
        reject("DUPLICATE_FINAL_STATISTICS_INCONSISTENT")
    return finals[0], len(finals)


def geometric_audit(entry: dict) -> dict:
    force, cg = entry["force"], entry["cg"]
    recon = tuple(a - b for a, b in zip(entry["origin_moment"], cross(cg, force)))
    out = []
    for i in range(3):
        j = (i + 1) % 3
        k = (i + 2) % 3
        # Absolute rounding envelope for M_CG=M_O-r_CG x F
        # independently derived from each scientific printed field.
        bound = math.fsum((
            entry["origin_err"][i], entry["cg_moment_err"][i],
            abs(cg[j]) * entry["force_err"][k],
            abs(force[k]) * entry["cg_err"][j],
            entry["cg_err"][j] * entry["force_err"][k],
            abs(cg[k]) * entry["force_err"][j],
            abs(force[j]) * entry["cg_err"][k],
            entry["cg_err"][k] * entry["force_err"][j],
        ))
        error = abs(recon[i] - entry["cg_moment"][i])
        if error > bound:
            reject("MOMENT_ORIGIN_TRANSFORM")
        out.append({"component": COMPONENTS[i],
                    "reconstructed_at_cg_nmm": recon[i],
                    "printed_at_cg_nmm": entry["cg_moment"][i],
                    "absolute_difference_nmm": error,
                    "max_print_rounding_difference_nmm": bound})
    return {"force_n": force, "moment_about_origin_nmm": entry["origin_moment"],
            "printed_cg_mm": cg, "center_shift_components": out}


def couple_oracle(a_mm: float = 100.0, k_n_per_mm: float = 120.0,
                  theta_rad: float = 0.00002) -> dict:
    """Exactly solvable small-rotation two-spring force couple.

    At x=+-a, prescribe dz=-x*theta, generalized external force Fz=k*dz.
    U=(k/2) sum(dz^2)=k*a^2*theta^2, My=dU/dtheta=2ka^2theta.
    No shell, contact, solver MPC or RF data are used by this oracle.
    """
    if not all(math.isfinite(x) and x > 0 for x in (a_mm, k_n_per_mm, theta_rad)):
        reject("BAD_COUPLE_INPUT")
    places = [(-a_mm, 0.0, 0.0), (a_mm, 0.0, 0.0)]
    disp = [(0.0, 0.0, -r[0] * theta_rad) for r in places]
    force = [(0.0, 0.0, k_n_per_mm * d[2]) for d in disp]
    total = tuple(math.fsum(f[i] for f in force) for i in range(3))
    moment = tuple(math.fsum(cross(r, f)[i] for r, f in zip(places, force)) for i in range(3))
    m_expected = 2 * k_n_per_mm * a_mm ** 2 * theta_rad
    if abs(moment[1] - m_expected) > 1e-10 or any(abs(f) > 1e-12 for f in total):
        reject("COUPLE_FORCE_MOMENT")
    energy = lambda angle: k_n_per_mm * a_mm ** 2 * angle ** 2
    slopes = {}
    for h in (1e-7, 2e-7):
        slope = (energy(theta_rad + h) - energy(theta_rad - h)) / (2 * h)
        if not math.isclose(slope, m_expected, rel_tol=1e-11, abs_tol=1e-9):
            reject("COUPLE_VIRTUAL_WORK")
        slopes[str(h)] = slope
    origin_shift = (37.0, -73.0, 12.0)
    shifted = tuple(math.fsum(cross(tuple(r[i] - origin_shift[i] for i in range(3)), f)[i]
                               for r, f in zip(places, force)) for i in range(3))
    if any(abs(shifted[i] - moment[i]) > 1e-10 for i in range(3)):
        reject("PURE_COUPLE_ORIGIN_INVARIANCE")
    return {"forces_net_n": total, "moment_nmm": moment,
            "exact_generalized_my_nmm": m_expected,
            "virtual_work_derivatives_nmm": slopes,
            "moment_after_origin_shift_nmm": shifted,
            "energy_nmm": energy(theta_rad)}


def verify_files(paths: dict[int, Path]) -> dict:
    if set(paths) != set(EXPECTED_DAT_SHA256):
        reject("MESH_COVERAGE")
    meshes = {}
    for mesh, path in sorted(paths.items()):
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != EXPECTED_DAT_SHA256[mesh]:
            reject("DAT_PROVENANCE")
        entry, count = parse_dat(raw.decode("latin-1"))
        meshes[f"n{mesh}"] = {
            "sha256": digest, "repeated_final_statistics": count,
            **geometric_audit(entry)}
    return {"status": "GEOMETRIC_MOMENT_AND_ANALYTIC_COUPLE_PASS_ONLY",
            "pure_couple_independent_analytic_oracle": couple_oracle(),
            "observed_ccx_contact": meshes,
            "ccx_contact_moment_is_solver_internal_not_external_oracle": True,
            "shell_rotational_spc_reconstruction": "NOT_ESTABLISHED",
            "six_component_support_equilibrium": "NOT_ADMITTED",
            "engineering_acceptance": "NOT_ADMITTED"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("n8_dat", type=Path)
    parser.add_argument("n16_dat", type=Path)
    opts = parser.parse_args()
    print(json.dumps(verify_files({8: opts.n8_dat, 16: opts.n16_dat}),
                     sort_keys=True, indent=2, allow_nan=False))
