"""C3D8 U-section raw RF3 control, not shell-contact or engineering admission."""
from __future__ import annotations
import hashlib,json,math,re,sys
from pathlib import Path
from probe_c3d8_u_contact import MESHES,CASES,deck,model
from check_u_rib_contact_observations import rf,contact_print
TOL=0.002
SCOPE="SYNTHETIC_C3D8_OPEN_U_RF3_BALANCE_OBSERVATION"

def evaluate(root,n,case):
    if type(n) is not int or n not in MESHES or case not in CASES:raise ValueError("C3D8_SCOPE")
    root=Path(root)/f"u_c3d8_control_n{n}_{case}"
    files={ext:root/f"panel.{ext}" for ext in ("inp","dat","sta","frd")}
    for ext,f in files.items():
        if f.is_symlink() or not f.is_file() or not 0<f.stat().st_size<(64000000 if ext=="frd" else 10000000):
            raise ValueError("C3D8_ARTIFACT_"+ext)
    if files["inp"].read_bytes()!=deck(n,case).encode():raise ValueError("C3D8_INPUT_PROVENANCE")
    times=[]
    for ln in files["sta"].read_text(encoding="ascii").splitlines():
        parts=ln.split()
        if len(parts)==7 and parts[0]=="1":
            t=float(parts[4])
            if not math.isfinite(t):raise ValueError("C3D8_NONFINITE_TIME")
            times.append(t)
    if not times or abs(times[-1]-1.)>1e-7:raise ValueError("C3D8_INCOMPLETE")
    dat=files["dat"].read_text(encoding="utf-8",errors="replace")
    _,_,_,_,plate,rib,center=model(n,case)
    groups={"PLATE_EDGE_RF":plate,"RIB_END_RF":rib,"CENTER_RF":center}
    raw={}
    for name,nodes in groups.items():
        value=rf(dat,name,expected_nodes=nodes)
        if value["count"]!=len(nodes):raise ValueError("C3D8_RF_COVERAGE_"+name)
        raw[name]=value["sum_rf3_n"]
    total=math.fsum(raw.values())
    if abs(total)>TOL:raise ValueError("C3D8_RAW_RF3_IMBALANCE")
    if case=="unlinked":
        if "statistics for slave set" in dat:raise ValueError("C3D8_FALSE_UNLINKED")
        cp=None
    else:cp=contact_print(dat)
    return {"raw_rf3_by_set_n":raw,"raw_rf3_balance_n":total,
            "contact_print":cp,"raw_rf3_balance_state":"OBSERVED_WITHIN_BOUNDED_TOLERANCE",
            "contact_separation":"NOT_ESTABLISHED","shell_mpc_reconstruction":"NOT_ESTABLISHED",
            "engineering_acceptance":"NOT_ADMITTED",
            "sha256":{ext:hashlib.sha256(f.read_bytes()).hexdigest() for ext,f in files.items()}}

def observe(root):
    return {"scope":SCOPE,"raw_rf3_tolerance_n":TOL,
            "cases":{str(n):{case:evaluate(root,n,case) for case in CASES} for n in MESHES},
            "shell_equivalence":"NOT_ESTABLISHED","engineering_acceptance":"NOT_ADMITTED"}
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: ROOT")
    print(json.dumps(observe(sys.argv[1]),sort_keys=True,allow_nan=False))
