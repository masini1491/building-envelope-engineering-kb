"""Explicit engineering-unit conversions used by calculation helpers.

This module intentionally has a small surface. Unknown conversions must not be guessed.
"""


def kpa_to_n_per_mm2(value: float) -> float:
    return float(value) / 1000.0


def kpa_m_to_n_per_mm(value: float) -> float:
    """Convert kPa*m tributary loading to N/mm line load.

    Numerically, 1 kPa * 1 m = 1 kN/m = 1 N/mm.
    """
    return float(value)


def kn_m_to_n_mm(value: float) -> float:
    return float(value) * 1_000_000.0


def n_mm_to_kn_m(value: float) -> float:
    return float(value) / 1_000_000.0


def cm4_to_mm4(value: float) -> float:
    return float(value) * 10_000.0


def mm4_to_cm4(value: float) -> float:
    return float(value) / 10_000.0
