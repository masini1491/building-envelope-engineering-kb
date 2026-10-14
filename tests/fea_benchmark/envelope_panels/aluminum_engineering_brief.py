"""Human-readable, research-only summary of an existing aluminum CCX JSON result.

This is a postprocessor, NOT a design calculator. No new model, solver,
fastener load, admissible stress, or capacity is introduced.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from aluminum_research_input import validate

EXPECTED_SCOPE = "RECTANGULAR_FOUR_EDGE_CLAMPED_LINEAR_ELASTIC_S8R_NLGEOM_P1"
TENSOR_SOURCE = "CCX_FRD_EXTRAPOLATED_AVERAGED_EXPANDED_NODE_TENSOR"
SUPPORT_SOURCE = "RECONSTRUCTED_FROM_INTERNAL_MINUS_FOLLOWER_PRESSURE"
HEX = set("0123456789abcdef")


def _real(value: object, label: str, *, nonnegative: bool = False) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("BRIEF_INVALID_NUMBER:" + label)
    if nonnegative and value < 0:
        raise ValueError("BRIEF_NEGATIVE_NUMBER:" + label)
    return float(value)


def _vector(value: object, label: str) -> tuple[float, float, float]:
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        raise ValueError("BRIEF_INVALID_VECTOR:" + label)
    return tuple(_real(v, label) for v in value)


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or not set(value) <= HEX:
        raise ValueError("BRIEF_INVALID_DIGEST:" + label)
    return value


def render(result: dict) -> str:
    if not isinstance(result, dict) or result.get("execution_status") != "ALUMINUM_PARAMETRIC_RESEARCH_EVIDENCE_PASS":
        raise ValueError("BRIEF_SOLVER_EVIDENCE_NOT_ACCEPTED")
    if result.get("model_scope") != EXPECTED_SCOPE:
        raise ValueError("BRIEF_MODEL_OUTSIDE_SCOPE")
    if (result.get("engineering_acceptance") != "NOT_ADMITTED"
            or result.get("global_six_component_balance") != "NOT_ADMITTED"
            or result.get("aluminum_design_manual_capacity") != "NOT_COMPUTED"
            or result.get("rotational_support_reaction") != "UNOBSERVED"):
        raise ValueError("BRIEF_ENGINEERING_BOUNDARY_INVALID")
    config = validate(result.get("inputs"))
    observations = result.get("research_observations")
    if not isinstance(observations, dict) or observations.get("engineering_acceptance") != "NOT_ADMITTED":
        raise ValueError("BRIEF_OBSERVATIONS_UNAVAILABLE")
    displacement = observations.get("displacement")
    if not isinstance(displacement, dict) or displacement.get("observed_source") != "CCX_DAT_FINAL_NALL_U":
        raise ValueError("BRIEF_DISPLACEMENT_NOT_OBSERVED")
    center = _vector(displacement.get("center_xyz_mm"), "CENTER")
    max_u3 = _real(displacement.get("max_abs_nodal_transverse_mm"), "NODAL_U3", nonnegative=True)
    max_u = _real(displacement.get("max_nodal_magnitude_mm"), "NODAL_MAG", nonnegative=True)
    if (type(displacement.get("nodes_covered")) is not int or displacement["nodes_covered"] <= 0
            or max_u3 + 1e-12 < abs(center[2]) or max_u + 1e-12 < max_u3):
        raise ValueError("BRIEF_DISPLACEMENT_COVERAGE_INVALID")
    stress = observations.get("stress")
    if not isinstance(stress, dict) or (stress.get("evidence_type") != TENSOR_SOURCE
            or stress.get("units") != "MPa" or stress.get("design_capacity") != "NOT_COMPUTED"
            or stress.get("integration_point_extreme") != "NOT_OBSERVED"
            or stress.get("independent_numerical_oracle") != "NOT_ESTABLISHED"):
        raise ValueError("BRIEF_STRESS_NOT_ADMITTED")
    component = stress.get("max_abs_component_label")
    if component not in ("SXX", "SYY", "SZZ", "SXY", "SYZ", "SZX"):
        raise ValueError("BRIEF_STRESS_COMPONENT_INVALID")
    component_abs = _real(stress.get("max_abs_component"), "STRESS", nonnegative=True)
    signed = _real(stress.get("max_abs_component_signed_value"), "SIGNED_STRESS")
    if not math.isclose(component_abs, abs(signed), abs_tol=1e-9, rel_tol=1e-8):
        raise ValueError("BRIEF_STRESS_SIGNED_MISMATCH")
    supports = observations.get("translational_support")
    if (not isinstance(supports, dict) or supports.get("evidence_type") != SUPPORT_SOURCE
            or supports.get("independent_support_measurement") != "NOT_OBSERVED"):
        raise ValueError("BRIEF_SUPPORT_NOT_INDEPENDENT")
    pressure = _vector(supports.get("external_pressure_resultant_N"), "PRESSURE")
    reaction = _vector(supports.get("inferred_support_resultant_N"), "SUPPORT")
    residual = _vector(supports.get("residual_N"), "RESIDUAL")
    relative = _real(supports.get("relative_force_residual"), "RESIDUAL_RATIO", nonnegative=True)
    if relative > 5e-7 or any(abs(pressure[i] + reaction[i] - residual[i]) > 1e-8 * max(1.,math.hypot(*pressure)) for i in range(3)):
        raise ValueError("BRIEF_FORCE_RECONSTRUCTION_INCONSISTENT")
    prov = result.get("artifact_provenance")
    if not isinstance(prov, dict):
        raise ValueError("BRIEF_PROVENANCE_MISSING")
    digests = {k:_digest(prov.get(k),k) for k in ("input_sha256", "solver_sha256", "dat_sha256", "frd_sha256", "sta_sha256")}
    area = config["width_mm"] * config["height_mm"]
    initial_nominal = area * config["pressure_n_mm2"]
    def f(v: float) -> str:
        return f"{v:.9g}"
    def xyz(vec: tuple[float,float,float]) -> str:
        return "(" + ", ".join(f(v) for v in vec) + ")"
    return "\n".join([
        "# 鋁板 S8R 研究結果摘要（非工程設計認可）",
        "",
        "**執行證據：受限合成研究數值 PASS；工程容量：NOT_ADMITTED。**",
        "",
        "## 指定模型與輸入",
        f"- 理想模型：矩形四邊固定、等向線彈性 S8R、NLGEOM follower P1 面壓；網格 {config['mesh']}×{config['mesh']}。",
        f"- 尺寸／板厚：{f(config['width_mm'])} × {f(config['height_mm'])} × {f(config['thickness_mm'])} mm。",
        f"- 明確指定材料：E={f(config['youngs_modulus_mpa'])} MPa、ν={f(config['poisson_ratio'])}；不依牌號自動帶入強度。",
        "- 材料來源標籤：輸入中有使用者明確聲明；為避免公開報告洩漏私人來源，摘要不複製標籤內容，亦不認證真偽。",
        f"- 面壓：{f(config['pressure_n_mm2'])} N/mm²；初始平面面積名義力 qA={f(initial_nominal)} N（非 follower 實際合力）。",
        "",
        "## 求解器觀測（非容量檢核）",
        f"- 原始 S8R 節點中心平移 (Ux,Uy,Uz) = {xyz(center)} mm。",
        f"- 原始節點最大 |Uz| = {f(max_u3)} mm；最大平移向量大小 = {f(max_u)} mm（只限取樣節點，不是連續場極值）。",
        f"- 展開節點之外插／平均應力最大絕對分量：{component} = {f(signed)} MPa（幅值 {f(component_abs)} MPa）；不是積分點峰值、不是設計應力。",
        f"- follower pressure 重建外力 (Fx,Fy,Fz) = {xyz(pressure)} N。",
        f"- 由內力／壓力重建之支承合力 (Fx,Fy,Fz) = {xyz(reaction)} N；殘差 = {xyz(residual)} N。",
        "",
        "## 必須保留的限制",
        "- 支承合力是重建量，**不是**獨立量得的扣件／角碼反力；轉動反力矩未觀測。",
        "- 應力是外插／平均的 expanded-node 張量分量，不是 Gauss 點峰值或構件容量。",
        "- 不含實際折板／加勁肋參數化、開孔、接觸、真實連接、屈曲、塑性、ADM 強度或合格判斷。",
        "- 材料證據來源由上游輸入聲明管理；本摘要不認證材料屬性與實際供貨。",
        "",
        "## 原始執行產物 SHA-256（取自上游結果，不代表本工具重新核算 hash）",
        *(f"- {k}: `{v}`" for k,v in digests.items()),
        "",
        "**工程設計驗收：NOT_ADMITTED；完整全域六分量平衡：NOT_ADMITTED。**",
        "",
    ])


def main() -> int:
    p = argparse.ArgumentParser(description="Format existing CCX aluminum research JSON; no solver execution")
    p.add_argument("result_json", type=Path)
    arg = p.parse_args()
    path = arg.result_json
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 4_000_000:
        raise SystemExit("BRIEF_INPUT_NOT_BOUNDED_REGULAR_FILE")
    def unique(pairs):
        d = {}
        for k,v in pairs:
            if k in d:
                raise ValueError("BRIEF_DUPLICATE_JSON_KEY")
            d[k] = v
        return d
    def reject_constant(value):
        raise ValueError("BRIEF_NONFINITE_JSON")
    try:
        report = render(json.loads(path.read_text(encoding="utf-8"),object_pairs_hook=unique,parse_constant=reject_constant))
    except (ValueError,TypeError,KeyError) as exc:
        raise SystemExit(f"BRIEF_EVIDENCE_REJECTED:{exc}") from exc
    print(report, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())