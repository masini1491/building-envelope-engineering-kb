"""Strength-only screen for specimen failure loads, never connection stiffness.

The mean-minus-one-SD / SF expression is an explicitly selected engineering
practice, NOT an automatically qualified code/standard characteristic value.
No external customer/test report is bundled with this public calculator.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean, stdev

METHOD = "ENGINEER_SELECTED_MEAN_MINUS_ONE_SAMPLE_SD_OVER_SF"
UNITS = {"kgf", "N"}
MODES = {"STUD_FRACTURE", "WELD_FAILURE", "OTHER", "UNKNOWN"}
REQUIRED = {"method", "failure_loads", "load_unit", "safety_factor", "failure_modes", "source_sha256"}
KGF_TO_N = 9.80665


def fail(code: str) -> None:
    raise ValueError("STUD_TENSILE_SCREEN_" + code)


def load_input(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 32768:
        fail("FILE_BOUNDARY")

    def no_duplicate_pairs(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                fail("DUPLICATE_JSON_KEY")
            obj[key] = value
        return obj

    def no_nonfinite(_):
        fail("JSON_NONFINITE")

    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=no_duplicate_pairs,
                      parse_constant=no_nonfinite)


def _positive_finite(value, reason: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        fail(reason)
    return float(value)


def calculate(data: dict) -> dict:
    if not isinstance(data, dict) or set(data) != REQUIRED:
        fail("SCHEMA")
    if data["method"] != METHOD:
        fail("METHOD_NOT_EXPLICIT")
    if type(data["load_unit"]) is not str or data["load_unit"] not in UNITS:
        fail("UNSUPPORTED_UNIT")
    digest = data["source_sha256"]
    if (not isinstance(digest, str) or len(digest) != 64 or
            any(c not in "0123456789abcdef" for c in digest)):
        fail("SOURCE_HASH")
    sf = _positive_finite(data["safety_factor"], "SAFETY_FACTOR")
    if sf <= 1:
        fail("SAFETY_FACTOR")
    raw = data["failure_loads"]
    if not isinstance(raw, list) or not 3 <= len(raw) <= 1000:
        fail("SAMPLE_COUNT")
    loads = [_positive_finite(x, "FAILURE_LOAD") for x in raw]
    modes = data["failure_modes"]
    if (not isinstance(modes, list) or len(modes) != len(loads)
            or any(type(x) is not str or x not in MODES for x in modes)):
        fail("FAILURE_MODES")
    avg = mean(loads)
    sample_sd = stdev(loads)
    reduced = avg - sample_sd
    if not math.isfinite(reduced) or reduced <= 0:
        fail("NONPOSITIVE_REDUCED_LOAD")
    candidate = reduced / sf
    factor = KGF_TO_N if data["load_unit"] == "kgf" else 1.0
    if not math.isfinite(candidate * factor):
        fail("OVERFLOW")
    return {
        "method": METHOD,
        "calculation_status": "REPRODUCED_AS_SELECTED_NOT_CODE_QUALIFIED",
        "sample_count": len(loads),
        "source_unit": data["load_unit"],
        "sample_mean_failure_load": avg,
        "sample_standard_deviation": sample_sd,
        "mean_minus_one_sample_sd": reduced,
        "engineer_selected_safety_factor": sf,
        "candidate_allowable_load_source_unit": candidate,
        "candidate_allowable_load_n": candidate * factor,
        "failure_mode_counts": {kind: modes.count(kind) for kind in sorted(MODES) if kind in modes},
        "fracture_mode_review": "REQUIRED" if "WELD_FAILURE" in modes or "OTHER" in modes or "UNKNOWN" in modes else "NOT_RESOLVED_BY_LOADS_ALONE",
        "source_authenticity": "EXTERNAL_REVIEW_REQUIRED",
        "formula_authority": "ENGINEER_SELECTED_PROJECT_PRACTICE_NOT_VERIFIED_STANDARD",
        "characteristic_fractile_or_confidence_bound": "NOT_ESTABLISHED",
        "connection_stiffness_n_per_mm": "NOT_ESTABLISHED",
        "stud_weld_capacity_design_admission": "NOT_ADMITTED",
        "engineering_acceptance": "NOT_ADMITTED",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input_json", type=Path)
    args = p.parse_args()
    print(json.dumps(calculate(load_input(args.input_json)), ensure_ascii=False,
                     sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
