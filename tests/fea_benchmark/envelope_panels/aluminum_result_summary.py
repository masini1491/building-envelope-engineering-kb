"""Bounded research observations from a completed aluminum CCX run.

NALL U is observed in DAT; support translations come from the existing
P1-pressure/force reconstruction, NOT from an independent support measurement.
No stress, strain, rotational reaction, capacity or engineering admission.
"""
from __future__ import annotations

import math
from pathlib import Path

from aluminum_research_input import validate
from check_aluminum_ritz import deck_material
from check_follower_pressure import displacement_block
from check_pressure_equilibrium import parse_deck


def _vector(value: object, name: str) -> tuple[float, float, float]:
    if (not isinstance(value, (tuple, list)) or len(value) != 3
            or any(type(x) not in (int, float) or not math.isfinite(x) for x in value)):
        raise ValueError("INVALID_RESULT_VECTOR:" + name)
    return tuple(float(x) for x in value)


def summarize(*, deck: Path, dat: Path, inputs: dict, translational_balance: dict) -> dict:
    config = validate(inputs)
    nodes, elements, edge, q = parse_deck(deck)
    if not elements or len(elements) != config["mesh"] ** 2 or not edge:
        raise ValueError("REPORT_DECK_MESH_MISMATCH")
    xs = [p[0] for p in nodes.values()]
    ys = [p[1] for p in nodes.values()]
    if (min(xs) != 0 or min(ys) != 0
            or abs(max(xs) - config["width_mm"]) > 1e-6
            or abs(max(ys) - config["height_mm"]) > 1e-6
            or abs(q - config["pressure_n_mm2"]) > 1e-12):
        raise ValueError("REPORT_DECK_GEOMETRY_OR_LOAD_MISMATCH")
    e, nu, t = deck_material(deck)
    if (abs(e - config["youngs_modulus_mpa"]) > 1e-8
            or abs(nu - config["poisson_ratio"]) > 1e-12
            or abs(t - config["thickness_mm"]) > 1e-10):
        raise ValueError("REPORT_DECK_MATERIAL_MISMATCH")

    data = dat.read_text(encoding="utf-8", errors="replace")
    u = displacement_block(data, set(nodes))
    cx, cy = config["width_mm"] / 2, config["height_mm"] / 2
    center_ids = [n for n, (x, y, z) in nodes.items()
                  if abs(x - cx) < 1e-7 and abs(y - cy) < 1e-7 and abs(z) < 1e-7]
    if len(center_ids) != 1:
        raise ValueError("REPORT_CENTER_NODE_NOT_UNIQUE")
    center_id = center_ids[0]

    # Deterministic tie-break on original S8R node ID. This is NOT a claim
    # about the maximum at arbitrary points within an element/expanded solid.
    max_node = max(sorted(nodes), key=lambda nid: (math.hypot(*u[nid]), -nid))
    max_transverse_node = max(sorted(nodes), key=lambda nid: (abs(u[nid][2]), -nid))
    max_magnitude = math.hypot(*u[max_node])

    if not isinstance(translational_balance, dict):
        raise ValueError("REPORT_BALANCE_MISSING")
    applied = _vector(translational_balance.get("pressure"), "PRESSURE")
    support = _vector(translational_balance.get("reconstructed_support"), "SUPPORT")
    residual = _vector(translational_balance.get("residual"), "RESIDUAL")
    relative = translational_balance.get("relative_global_residual")
    if (type(relative) not in (int, float) or not math.isfinite(relative)
            or relative < 0 or relative > 5e-7 or applied[2] <= 0):
        raise ValueError("REPORT_BALANCE_INVALID")
    # Keep all three vectors consistent with the previously admitted
    # restricted translational balance, without inferring any moment.
    scale = max(1.0, math.hypot(*applied))
    if any(abs(applied[i] + support[i] - residual[i]) > 1e-8 * scale
           for i in range(3)):
        raise ValueError("REPORT_BALANCE_VECTOR_MISMATCH")

    return {
        "scope": "ORIGINAL_S8R_NODES_FINAL_NALL_TRANSLATIONAL_U",
        "units": {"displacement": "mm", "force": "N"},
        "displacement": {
            "observed_source": "CCX_DAT_FINAL_NALL_U",
            "nodes_covered": len(u),
            "center_node_id": center_id,
            "center_xyz_mm": list(u[center_id]),
            "max_nodal_magnitude_mm": max_magnitude,
            "max_nodal_magnitude_node_id": max_node,
            "max_abs_nodal_transverse_mm": abs(u[max_transverse_node][2]),
            "max_abs_nodal_transverse_node_id": max_transverse_node,
        },
        "translational_support": {
            "evidence_type": "RECONSTRUCTED_FROM_INTERNAL_MINUS_FOLLOWER_PRESSURE",
            "external_pressure_resultant_N": list(applied),
            "inferred_support_resultant_N": list(support),
            "residual_N": list(residual),
            "relative_force_residual": float(relative),
            "independent_support_measurement": "NOT_OBSERVED",
        },
        "stress": "NOT_OBSERVED",
        "strain": "NOT_OBSERVED",
        "rotational_support_reaction": "NOT_OBSERVED",
        "engineering_acceptance": "NOT_ADMITTED",
        "aluminum_design_manual_capacity": "NOT_COMPUTED",
    }
