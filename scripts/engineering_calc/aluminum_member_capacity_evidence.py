"""受限 ADM 構件容量證據核對（不推導 ADM 設計強度）。

這是外部容量與荷載證據的 identity / completeness gate，不是 Aluminum
Design Manual chapter D/E/F/G/H 的實作。不得把任一數值利用率、使用者
聲明的標準來源、或此函式的執行成功升格為 engineering PASS。
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence


class AluminumCapacityEvidenceError(ValueError):
    """輸入結構不正確，或來源／構件身分不一致。"""


@dataclass(frozen=True)
class LimitStateComparison:
    limit_state_id: str
    demand: float
    supplied_capacity: float
    unit: str
    ratio: float
    exceeds_supplied_capacity: bool
    evidence_status: str = "USER_DECLARED_UNVERIFIED"


@dataclass(frozen=True)
class AluminumCapacityEvidenceReview:
    calculation_status: str
    declared_limit_states: tuple[str, ...]
    unresolved_limit_states: tuple[str, ...]
    comparisons: tuple[LimitStateComparison, ...]
    declared_interaction_status: str
    scope_status: str = "USER_DECLARED_LIMIT_STATE_SET_ONLY"
    standard_capacity_kernel: str = "NOT_IMPLEMENTED"
    source_authenticity: str = "NOT_INDEPENDENTLY_VERIFIED"
    engineering_acceptance: str = "NOT_ADMITTED"


_CONTEXT_FIELDS = (
    "member_role", "alloy_temper", "product_form", "weld_condition",
    "adm_edition", "design_method",
)
_SOURCE_FIELDS = (
    "alloy_temper", "product_form", "weld_condition",
    "adm_edition", "design_method",
)


def _mapping(value: object, name: str) -> Mapping:
    if not isinstance(value, Mapping):
        raise AluminumCapacityEvidenceError(f"{name} must be an object")
    return value


def _string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AluminumCapacityEvidenceError(f"{name} must be a nonempty string")
    return value.strip()


def _number(value: object, name: str, *, allow_zero: bool) -> float:
    if isinstance(value, bool):
        raise AluminumCapacityEvidenceError(f"{name} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise AluminumCapacityEvidenceError(f"{name} must be numeric") from exc
    if not isfinite(result) or result < 0 or (not allow_zero and result == 0):
        raise AluminumCapacityEvidenceError(f"{name} must be finite and positive" if not allow_zero
                                            else f"{name} must be finite and nonnegative")
    return result


def inspect_aluminum_member_capacity_evidence(
    *,
    member_context: Mapping,
    required_limit_states: Sequence[str],
    limit_state_entries: Sequence[Mapping],
    combined_action_review: Mapping,
) -> AluminumCapacityEvidenceReview:
    """核對外部給定各 limit state 的容量身分與數值比。

    required_limit_states 必須由有權的工程師獨立界定；此函式不會從
    ADM 自動找出全部適用 limit states。每一項容量均須由使用者提供
    完整的來源 locator，且來源與 member_context identity 相符。
    來源文字與 provenance 均未被本函式獨立驗真。
    """
    ctx = _mapping(member_context, "member_context")
    identity = {field: _string(ctx.get(field), f"member_context.{field}")
                for field in _CONTEXT_FIELDS}
    if identity["design_method"] not in ("ASD", "LRFD"):
        raise AluminumCapacityEvidenceError("design_method must be ASD or LRFD")
    if isinstance(required_limit_states, (str, bytes)) or not isinstance(required_limit_states, Sequence):
        raise AluminumCapacityEvidenceError("required_limit_states must be an array")
    required = tuple(_string(v, "required_limit_states entry") for v in required_limit_states)
    if not required or len(set(required)) != len(required):
        raise AluminumCapacityEvidenceError("required_limit_states must be unique and nonempty")
    if isinstance(limit_state_entries, (str, bytes)) or not isinstance(limit_state_entries, Sequence):
        raise AluminumCapacityEvidenceError("limit_state_entries must be an array")
    comparison_by_id: dict[str, LimitStateComparison] = {}
    unresolved: set[str] = set()
    observed: set[str] = set()
    for raw in limit_state_entries:
        entry = _mapping(raw, "limit_state entry")
        ident = _string(entry.get("limit_state_id"), "limit_state_id")
        if ident not in required or ident in observed:
            raise AluminumCapacityEvidenceError("duplicate or undeclared limit state")
        observed.add(ident)
        state = _string(entry.get("status"), "limit_state status")
        if state == "UNRESOLVED":
            _string(entry.get("reason"), "unresolved reason")
            unresolved.add(ident)
            continue
        if state != "EXTERNAL_CAPACITY_SUPPLIED":
            raise AluminumCapacityEvidenceError("unsupported limit state status")
        source = _mapping(entry.get("capacity_source"), "capacity_source")
        for field in _SOURCE_FIELDS:
            if _string(source.get(field), f"capacity_source.{field}") != identity[field]:
                raise AluminumCapacityEvidenceError(f"capacity_source.{field} identity mismatch")
        _string(source.get("reference_locator"), "capacity_source.reference_locator")
        unit = _string(entry.get("unit"), "limit state unit")
        if unit not in ("N", "N-mm", "MPa"):
            raise AluminumCapacityEvidenceError("limit state unit must be N, N-mm or MPa")
        demand = _number(entry.get("demand"), "demand", allow_zero=True)
        capacity = _number(entry.get("design_capacity"), "design_capacity", allow_zero=False)
        ratio = demand / capacity
        if not isfinite(ratio):
            raise AluminumCapacityEvidenceError("non-finite ratio")
        comparison_by_id[ident] = LimitStateComparison(
            limit_state_id=ident,
            demand=demand,
            supplied_capacity=capacity,
            unit=unit,
            ratio=ratio,
            exceeds_supplied_capacity=ratio > 1.0,
        )
    unresolved.update(set(required) - observed)
    combined = _mapping(combined_action_review, "combined_action_review")
    interaction_status = _string(combined.get("status"), "combined_action_review.status")
    if interaction_status not in ("UNRESOLVED", "EXTERNALLY_REVIEWED"):
        raise AluminumCapacityEvidenceError("combined action status unsupported")
    if interaction_status == "EXTERNALLY_REVIEWED":
        _string(combined.get("reference_locator"), "combined_action_review.reference_locator")
    else:
        _string(combined.get("reason"), "combined_action_review.reason")
    return AluminumCapacityEvidenceReview(
        calculation_status=("INCOMPLETE_INPUT" if unresolved or interaction_status == "UNRESOLVED"
                            else "NUMERIC_RECONCILIATION_ONLY"),
        declared_limit_states=required,
        unresolved_limit_states=tuple(name for name in required if name in unresolved),
        comparisons=tuple(comparison_by_id[name] for name in required if name in comparison_by_id),
        declared_interaction_status=interaction_status,
    )
