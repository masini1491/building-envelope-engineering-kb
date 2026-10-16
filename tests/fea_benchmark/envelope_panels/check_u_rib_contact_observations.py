"""Read-only CCX S8R U-base contact observation. Not MPC force reconstruction."""
from __future__ import annotations
import hashlib,json,math,re,sys
from pathlib import Path
MESHES=(8,16)
CASES=("toward","away","unlinked")
SCOPE="SYNTHETIC_U_BASE_CONTACT_OBSERVATIONS_NOT_ADMITTED"
NUM=r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+|[+-]\d{2,3})?"

def val(x):
    value=float(re.sub(r"(?<=\d)([+-]\d{2,3})$",r"E\1",x.replace("D","E")))
    if not math.isfinite(value):raise ValueError("U_CONTACT_DIAG_NONFINITE")
    return value

def numeric_row(chunk,count):
    for line in chunk.splitlines():
        fields=line.split()
        if len(fields)==count and all(re.fullmatch(NUM,x) for x in fields):
            return [val(x) for x in fields]
    raise ValueError("U_CONTACT_DIAG_MISSING_NUMERIC_ROW")

def contact_print(raw):
    head=re.compile(r"(?im)^\s*statistics for slave set\s+RIB_BASE_UNDERSIDE,\s*master set\s+PLATE_TOP\s+and time\s+("+NUM+r")\s*$")
    hits=list(head.finditer(raw))
    if not hits or abs(val(hits[-1].group(1))-1.)>1e-7:raise ValueError("U_CONTACT_DIAG_FINAL_SURFACE_MISSING")
    block=raw[hits[-1].end():]
    f=block.find("total surface force (fx,fy,fz)")
    a=block.find("area,  normal force (+ = tension)")
    if f<0 or a<f:raise ValueError("U_CONTACT_DIAG_SURFACE_HEADER")
    force=numeric_row(block[f:].split("center of gravity and mean normal")[0],6)
    area=numeric_row(block[a:],3)
    if area[0]<0:raise ValueError("U_CONTACT_DIAG_NEGATIVE_CONTACT_AREA")
    return {"slave_total_force_n":force[:3],"slave_total_moment_nmm":force[3:],
            "contact_area_mm2":area[0],"signed_normal_force_n":area[1],
            "shear_force_n":area[2]}

def rf(raw,name):
    head=re.compile(r"(?im)^\s*forces\s+\([^\n]*\)\s+for set\s+"+name+r"\s+and time\s+("+NUM+r")\s*$")
    hits=list(head.finditer(raw))
    if not hits or abs(val(hits[-1].group(1))-1.)>1e-7:raise ValueError("U_CONTACT_DIAG_FINAL_RF_MISSING_"+name)
    entries={}
    for line in raw[hits[-1].end():].splitlines():
        fields=line.split()
        if len(fields)==4 and fields[0].isdigit() and all(re.fullmatch(NUM,t) for t in fields[1:]):
            key=int(fields[0])
            if key in entries:raise ValueError("U_CONTACT_DIAG_DUPLICATE_NODE_"+name)
            entries[key]=tuple(val(t) for t in fields[1:])
        elif entries:break
    if not entries:raise ValueError("U_CONTACT_DIAG_EMPTY_RF_"+name)
    return {"count":len(entries),"sum_rf3_n":math.fsum(v[2] for v in entries.values())}

def observe_dat(raw,case):
    if case not in CASES:raise ValueError("U_CONTACT_DIAG_UNKNOWN_CASE")
    data={k:rf(raw,k) for k in ("PLATE_EDGE_RF","RIB_END_RF","CENTER_RF")}
    data["raw_rf3_sum_n"]=math.fsum(data[k]["sum_rf3_n"] for k in ("PLATE_EDGE_RF","RIB_END_RF","CENTER_RF"))
    if case=="unlinked":
        if "statistics for slave set RIB_BASE_UNDERSIDE" in raw:raise ValueError("U_CONTACT_DIAG_FALSE_CONTACT")
        data["contact_print"]=None
    else:data["contact_print"]=contact_print(raw)
    data["raw_rf_is_complete_mpc_balance"]="UNPROVEN"
    data["independent_contact_force_oracle"]="NOT_ESTABLISHED"
    data["engineering_acceptance"]="NOT_ADMITTED"
    return data

def observe(root):
    records={}
    for n in MESHES:
        records[str(n)]={}
        for case in CASES:
            path=Path(root)/f"u_base_contact_n{n}_{case}"/"panel.dat"
            if path.is_symlink() or not path.is_file() or not 0<path.stat().st_size<10000000:
                raise ValueError("U_CONTACT_DIAG_MISSING_DAT")
            result=observe_dat(path.read_text(encoding="utf-8",errors="replace"),case)
            result["dat_sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
            records[str(n)][case]=result
    return {"scope":SCOPE,"cases":records,"independent_global_balance":"NOT_ESTABLISHED",
            "mpc_reaction_reconstruction":"NOT_ESTABLISHED","engineering_acceptance":"NOT_ADMITTED"}

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: ROOT")
    print(json.dumps(observe(sys.argv[1]),sort_keys=True,allow_nan=False))
    print("U_CONTACT_DIAGNOSTIC_CAPTURE_ONLY_NOT_ENGINEERING_PASS")
