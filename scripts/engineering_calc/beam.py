"""Closed-form beam sanity checks with explicit boundary conditions.

This is intentionally not a general beam solver. The caller is responsible for verifying that
its structural model matches the calculation being reviewed.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SimpleSpanUdlResult:
    reaction_each: float
    shear_max: float
    moment_max: float
    deflection_max: float


def simple_span_udl(*, span: float, line_load: float, elastic_modulus: float, inertia: float) -> SimpleSpanUdlResult:
    """Simple span with full-span uniform load.

    Use one consistent unit system. Example: N, mm, MPa (=N/mm^2), mm^4.
    Returned reaction/shear, moment and deflection follow that system.
    """
    span = float(span)
    line_load = float(line_load)
    elastic_modulus = float(elastic_modulus)
    inertia = float(inertia)
    if span <= 0 or elastic_modulus <= 0 or inertia <= 0:
        raise ValueError("span, elastic_modulus and inertia must be > 0")

    reaction = line_load * span / 2.0
    moment = line_load * span**2 / 8.0
    deflection = 5.0 * line_load * span**4 / (384.0 * elastic_modulus * inertia)
    return SimpleSpanUdlResult(
        reaction_each=reaction,
        shear_max=abs(reaction),
        moment_max=abs(moment),
        deflection_max=abs(deflection),
    )
