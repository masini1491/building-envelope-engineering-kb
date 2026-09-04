"""Calculation-chain reconciliation helpers for document review.

These helpers detect arithmetic discontinuities. They do not determine whether the
engineering model, standard, load source, or acceptance criterion is correct.
"""

from dataclasses import dataclass
from math import fsum, isfinite, prod
from typing import Iterable, Sequence

from .compare import Comparison, compare_values


@dataclass(frozen=True)
class AuditStep:
    name: str
    reported: float
    recomputed: float
    comparison: Comparison


@dataclass(frozen=True)
class ProductAudit:
    factors: tuple[float, ...]
    recomputed: float
    comparison: Comparison


@dataclass(frozen=True)
class ForceBalanceAudit:
    applied_sum: float
    reaction_sum: float
    residual: float
    comparison: Comparison


def audit_value(
    name: str,
    *,
    reported: float,
    recomputed: float,
    abs_tol: float = 1e-9,
    rel_tol: float = 1e-6,
) -> AuditStep:
    if not name.strip():
        raise ValueError("audit step name must not be blank")
    comparison = compare_values(reported, recomputed, abs_tol=abs_tol, rel_tol=rel_tol)
    return AuditStep(
        name=name,
        reported=comparison.reported,
        recomputed=comparison.recomputed,
        comparison=comparison,
    )


def audit_product(
    *,
    factors: Sequence[float],
    reported: float,
    abs_tol: float = 1e-9,
    rel_tol: float = 1e-6,
) -> ProductAudit:
    if not factors:
        raise ValueError("at least one factor is required")
    normalized = tuple(float(value) for value in factors)
    if not all(isfinite(value) for value in normalized):
        raise ValueError("all factors must be finite")
    recomputed = prod(normalized)
    comparison = compare_values(reported, recomputed, abs_tol=abs_tol, rel_tol=rel_tol)
    return ProductAudit(factors=normalized, recomputed=recomputed, comparison=comparison)


def audit_force_balance(
    *,
    applied_forces: Iterable[float],
    reactions: Iterable[float],
    abs_tol: float = 1e-9,
    rel_tol: float = 1e-6,
) -> ForceBalanceAudit:
    """Check static force balance using one signed force convention.

    Equilibrium is checked as ``sum(applied) + sum(reactions) = 0``.
    """
    applied = tuple(float(value) for value in applied_forces)
    reaction_values = tuple(float(value) for value in reactions)
    if not all(isfinite(value) for value in (*applied, *reaction_values)):
        raise ValueError("forces must be finite")
    applied_sum = fsum(applied)
    reaction_sum = fsum(reaction_values)
    residual = applied_sum + reaction_sum
    comparison = compare_values(0.0, residual, abs_tol=abs_tol, rel_tol=rel_tol)
    return ForceBalanceAudit(
        applied_sum=applied_sum,
        reaction_sum=reaction_sum,
        residual=residual,
        comparison=comparison,
    )
