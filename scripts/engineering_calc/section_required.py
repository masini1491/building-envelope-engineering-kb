"""Required section-property arithmetic.

Engineering authority:
knowledge/structural-design/preliminary-sizing/required-section-properties.md

The caller must supply project-approved criteria. This module does not derive allowable stress.
"""


def required_inertia(i_trial: float, delta_trial: float, delta_allow: float) -> float:
    i_trial = float(i_trial)
    delta_allow = float(delta_allow)
    if i_trial <= 0:
        raise ValueError("i_trial must be > 0")
    if delta_allow <= 0:
        raise ValueError("delta_allow must be > 0")
    return i_trial * abs(float(delta_trial)) / delta_allow


def required_section_modulus(moment_max: float, allowable_stress: float) -> float:
    allowable_stress = float(allowable_stress)
    if allowable_stress <= 0:
        raise ValueError("allowable_stress must be > 0 and must come from an approved source")
    return abs(float(moment_max)) / allowable_stress


def utilization(required: float, actual: float) -> float:
    actual = float(actual)
    if actual <= 0:
        raise ValueError("actual property must be > 0")
    return float(required) / actual
