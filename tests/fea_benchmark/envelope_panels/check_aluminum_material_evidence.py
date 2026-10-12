"""Fail-closed, user-declared material metadata *consistency* checker.

This parser does not inspect/validate manufacturer PDFs or attest properties.
Never emit evidence details or product identifiers to public repository output.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

_REQUIRED = {
    "manufacturer", "alloy_temper", "product_id", "product_form",
    "material_condition", "source_visibility", "evidence_claim",
    "thickness_range_mm", "elastic_properties",
}
_ALLOWED_VISIBILITY = frozenset(("PUBLIC", "PRIVATE"))
_EXPECTED_CLAIMS = {
    "USER_DECLARED_UNVERIFIED": "USER_DECLARED_NOT_VERIFIED",
    "MANUFACTURER_DECLARATION_ACCEPTED_BY_USER": "MANUFACTURER_DECLARATION_ACCEPTED_BY_USER",
}
_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")


def _number(value: object) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("MATERIAL_EVIDENCE_NONFINITE_OR_NONNUMERIC")
    return float(value)


def read_metadata(path: Path) -> dict:
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 4096:
        raise ValueError("MATERIAL_EVIDENCE_FILE_NOT_BOUNDED")

    def no_constant(_value):
        raise ValueError("MATERIAL_EVIDENCE_INVALID_JSON_NUMBER")

    def no_duplicate(pairs):
        d = {}
        for key, value in pairs:
            if key in d:
                raise ValueError("MATERIAL_EVIDENCE_DUPLICATE_KEY")
            d[key] = value
        return d

    obj = json.loads(path.read_text(encoding="utf-8"),
                     object_pairs_hook=no_duplicate, parse_constant=no_constant)
    if not isinstance(obj, dict):
        raise ValueError("MATERIAL_EVIDENCE_SCHEMA_MISMATCH")
    return obj


def check(selection: dict, evidence: dict) -> str:
    """Return *declared metadata consistency*, not material-source verification."""
    if not isinstance(selection, dict) or not isinstance(evidence, dict):
        raise ValueError("MATERIAL_EVIDENCE_SCHEMA_MISMATCH")
    if set(evidence) != _REQUIRED:
        raise ValueError("MATERIAL_EVIDENCE_SCHEMA_MISMATCH")
    product = selection.get("product_id")
    if (type(product) is not str or not _ID_RE.fullmatch(product)
            or type(evidence["product_id"]) is not str
            or evidence["product_id"] != product):
        raise ValueError("MATERIAL_EVIDENCE_PRODUCT_MISMATCH")
    if (evidence["manufacturer"] != selection.get("manufacturer")
            or evidence["alloy_temper"] != selection.get("alloy_temper")):
        raise ValueError("MATERIAL_EVIDENCE_ALLOY_OR_MANUFACTURER_MISMATCH")
    if (evidence["product_form"] != "sheet"
            or evidence["material_condition"] != "AS_SUPPLIED"):
        raise ValueError("MATERIAL_EVIDENCE_PRODUCT_STATE_UNSUPPORTED")
    if (type(evidence["source_visibility"]) is not str
            or evidence["source_visibility"] not in _ALLOWED_VISIBILITY
            or evidence["evidence_claim"] != _EXPECTED_CLAIMS.get(selection.get("property_evidence_status"))):
        raise ValueError("MATERIAL_EVIDENCE_STATUS_NOT_ADMITTED")
    bounds = evidence["thickness_range_mm"]
    if not isinstance(bounds, list) or len(bounds) != 2:
        raise ValueError("MATERIAL_EVIDENCE_THICKNESS_SCOPE_INVALID")
    low, high = (_number(bounds[0]), _number(bounds[1]))
    if not 0 < low <= high <= 50:
        raise ValueError("MATERIAL_EVIDENCE_THICKNESS_SCOPE_INVALID")
    thickness = _number(selection.get("thickness_mm"))
    if not low <= thickness <= high:
        raise ValueError("MATERIAL_EVIDENCE_THICKNESS_OUTSIDE_SCOPE")
    elastic = evidence["elastic_properties"]
    if not isinstance(elastic, dict) or set(elastic) != {
            "youngs_modulus_mpa", "poisson_ratio"}:
        raise ValueError("MATERIAL_EVIDENCE_ELASTIC_FIELDS_INVALID")
    for key in ("youngs_modulus_mpa", "poisson_ratio"):
        if _number(selection.get(key)) != _number(elastic[key]):
            raise ValueError("MATERIAL_EVIDENCE_PROPERTY_VALUE_MISMATCH")
    if selection["property_evidence_status"] == "MANUFACTURER_DECLARATION_ACCEPTED_BY_USER":
        return "USER_ACCEPTED_MANUFACTURER_METADATA_CONSISTENCY_ONLY"
    return "DECLARED_METADATA_CONSISTENCY_ONLY"
