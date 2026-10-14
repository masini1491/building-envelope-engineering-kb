"""Read-only engineering-facing report for the exact synthetic rib-thickness sweep.

Accepts the JSON emitted by check_rib_thickness_sweep.check(root), whose
model/solver provenance has already been verified in the same run. This
postprocessor does not reverify raw solver artifacts or compute design capacity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

THICKNESSES = (2.0, 3.0)
MESHES = (8, 16)
HEIGHTS = (0, 4, 8)
_SCOPE = "SYNTHETIC_CENTER_RIB_TWO_DISCRETE_THICKNESSES_ONLY"
_NOT_ADMITTED = "NOT_ADMITTED"
_KEYS = {
    "scope", "plate_width_mm", "plate_height_mm", "pressure_n_mm2",
    "youngs_modulus_mpa", "poisson_ratio", "center_displacement_mm",
    "flat_ritz_by_thickness", "flat_plate_Kirchhoff_t_cubed_ratio",
    "flat_plate_solver_t3_over_t2_ratio", "two_mesh_differences",
    "rib_web_connection", "rigid_rotation_or_fastener_force",
    "pressure_balance_six_components", "material_capacity",
    "engineering_acceptance", "cases",
}


def _real(value: object, label: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("RIB_REPORT_INVALID_NUMBER:" + label)
    return float(value)


def _same(got: object, want: float, label: str, *, rel: float = 1e-9) -> None:
    val = _real(got, label)
    if not math.isclose(val, want, rel_tol=rel, abs_tol=1e-12):
        raise ValueError("RIB_REPORT_INCONSISTENT:" + label)


def _mapping(value: object, expected: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("RIB_REPORT_SCHEMA_INVALID:" + label)
    return value


def _hash(value: object, label: str) -> None:
    if (not isinstance(value, str) or len(value) != 64
            or any(c not in "0123456789abcdef" for c in value)):
        raise ValueError("RIB_REPORT_INVALID_ARTIFACT_DIGEST:" + label)


def _observations(result: dict) -> dict[tuple[float, int, int], float]:
    _mapping(result, _KEYS, "ROOT")
    if result["scope"] != _SCOPE or result["rib_web_connection"] != "IDEAL_SHARED_S8R_NODES":
        raise ValueError("RIB_REPORT_MODEL_OUTSIDE_SCOPE")
    for key in ("engineering_acceptance", "material_capacity",
                "rigid_rotation_or_fastener_force", "pressure_balance_six_components"):
        if result[key] != _NOT_ADMITTED:
            raise ValueError("RIB_REPORT_BOUNDARY_INVALID:" + key)
    for key, value in (("plate_width_mm", 100.0), ("plate_height_mm", 100.0),
                       ("pressure_n_mm2", .0001), ("youngs_modulus_mpa", 69000.0),
                       ("poisson_ratio", .33)):
        _same(result[key], value, key)
    fields = _mapping(result["center_displacement_mm"], {str(t) for t in THICKNESSES}, "THICKNESS")
    cases = _mapping(result["cases"],
                     {f"t{t}_n{n}_h{h}" for t in THICKNESSES for n in MESHES for h in HEIGHTS},
                     "CASES")
    vals = {}
    for t in THICKNESSES:
        meshes = _mapping(fields[str(t)], {str(n) for n in MESHES}, "MESH")
        for n in MESHES:
            heights = _mapping(meshes[str(n)], {str(h) for h in HEIGHTS}, "HEIGHT")
            for h in HEIGHTS:
                val = _real(heights[str(h)], "CENTER")
                if not 0 < val < .05*t:
                    raise ValueError("RIB_REPORT_DISPLACEMENT_OUTSIDE_SCOPE")
                vals[t, n, h] = val
                name = f"t{t}_n{n}_h{h}"
                item = _mapping(cases[name],
                                {"center_mm", "height_mm", "thickness_mm", "mesh", "sha256"},
                                "CASE:" + name)
                _same(item["center_mm"], val, "CASE_CENTER:" + name)
                _same(item["height_mm"], h, "CASE_HEIGHT:" + name)
                _same(item["thickness_mm"], t, "CASE_THICKNESS:" + name)
                if type(item["mesh"]) is not int or item["mesh"] != n:
                    raise ValueError("RIB_REPORT_CASE_MESH_MISMATCH:" + name)
                digests = _mapping(item["sha256"], {"inp", "dat", "sta", "frd"}, "DIGESTS")
                for kind, digest in digests.items():
                    _hash(digest, name + ":" + kind)

    ritz = _mapping(result["flat_ritz_by_thickness"], {str(t) for t in THICKNESSES}, "RITZ")
    mesh_diffs = _mapping(result["two_mesh_differences"],
                          {f"t{t}_h{h}" for t in THICKNESSES for h in HEIGHTS},
                          "MESH_DIFF")
    for t in THICKNESSES:
        ref = _mapping(ritz[str(t)], {"ritz_center_mm", "relative_difference"}, "RITZ_CASE")
        expected_ref = _real(ref["ritz_center_mm"], "RITZ_VALUE")
        if expected_ref <= 0:
            raise ValueError("RIB_REPORT_RITZ_NOT_POSITIVE")
        difference = abs(vals[t, 16, 0] - expected_ref) / expected_ref
        _same(ref["relative_difference"], difference, "RITZ_RELATIVE_DIFFERENCE")
        if difference > .20:
            raise ValueError("RIB_REPORT_RITZ_SCREEN_FAILED")
        for n in MESHES:
            if not vals[t,n,0] > vals[t,n,4] > vals[t,n,8]:
                raise ValueError("RIB_REPORT_RIB_HEIGHT_ORDER_FAILED")
        for h in HEIGHTS:
            ratio = abs(vals[t,16,h]-vals[t,8,h]) / vals[t,16,h]
            _same(mesh_diffs[f"t{t}_h{h}"], ratio, "MESH_DIFFERENCE")
            if ratio > .15:
                raise ValueError("RIB_REPORT_MESH_SCREEN_FAILED")
    theory = (2/3)**3
    _same(result["flat_plate_Kirchhoff_t_cubed_ratio"], theory, "THEORY_RATIO")
    ratio = vals[3.,16,0] / vals[2.,16,0]
    _same(result["flat_plate_solver_t3_over_t2_ratio"], ratio, "SOLVER_RATIO")
    if abs(ratio-theory)/theory > .20:
        raise ValueError("RIB_REPORT_KIRCHHOFF_SCREEN_FAILED")
    ritz_ratio = (ritz["3.0"]["ritz_center_mm"] / ritz["2.0"]["ritz_center_mm"])
    _same(ritz_ratio, theory, "RITZ_THICKNESS_RATIO")
    for n in MESHES:
        for h in HEIGHTS:
            if not vals[3.,n,h] < vals[2.,n,h]:
                raise ValueError("RIB_REPORT_THICKNESS_ORDER_FAILED")
    return vals


def render(result: dict, *, source_digest: str | None = None) -> str:
    vals = _observations(result)
    if source_digest is not None:
        _hash(source_digest, "SOURCE_JSON")
    def fmt(val: float) -> str:
        return f"{val:.9g}"
    lines = [
        "# 中心加勁肋板厚與肋高比較｜合成研究摘要",
        "",
        "**只限受限 S8R 合成算例；非帷幕牆工程設計或容量合格判定。**",
        "",
        "## 模型與讀值來源",
        "",
        "- 板面 100 × 100 mm；板厚與肋厚同步採 2 或 3 mm；中心肋高 0／4／8 mm。",
        "- 四邊理想固定，肋與板完全共節點；肋端沒有真實扣件模型。",
        "- 等向線彈性 E=69000 MPa、ν=0.33；P=0.0001 N/mm² 的受限合成 follower 面壓。",
        "- 真實 CalculiX 2.21 輸出中的中心節點 U3 幅值；本表不是整片鋁板的最大撓度。",
        "- 網格 8／16 只是兩種離散取樣，不能據此證明一般網格收斂階數。",
        "",
        "## 16 網格：板肋厚度及肋高比較",
        "",
        "| 中心肋高 (mm) | 2 mm 板肋中心 | 3 mm 板肋中心 | 增厚後中心撓度降幅 | 2 mm 加肋降幅 | 3 mm 加肋降幅 |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for h in HEIGHTS:
        u2, u3 = vals[2.,16,h], vals[3.,16,h]
        thick_drop = 100*(1-u3/u2)
        rib2 = 100*(1-u2/vals[2.,16,0])
        rib3 = 100*(1-u3/vals[3.,16,0])
        lines.append(f"| {h} | {fmt(u2)} mm | {fmt(u3)} mm | {thick_drop:.2f}% | {rib2:.2f}% | {rib3:.2f}% |")
    lines += [
        "",
        "上述百分比屬同一指定載重、幾何、材料及邊界之**觀測差異**，不是可移用到其他尺寸的設計效率。",
        "",
        "## 解析參照與網格敏感度",
        "",
        f"- 無肋薄板理論厚度撓度比 (2/3)³：{fmt((2/3)**3)}。",
        f"- 無肋 n=16 真實求解撓度比（3 mm／2 mm）：{fmt(vals[3.,16,0]/vals[2.,16,0])}。",
        "",
        "| 肋高 (mm) | 2 mm：n8 與 n16 差異 | 3 mm：n8 與 n16 差異 |",
        "| ---: | ---: | ---: |",
    ]
    for h in HEIGHTS:
        a=abs(vals[2.,16,h]-vals[2.,8,h])/vals[2.,16,h]*100
        b=abs(vals[3.,16,h]-vals[3.,8,h])/vals[3.,16,h]*100
        lines.append(f"| {h} | {a:.2f}% | {b:.2f}% |")
    lines += [
        "",
        "## 證據與不可推論事項",
        "",
        "- 12 組解由上游 `check_rib_thickness_sweep.check()` 檢查原始 deck、DAT、STA、FRD 的範圍與 SHA-256，再產生輸入 JSON；本報表僅重驗 JSON 欄位及數值一致性，不重新讀取或驗證原始求解器檔案。",
        "- 原始各案例 `inp`／`dat`／`sta`／`frd` SHA-256 保留在機器可讀 JSON，供追溯，不等於本報表已重算各檔雜湊。",
        "- 沒有板內任意位置的精確最大撓度、Gauss 點應力峰值、實際折邊、螺絲／角碼反力、連接滑移、屈曲、塑性或 ADM 容量驗證。",
        "- 不應由此比較結果推導實際工程合格與否；新增工程參數必須有自己的獨立驗證。",
        "",
    ]
    if source_digest is not None:
        lines += [f"來源 JSON SHA-256（本次讀入位元組）：`{source_digest}`", ""]
    lines += ["**工程適用狀態：EVIDENCE GATED／MATERIAL_CAPACITY_NOT_ADMITTED／GENERAL_GLOBAL_BALANCE_NOT_ADMITTED**", ""]
    return "\n".join(lines)


def _unique(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for k,v in pairs:
        if k in out:
            raise ValueError("RIB_REPORT_DUPLICATE_JSON_KEY")
        out[k] = v
    return out


def _reject_constant(value: str) -> None:
    raise ValueError("RIB_REPORT_NONFINITE_JSON:" + value)


def main() -> int:
    p = argparse.ArgumentParser(description="Format previously verified synthetic rib-thickness sweep JSON")
    p.add_argument("result_json", type=Path)
    args = p.parse_args()
    path = args.result_json
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 4_000_000:
        raise SystemExit("RIB_REPORT_INPUT_FILE_NOT_BOUNDED")
    raw = path.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8"),object_pairs_hook=_unique,parse_constant=_reject_constant)
        output = render(data,source_digest=hashlib.sha256(raw).hexdigest())
    except (ValueError,UnicodeError,TypeError,KeyError) as exc:
        raise SystemExit("RIB_REPORT_INVALID_EVIDENCE:" + str(exc)) from exc
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
