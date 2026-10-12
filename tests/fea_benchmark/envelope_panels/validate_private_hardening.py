"""Private-file-only hardening-table structure preflight, not material admission.

This checker does not persist input or print proprietary numerical values.
It NEVER writes a *PLASTIC card or solver deck.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

ALLOYS = frozenset(("3003-H14", "3004-H12", "3004-O"))
_FIELDS = frozenset(("alloy_temper", "product_id", "manufacturer", "state", "data_origin", "units", "curve_type", "elastic_modulus_mpa", "poisson_ratio", "points"))
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")


def _number(value):
    if type(value) not in (float, int) or not math.isfinite(value):
        raise ValueError("HARDENING_NONFINITE_OR_NONNUMERIC")
    return float(value)


def validate(record: dict) -> dict:
    if not isinstance(record, dict) or set(record) != _FIELDS:
        raise ValueError("HARDENING_SCHEMA_MISMATCH")
    if record["alloy_temper"] not in ALLOYS or type(record["alloy_temper"]) is not str:
        raise ValueError("HARDENING_ALLOY_UNSUPPORTED")
    if type(record["product_id"]) is not str or not _ID.fullmatch(record["product_id"]):
        raise ValueError("HARDENING_PRODUCT_ID_INVALID")
    if (record["manufacturer"] != "CS Aluminum" or record["state"] != "AS_SUPPLIED"
            or record["data_origin"] != "PRIVATE_USER_SUPPLIED_MANUFACTURER_DECLARATION"
            or record["units"] != "N-mm-MPa"
            or record["curve_type"] != "TRUE_VON_MISES_STRESS_EQUIVALENT_PLASTIC_STRAIN"):
        raise ValueError("HARDENING_SOURCE_OR_CONVENTION_UNSUPPORTED")
    e = _number(record["elastic_modulus_mpa"])
    nu = _number(record["poisson_ratio"])
    if not 1000 <= e <= 200000 or not -0.9 < nu < 0.49:
        raise ValueError("HARDENING_ELASTIC_PARAMETERS_OUT_OF_BOUNDS")
    points = record["points"]
    if not isinstance(points, list) or not 3 <= len(points) <= 256:
        raise ValueError("HARDENING_POINT_COUNT_UNSUPPORTED")
    prev_strain = -1.0
    prev_stress = -1.0
    for i, pair in enumerate(points):
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("HARDENING_POINT_FORMAT_INVALID")
        stress, plastic_strain = map(_number, pair)
        if not 0 < stress <= e or not 0 <= plastic_strain <= 1.0:
            raise ValueError("HARDENING_POINT_RANGE_INVALID")
        if (i == 0 and plastic_strain != 0.0
                or i > 0 and (plastic_strain <= prev_strain or stress < prev_stress)):
            raise ValueError("HARDENING_PLASTIC_STRAIN_OR_STRESS_NONMONOTONIC")
        prev_stress, prev_strain = stress, plastic_strain
    return {
        "validation": "PRIVATE_DECLARED_HARDENING_TABLE_STRUCTURE_ONLY",
        "point_count": len(points),
        "calculix_plasticity_admission": "NOT_ADMITTED",
        "manufacturer_batch_authenticity": "NOT_CHECKED",
        "engineering_capacity": "NOT_ADMITTED",
        "does_not_generate_solver_deck": True,
    }


def read(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 65536:
        raise ValueError("HARDENING_FILE_MISSING_OR_UNBOUNDED")
    def duplicates(pairs):
        out = {}
        for name, value in pairs:
            if name in out:
                raise ValueError("HARDENING_DUPLICATE_JSON_KEY")
            out[name] = value
        return out
    def constant(_):
        raise ValueError("HARDENING_NAN_OR_INFINITY")
    return validate(json.loads(path.read_text(encoding="utf-8"),
                               object_pairs_hook=duplicates, parse_constant=constant))


def main() -> int:
    cli = argparse.ArgumentParser()
    cli.add_argument("private_input", type=Path)
    args = cli.parse_args()
    print(json.dumps(read(args.private_input), sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
