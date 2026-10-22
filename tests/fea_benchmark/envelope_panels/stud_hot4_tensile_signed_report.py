"""Hot 4: tensile failure-test statistics versus signed C3D20R model transfer.

A PRIVATE specimen strength JSON is compared only with the exact Hot 1/2
SYNTHETIC n8/n16/n24 bilateral Z SPRING2 solver evidence. Neither output
is a real welded-stud tensile demand, design allowable, or utilization.
The CLI obtains solver data ONLY by replaying exact SHA-256 pinned ZIP
through stud_engineering_intake_report.replay_zip(). Raw specimen values and
source identity are never copied into the research report.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from stud_connection_evidence_gate import assess, load as load_specimen
from stud_engineering_intake_report import (
    PRESSURES, MESHES, K_CASES, fixture, inspect, read_request, replay_zip,
)
from stud_tensile_strength_screen import calculate, load_input

SCOPE = "C3D20R_HOT4_SIGNED_Z_LINK_VS_TENSILE_TEST_RESEARCH_ONLY"
UPSTREAM_SCOPE = "SYNTHETIC_C3D20R_FIXED_FOUR_STATION_SIGNED_MESH_STUDY_NOT_DESIGN"
EXPECTED_KEYS = {"mesh", "case", "direction", "nominal_signed_pressure_n_per_mm2",
                 "synthetic_k_n_per_mm", "stud_positions_mm", "signed_forces_n",
                 "max_signed_force_magnitude_n", "total_signed_force_n",
                 "rib_end_observed_rf3_n", "rib_balance_residual_n",
                 "global_z_balance_residual_n", "center_mean_u3_mm"}


def reject(code):
    raise ValueError("C3D20R_HOT4_" + code)


def _positive_finite(value, code):
    if type(value) not in (int,float) or not math.isfinite(value) or value <= 0:
        reject(code)
    return float(value)


def compare(request, raw_test, replayed, specimen_metadata=None):
    """Only CLI path replaying pinned solver ZIP establishes upstream provenance.

    Internal use accepts a solver dict for synthetic unit tests only; callers
    must not claim this represents external verified evidence.
    """
    gate = inspect(request)
    if gate["calculation_status"] != "SUPPORTED_SYNTHETIC_SCOPE":
        return {**gate, "hot4_scope": SCOPE,
                "tensile_statistical_review": "NOT_RUN",
                "ratio_is_design_check": False}
    test = calculate(raw_test)
    metadata = {"status": "NOT_PROVIDED", "missing_fields": [],
                "source_coherence": "NOT_CHECKED",
                "interface_relevance": "NOT_ESTABLISHED"}
    if specimen_metadata is not None:
        details = assess(specimen_metadata)
        if specimen_metadata["source_class"] == "NO_EVIDENCE":
            reject("STRENGTH_WITH_NO_EVIDENCE")
        if specimen_metadata["source_sha256"] != raw_test["source_sha256"]:
            reject("SPECIMEN_SOURCE_DIGEST_MISMATCH")
        metadata = {
            "status": details["readiness"],
            "source_coherence": "SAME_DECLARED_SHA256_NOT_AUTHENTICATED",
            "missing_fields": details["missing_fields"],
            "interface_relevance": "NOT_ESTABLISHED",
        }
    if replayed is None:
        return {
            "calculation_status": "EVIDENCE_REQUIRED",
            "hot4_scope": SCOPE,
            "tensile_statistical_review": test["calculation_status"],
            "specimen_metadata_review": metadata,
            "solver_evidence_replayed": False,
            "ratio_is_design_check": False,
            "engineering_acceptance": "NOT_ADMITTED",
        }
    if (not isinstance(replayed,dict) or replayed.get("scope") != UPSTREAM_SCOPE or
            replayed.get("engineering_acceptance") != "NOT_ADMITTED" or
            replayed.get("case_count") != 18 or
            replayed.get("local_connector_force_convergence") != "NOT_ESTABLISHED" or
            replayed.get("mesh_independent_true_stud_force") != "NOT_ESTABLISHED"):
        reject("UPSTREAM_SCOPE")
    all_cases = replayed.get("cases")
    if not isinstance(all_cases,list) or len(all_cases) != 18:
        reject("UPSTREAM_COVERAGE")
    indexed={}
    for row in all_cases:
        if not isinstance(row,dict) or set(row) != EXPECTED_KEYS:
            reject("UPSTREAM_CASE_SCHEMA")
        key=(row["mesh"],row["case"],row["direction"])
        if key in indexed or key[0] not in MESHES or key[1] not in K_CASES or key[2] not in PRESSURES:
            reject("UPSTREAM_CASE_ID")
        if (row["synthetic_k_n_per_mm"] != K_CASES[key[1]] or
                row["nominal_signed_pressure_n_per_mm2"] != PRESSURES[key[2]] or
                row["stud_positions_mm"] != [150.,450.,750.,1050.]):
            reject("UPSTREAM_CASE_PARAMETERS")
        values=row["signed_forces_n"]
        if not isinstance(values,list) or len(values)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in values):
            reject("UPSTREAM_STATION_FORCES")
        if any(type(row[field]) not in (int,float) or not math.isfinite(row[field]) for field in
               ("max_signed_force_magnitude_n","total_signed_force_n","rib_end_observed_rf3_n",
                "rib_balance_residual_n","global_z_balance_residual_n","center_mean_u3_mm")):
            reject("UPSTREAM_NONFINITE")
        if (abs(max(map(abs,values))-row["max_signed_force_magnitude_n"])>1e-8 or
                abs(math.fsum(values)-row["total_signed_force_n"])>1e-8 or
                abs(math.fsum([row["total_signed_force_n"],row["rib_end_observed_rf3_n"]]))>0.002 or
                abs(row["rib_balance_residual_n"])>0.002 or
                abs(row["global_z_balance_residual_n"])>0.002):
            reject("UPSTREAM_FORCE_BALANCE")
        indexed[key]=row
    required={(n,c,d) for n in MESHES for c in K_CASES for d in PRESSURES}
    if set(indexed)!=required:
        reject("UPSTREAM_CASE_COVERAGE")
    mesh=request["mesh"]
    name=request["connection"]["case"]
    selected = [indexed[(mesh,name,d)] for d in PRESSURES]
    if name != "unlinked":
        for row in selected:
            sign = 1 if row["direction"] == "positive" else -1
            if sign * row["center_mean_u3_mm"] <= 0 or any(sign*v<=0 for v in row["signed_forces_n"]):
                reject("UPSTREAM_SIGN_REVERSAL")
        if any(a*b>=0 for a,b in zip(selected[0]["signed_forces_n"],selected[1]["signed_forces_n"])):
            reject("UPSTREAM_PAIR_SIGN")
    candidate = _positive_finite(test["candidate_allowable_load_n"], "CANDIDATE_LOAD")
    rows=[]
    for row in selected:
        max_force = row["max_signed_force_magnitude_n"]
        arithmetic = max_force/candidate
        if not math.isfinite(arithmetic):
            reject("ARITHMETIC_OVERFLOW")
        rows.append({
            "direction": row["direction"],
            "signed_pressure_n_mm2":row["nominal_signed_pressure_n_per_mm2"],
            "synthetic_four_station_signed_forces_n":row["signed_forces_n"],
            "max_synthetic_force_magnitude_n":max_force,
            "candidate_tensile_force_n_NOT_APPROVED":candidate,
            "arithmetic_magnitude_ratio_NOT_UTILIZATION":arithmetic,
            "rib_balance_residual_n":row["rib_balance_residual_n"],
            "global_z_balance_residual_n":row["global_z_balance_residual_n"],
        })
    def fmt(v):
        if type(v) not in (int,float) or not math.isfinite(v):
            reject("REPORT_NONFINITE")
        return f"{v:.7g}"
    lines=[
        "# Hot 4｜植釘抗拉試驗候選值與 C3D20R 合成傳力研究對照","",
        "**本表不是技師設計計算書；不得將純數值比例解釋為實際植釘使用率或安全驗算。**","",
        "## 抗拉破壞荷載統計（依指定技師算法）","",
        f"- 試體數：{test['sample_count']}；統計原單位：{test['source_unit']}。",
        f"- 平均破壞荷載：{fmt(test['sample_mean_failure_load'])}；樣本標準差（n−1）：{fmt(test['sample_standard_deviation'])}。",
        f"- 工程師指定安全係數：{fmt(test['engineer_selected_safety_factor'])}；候選容許抗拉力：{fmt(candidate)} N／支（未核准）。",
        "- 算法採「平均值減一個樣本標準差，再除以安全係數」；不是標準核准的特徵值或信賴下限。",
        f"- 破壞模式計數：{', '.join(k+'='+str(v) for k,v in sorted(test['failure_mode_counts'].items()))}。",
        f"- 破壞位置覆核：{test['fracture_mode_review']}；來源真實性：外部審查未完成。",
        f"- 試體欄位資料完整性：{metadata['status']}；試體與合成模型的力學等效性：NOT_ESTABLISHED。",
        "",
        "## 相同指定網格、連接案例之正反向合成對照","",
        "| 面壓方向 | 四站點模型有號 Z 力 (N) | 最大模型力絕對值 (N) | 純數值比（非使用率） |",
        "|---|---|---:|---:|",
    ]
    for row in rows:
        forces="／".join(fmt(x) for x in row["synthetic_four_station_signed_forces_n"])
        lines.append(f"| {row['direction']} | {forces} | {fmt(row['max_synthetic_force_magnitude_n'])} | "
                     f"{fmt(100*row['arithmetic_magnitude_ratio_NOT_UTILIZATION'])}% |")
    lines += ["","## 來源與未通過設計門檻","",
              "- C3D20R 正反向 solver 證據由 SHA-256 固定 ZIP 的原始 .inp/.sta/.dat/.frd 重新驗證；不得以自行填寫的 JSON 冒充求解。",
              "- 原始試驗荷載只限本機私人輸入，公開 CI 僅使用虛構數據；報表不複製逐支破壞荷載、私人來源雜湊或可識別試體資料。",
              "- 雙向 Z-only SPRING2 不含接觸開離、剪力、焊道失效或實際接頭剛度。",
              "- 目前無法從模型正負方向確定真實鋁植釘的拉力或壓力，也沒有實際風壓與支承條件。",
              "- 即使數值比例很小，仍不得宣布強度合格；正式設計仍須補接頭及工程適用證據。","",
              "**工程驗收：NOT_ADMITTED**",""]
    return {
        "calculation_status":"COMPUTED_RESEARCH_ONLY",
        "hot4_scope":SCOPE,
        "sample_count":test["sample_count"],
        "statistical_method":test["method"],
        "candidate_allowable_n_NOT_APPROVED":candidate,
        "failure_mode_counts":test["failure_mode_counts"],
        "fracture_mode_review":test["fracture_mode_review"],
        "specimen_metadata_review":metadata,
        "solver_evidence_replayed":True,
        "mesh":mesh,"connection_case":name,
        "directional_research_rows":rows,
        "ratio_is_design_check":False,
        "real_stud_tension_compression_mapping":"NOT_ESTABLISHED",
        "physical_stud_stiffness":"NOT_ESTABLISHED",
        "allowable_design_authority":"NOT_ESTABLISHED",
        "project_loads_and_supports":"NOT_ESTABLISHED",
        "report_zh_tw":"\n".join(lines),
        "engineering_acceptance":"NOT_ADMITTED",
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("private_strength_json",type=Path)
    parser.add_argument("bounded_synthetic_model_json",type=Path)
    parser.add_argument("--specimen-evidence-json",type=Path)
    parser.add_argument("--pinned-evidence-zip",type=Path)
    args=parser.parse_args()
    request=read_request(args.bounded_synthetic_model_json)
    raw_strength=load_input(args.private_strength_json)
    specimen=(load_specimen(args.specimen_evidence_json)
              if args.specimen_evidence_json is not None else None)
    gate=inspect(request)
    if gate["calculation_status"]!="SUPPORTED_SYNTHETIC_SCOPE":
        output=compare(request,raw_strength,None,specimen)
    elif args.pinned_evidence_zip is None:
        output=compare(request,raw_strength,None,specimen)
    else:
        output=compare(request,raw_strength,replay_zip(args.pinned_evidence_zip),specimen)
    print(json.dumps(output,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False))


if __name__=="__main__":
    main()
