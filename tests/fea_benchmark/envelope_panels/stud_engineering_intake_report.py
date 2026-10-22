"""Hot 3: fixed synthetic C3D20R input gate and Chinese solver-evidence report.

No arbitrary engineering model, real wind load, steel/aluminum capacity,
calibrated welded stud or generic review.py check_type is admitted.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import tempfile
import zipfile

RUN_ID = 39721243850
ARTIFACT_ID = 12401885093
PIN_SHA256 = "d35d73f6b9f0d5f94f45e53b1c81c607d9839c77c25ea54ba654e033993933a7"
SCOPE = "C3D20R_SYNTHETIC_FOUR_Z_STATION_INPUT_ONLY"
K_CASES = {"unlinked": 0., "soft": 50., "stiff": 500.}
PRESSURES = {"positive": .0001, "negative": -.0001}
MESHES = (8, 16, 24)
GEOMETRY = {
    "panel_length_mm": 1200., "panel_width_mm": 300.,
    "panel_thickness_mm": 3., "rib_outer_width_mm": 50.,
    "rib_height_above_plate_mm": 50., "rib_thickness_mm": 3.,
    "rib_count": 1, "rib_centerline_y_mm": 0.,
}
MATERIAL = {"model": "SYNTHETIC_ISOTROPIC_ELASTIC_NOT_PRODUCT",
            "youngs_modulus_mpa": 69000., "poisson_ratio": .33}
SUPPORT = {"plate": "IDEAL_FIXED_PERIMETER_TRANSLATIONS",
           "rib": "IDEAL_FIXED_BOTH_END_TRANSLATIONS"}
UNITS = {"length": "mm", "pressure": "N/mm2", "stress": "MPa",
         "force": "N", "stiffness": "N/mm"}
POSITIONS = [150., 450., 750., 1050.]
INPUT_FIELDS = frozenset(("scope", "provenance", "geometry", "material",
                          "support", "units", "load", "connection", "mesh"))


def fail(code):
    raise ValueError("C3D20R_HOT3_" + code)


def fixture(mesh=24, case="soft", direction="positive"):
    if type(mesh) is not int or mesh not in MESHES or case not in K_CASES or direction not in PRESSURES:
        fail("FIXTURE_SCOPE")
    return {
        "scope": SCOPE, "provenance": "PUBLIC_SYNTHETIC_FIXTURE_ONLY",
        "geometry": dict(GEOMETRY), "material": dict(MATERIAL),
        "support": dict(SUPPORT), "units": dict(UNITS),
        "mesh": mesh,
        "load": {"application": "PLATE_P1", "direction": direction,
                 "signed_pressure_n_mm2": PRESSURES[direction]},
        "connection": {"model": "BILATERAL_Z_SPRING2_NO_CONTACT",
                       "case": case, "k_per_station_n_mm": K_CASES[case],
                       "station_x_mm": POSITIONS.copy()},
    }


def _compare(actual, expected, label, missing, invalid, unsupported):
    if not isinstance(actual, dict):
        invalid.append(label)
        return
    for key, wanted in expected.items():
        path = (label + "." if label else "") + key
        if key not in actual or actual[key] is None:
            missing.append(path)
            continue
        got = actual[key]
        if isinstance(wanted, dict):
            _compare(got, wanted, path, missing, invalid, unsupported)
        elif isinstance(wanted, list):
            if not isinstance(got, list) or len(got) != len(wanted):
                invalid.append(path)
            elif any(type(x) not in (int,float) or not math.isfinite(x) for x in got):
                invalid.append(path)
            elif got != wanted:
                unsupported.append(path)
        elif type(wanted) in (int,float):
            if type(got) not in (int,float) or not math.isfinite(got):
                invalid.append(path)
            elif got != wanted:
                unsupported.append(path)
        elif type(got) is not type(wanted):
            invalid.append(path)
        elif got != wanted:
            unsupported.append(path)
    for key in actual.keys() - expected.keys():
        unsupported.append((label + "." if label else "") + str(key))


def inspect(request):
    missing, invalid, unsupported = [], [], []
    if not isinstance(request, dict):
        request = {}
        invalid.append("request")
    conn = request.get("connection")
    loading = request.get("load")
    raw_mesh = request.get("mesh")
    case = conn.get("case") if isinstance(conn,dict) else None
    direction = loading.get("direction") if isinstance(loading,dict) else None
    mesh = raw_mesh if type(raw_mesh) is int and raw_mesh in MESHES else 8
    reference = fixture(mesh,case if case in K_CASES else "soft",
                        direction if direction in PRESSURES else "positive")
    _compare(request, reference, "", missing, invalid, unsupported)
    if case is not None and case not in K_CASES:
        unsupported.append("connection.case")
    if direction is not None and direction not in PRESSURES:
        unsupported.append("load.direction")
    if type(raw_mesh) is int and raw_mesh not in MESHES:
        unsupported.append("mesh")
    if missing or invalid:
        status = "INCOMPLETE_INPUT"
    elif unsupported:
        status = "UNSUPPORTED_MODEL"
    else:
        status = "SUPPORTED_SYNTHETIC_SCOPE"
    return {
        "calculation_status": status, "comparison_status": "NOT_PROVIDED",
        "missing_fields": sorted(set(missing)), "invalid_fields": sorted(set(invalid)),
        "unsupported_fields": sorted(set(unsupported)),
        "model_scope": SCOPE, "solver_evidence_replayed": False,
        "engineering_acceptance": "NOT_ADMITTED",
    }


def unique_keys(pairs):
    out = {}
    for key,value in pairs:
        if key in out:
            fail("DUPLICATE_KEY")
        out[key]=value
    return out


def nonfinite(_):
    fail("NONFINITE_JSON")


def read_request(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 32768:
        fail("REQUEST_FILE")
    return json.loads(path.read_text(encoding="utf8"),
                      object_pairs_hook=unique_keys,parse_constant=nonfinite)


def replay_zip(path):
    """Check the exact ZIP bytes then re-run canonical 18-case raw-solver verifier."""
    path = Path(path)
    if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= 20_000_000:
        fail("ARTIFACT_FILE")
    with path.open("rb") as stream:
        sha = hashlib.file_digest(stream,"sha256").hexdigest()
    if sha != PIN_SHA256:
        fail("ARTIFACT_DIGEST")
    with zipfile.ZipFile(path) as archive:
        infos=archive.infolist()
        if not 72 <= len(infos) <= 120:
            fail("ZIP_MEMBER_COUNT")
        by_name={}
        total=0
        for info in infos:
            p=PurePosixPath(info.filename)
            if (info.is_dir() or p.is_absolute() or ".." in p.parts or
                    not 1 <= len(p.parts) <= 3 or
                    info.file_size <= 0 or info.file_size > 30_000_000 or
                    ((info.external_attr >> 16) & 0o170000) == 0o120000):
                fail("UNSAFE_ZIP_MEMBER")
            canonical="/".join(p.parts[-2:]) if len(p.parts)>1 else info.filename
            if canonical in by_name:
                fail("DUPLICATE_ZIP_MEMBER")
            by_name[canonical]=info
            total += info.file_size
            if total > 200_000_000:
                fail("ZIP_SIZE")
        required={f"refine_{n}_{case}_{direction}/panel.{ext}"
                  for n in MESHES for case in K_CASES for direction in PRESSURES
                  for ext in ("inp","dat","sta","frd")}
        if not required.issubset(by_name):
            fail("ARTIFACT_COVERAGE")
        with tempfile.TemporaryDirectory(prefix="c3d20r_hot3_") as tmp:
            root=Path(tmp)
            for name,info in by_name.items():
                dst=root/name
                dst.parent.mkdir(parents=True,exist_ok=True)
                with archive.open(info) as source,dst.open("wb") as target:
                    import shutil
                    shutil.copyfileobj(source,target)
            from verify_stud_mesh_refinement_trial import verify
            result=verify(root)
    if (result.get("case_count")!=18 or
            result.get("engineering_acceptance")!="NOT_ADMITTED" or
            result.get("scope")!="SYNTHETIC_C3D20R_FIXED_FOUR_STATION_SIGNED_MESH_STUDY_NOT_DESIGN"):
        fail("UPSTREAM_EVIDENCE")
    return result


def render(request, source):
    gate=inspect(request)
    if gate["calculation_status"]!="SUPPORTED_SYNTHETIC_SCOPE":
        return gate
    if source is None:
        return {**gate,"calculation_status":"EVIDENCE_REQUIRED"}
    if source.get("case_count")!=18 or source.get("engineering_acceptance")!="NOT_ADMITTED":
        fail("INVALID_REPLAY")
    name=request["connection"]["case"]
    direction=request["load"]["direction"]
    mesh=request["mesh"]
    rows=sorted((x for x in source["cases"] if x["case"]==name and x["direction"]==direction),
                key=lambda x:x["mesh"])
    diffs=sorted((x for x in source["comparisons"] if x["case"]==name and x["direction"]==direction),
                 key=lambda x:x["coarse_mesh"])
    if [x["mesh"] for x in rows]!=list(MESHES) or [(x["coarse_mesh"],x["fine_mesh"]) for x in diffs]!=[(8,16),(16,24)]:
        fail("RESULT_COVERAGE")
    selected=next(x for x in rows if x["mesh"]==mesh)
    def fmt(value):
        if type(value) not in (int,float) or not math.isfinite(value):
            fail("RESULT_NONFINITE")
        return f"{value:.8g}"
    lines=[
        "# C3D20R 受限板肋比較｜合成研究繁中摘要","",
        "**僅限公開合成模型；非技師計算書或正式設計驗收。**","",
        f"- 指定 n{mesh}；{name}（每站合成 K={K_CASES[name]:g} N/mm）；面壓方向 {direction}。",
        "- 板 1200×300×3 mm；中心 U 肋 50×50×3 mm；四站位置 150／450／750／1050 mm。",
        "- 合成 E=69000 MPa、ν=0.33，理想固定板邊／U 肋端，P1 ±0.0001 N/mm²。",
        "- 無接觸、Z-only 雙向 SPRING2；有號 k×相對 U3 不是實物植釘拉力。","",
        "| 網格 | 板中心 U3 (mm) | 四站有號傳力 (N) | 肋端 RF3 (N) | Z 平衡殘差 (N) |",
        "|---|---:|---|---:|---:|"
    ]
    for x in rows:
        fs="／".join(fmt(f) for f in x["signed_forces_n"])
        lines.append(f"| n{x['mesh']} | {fmt(x['center_mean_u3_mm'])} | {fs} | {fmt(x['rib_end_observed_rf3_n'])} | {fmt(x['global_z_balance_residual_n'])} |")
    lines += ["","## 網格差異（研究級 5% 篩選）","",
              "| 網格 | 中心 U3 相對變化 | 最大單站傳力相對變化 |",
              "|---|---:|---:|"]
    for x in diffs:
        val="不適用（無連接）" if x["max_station_force_change_relative"] is None else f"{100*x['max_station_force_change_relative']:.3f}%"
        lines.append(f"| n{x['coarse_mesh']}→n{x['fine_mesh']} | {100*x['center_change_relative']:.3f}% | {val} |")
    lines += ["","## 來源與不適用範圍","",
              f"- 固定原始資料：GitHub Actions Run #{RUN_ID}、Artifact #{ARTIFACT_ID}、SHA-256 {PIN_SHA256}。",
              "- 本次重新由實際 solver deck、STA、DAT、FRD 獨立驗證後輸出；不接受任意報告 JSON 冒充。",
              "- 5% 不是實務設計精度，不能推定網格極限收斂。",
              "- 真正植釘 K、焊道、剪力、接觸開離、實際風壓與支承、材料設計強度均未確認。","",
              "**工程驗收：NOT_ADMITTED**",""]
    return {
        "calculation_status":"COMPUTED","comparison_status":"NOT_PROVIDED",
        "model_scope":SCOPE,"solver_evidence_replayed":True,
        "selected":{"mesh":mesh,"case":name,"direction":direction},
        "observed":{"center_u3_mm":selected["center_mean_u3_mm"],
                    "signed_four_link_forces_n":selected["signed_forces_n"],
                    "rib_rf3_n":selected["rib_end_observed_rf3_n"],
                    "global_z_residual_n":selected["global_z_balance_residual_n"]},
        "mesh_screen":source["last_refinement_status"],
        "report_zh_tw":"\n".join(lines),
        "real_stud_calibration":"NOT_ESTABLISHED",
        "engineering_acceptance":"NOT_ADMITTED",
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request_json",type=Path)
    parser.add_argument("--pinned-evidence-zip",type=Path)
    args=parser.parse_args()
    request=read_request(args.request_json)
    gate=inspect(request)
    if gate["calculation_status"]!="SUPPORTED_SYNTHETIC_SCOPE":
        out=gate
    elif args.pinned_evidence_zip is None:
        out={**gate,"calculation_status":"EVIDENCE_REQUIRED"}
    else:
        out=render(request,replay_zip(args.pinned_evidence_zip))
    print(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False))


if __name__=="__main__":
    main()
