"""Isolated one-C3D8 synthetic elastoplastic constitutive smoke (not aluminum)."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

E = 70000.0  # All numbers deliberately synthetic: NOT AA3003/AA3004 properties.
NU = 0.30
SIGMA_Y = 100.0
H = 1000.0
CASES = {"elastic": 0.0008, "plastic": 0.004}
NODES = set(range(1, 9))
STRESS_LABELS = ("SXX", "SYY", "SZZ", "SXY", "SYZ", "SZX")


def deck(case: str) -> str:
    if case not in CASES:
        raise ValueError("SYNTHETIC_CASE_INVALID")
    return "\n".join((
        "*HEADING", "ONE C3D8 SYNTHETIC BILINEAR; NOT ANY ALUMINUM ALLOY",
        "*NODE", "1,0,0,0", "2,1,0,0", "3,1,1,0", "4,0,1,0",
        "5,0,0,1", "6,1,0,1", "7,1,1,1", "8,0,1,1",
        "*ELEMENT,TYPE=C3D8,ELSET=CUBE", "1,1,2,3,4,5,6,7,8",
        "*NSET,NSET=LEFT", "1,4,5,8", "*NSET,NSET=RIGHT", "2,3,6,7",
        "*MATERIAL,NAME=ARTIFICIAL_BILINEAR", "*ELASTIC", f"{E},{NU}",
        "*PLASTIC,HARDENING=ISOTROPIC", f"{SIGMA_Y},0.",
        f"{SIGMA_Y+H*0.01},0.01",
        "*SOLID SECTION,ELSET=CUBE,MATERIAL=ARTIFICIAL_BILINEAR",
        "*STEP", "*STATIC", "0.1,1.,0.00001,0.1",
        "*BOUNDARY", "LEFT,1,1,0.", f"RIGHT,1,1,{CASES[case]:.8f}",
        "1,2,3,0.", "4,3,3,0.",
        "*EL FILE", "S,PEEQ,NOE", "*END STEP", "",
    ))


def analytic(case: str) -> dict:
    if case not in CASES:
        raise ValueError("SYNTHETIC_CASE_INVALID")
    strain = CASES[case]
    trial = E * strain
    plastic_strain = max(0.0, (trial - SIGMA_Y) / (E + H))
    stress = trial if plastic_strain == 0.0 else SIGMA_Y + H * plastic_strain
    return {"strain": strain, "stress_mpa": stress, "peeq": plastic_strain}


def _values(line: str, n: int) -> tuple[int, tuple[float, ...]]:
    if not line.startswith(" -1") or len(line) < 13 + 12*n:
        raise ValueError("SYNTHETIC_FRD_ROW_MALFORMED")
    try:
        node = int(line[3:13])
        items = tuple(float(line[13+12*i:25+12*i]) for i in range(n))
    except ValueError as exc:
        raise ValueError("SYNTHETIC_FRD_ROW_MALFORMED") from exc
    if node not in NODES or any(not math.isfinite(v) for v in items):
        raise ValueError("SYNTHETIC_FRD_NONFINITE_OR_UNEXPECTED_NODE")
    return node, items


def parse(frd: Path) -> dict[str, dict[int, tuple[float, ...]]]:
    if frd.is_symlink() or not frd.is_file() or not 0 < frd.stat().st_size < 8_000_000:
        raise ValueError("SYNTHETIC_FRD_MISSING_OR_UNBOUNDED")
    raw = frd.read_bytes()
    if b"\x00" in raw:
        raise ValueError("SYNTHETIC_FRD_BINARY")
    lines = raw.decode("ascii").splitlines()
    records: dict[str, list[tuple[float, dict[int, tuple[float, ...]]]]] = {"STRESS": [], "PE": []}
    now: str | None = None
    stamp: float | None = None
    labels: list[str] = []
    buffer: dict[int, tuple[float, ...]] = {}
    for line in lines:
        t = line.strip()
        if t.startswith("100CL"):
            if now is not None:
                raise ValueError("SYNTHETIC_FRD_TRUNCATED")
            try:
                stamp = float(line[12:24])
            except ValueError as exc:
                raise ValueError("SYNTHETIC_FRD_INVALID_TIME") from exc
            if not math.isfinite(stamp):
                raise ValueError("SYNTHETIC_FRD_INVALID_TIME")
            continue
        parts = t.split()
        if parts and parts[0] == "-4" and len(parts) >= 3 and parts[1] in records:
            n = 6 if parts[1] == "STRESS" else 1
            if now is not None or stamp is None or parts[2] != str(n):
                raise ValueError("SYNTHETIC_FRD_HEADER_INVALID")
            now, labels, buffer = parts[1], [], {}
            continue
        if now is None:
            continue
        if t == "-3":
            if ((now == "STRESS" and tuple(labels) != STRESS_LABELS)
                or (now == "PE" and tuple(labels) != ("PEEQ",))
                or set(buffer) != NODES):
                raise ValueError("SYNTHETIC_FRD_LABEL_OR_COVERAGE_MISMATCH")
            records[now].append((stamp, buffer))
            now = None
        elif len(parts) >= 2 and parts[0] == "-5":
            labels.append(parts[1])
        elif line.startswith(" -1"):
            node, data = _values(line, 6 if now == "STRESS" else 1)
            if node in buffer:
                raise ValueError("SYNTHETIC_FRD_DUPLICATE_NODE")
            buffer[node] = data
        elif t.startswith("-2"):
            raise ValueError("SYNTHETIC_FRD_CONTINUATION_UNSUPPORTED")
    if now is not None:
        raise ValueError("SYNTHETIC_FRD_TRUNCATED")
    result = {}
    for name, sets in records.items():
        finals = [data for time, data in sets if abs(time - 1.0) <= 1e-7]
        if len(finals) != 1:
            raise ValueError("SYNTHETIC_FRD_FINAL_FIELD_MISSING_OR_DUPLICATED:" + name)
        result[name] = finals[0]
    return result


def check(case: str, path: Path) -> dict:
    if path.is_symlink() or not path.is_dir() or (path / "cube.inp").read_text() != deck(case):
        raise ValueError("SYNTHETIC_DECK_CHANGED")
    sta = path / "cube.sta"
    if sta.is_symlink() or not sta.is_file() or not 0 < sta.stat().st_size < 1_000_000:
        raise ValueError("SYNTHETIC_STA_ABSENT")
    from run_synthetic_panel import _completed_step
    _completed_step(sta)
    ref = analytic(case)
    parsed = parse(path / "cube.frd")
    # Node-extrapolated fields from ONE element, not independent Gauss observations.
    stresses = [parsed["STRESS"][n] for n in sorted(NODES)]
    peeqs = [parsed["PE"][n][0] for n in sorted(NODES)]
    if any(max(abs(x) for x in v[1:]) > 0.03 * ref["stress_mpa"] for v in stresses):
        raise ValueError("SYNTHETIC_UNIAXIAL_STRESS_ASSUMPTION_FAILED")
    s_error = max(abs(v[0] - ref["stress_mpa"]) for v in stresses) / ref["stress_mpa"]
    p_error = max(abs(v - ref["peeq"]) for v in peeqs)
    p_limit = (1e-5 if case == "elastic" else 0.05 * ref["peeq"])
    if (any(v < -1e-7 for v in peeqs) or s_error > 0.03 or p_error > p_limit):
        raise ValueError("SYNTHETIC_INDEPENDENT_CONSTITUTIVE_ORACLE_MISMATCH")
    return {"case": case, "model_scope": "SYNTHETIC_ONE_C3D8_UNIAXIAL",
            "reference": ref, "max_relative_stress_error": s_error,
            "max_absolute_peeq_error": p_error,
            "frd_observation": "EXTRAPOLATED_NODAL_NOT_GAUSS_POINT",
            "real_aluminum_material_plasticity": "NOT_ADMITTED",
            "engineering_acceptance": "NOT_ADMITTED"}


def main() -> int:
    cli = argparse.ArgumentParser()
    cli.add_argument("--case", choices=CASES, required=True)
    cli.add_argument("--directory", type=Path, required=True)
    cli.add_argument("--check", action="store_true")
    opts = cli.parse_args()
    if opts.check:
        print(json.dumps(check(opts.case, opts.directory), sort_keys=True, allow_nan=False))
        print("SYNTHETIC_C3D8_CONSTITUTIVE_ORACLE_PASS; NO MATERIAL OR CAPACITY ADMISSION")
    else:
        if opts.directory.is_symlink() or not opts.directory.is_dir() or any(opts.directory.iterdir()):
            raise ValueError("SYNTHETIC_WORKSPACE_MUST_BE_EMPTY")
        (opts.directory / "cube.inp").write_text(deck(opts.case), encoding="ascii")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
