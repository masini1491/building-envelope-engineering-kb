"""Read-only full ORIGINAL-node RF3 diagnostic for synthetic S8R active contact.

The expanded S8R internal nodes are NOT represented by this original-node set.
No interpretation as true full MPC balance or design contact capacity is made.
"""
from __future__ import annotations
import hashlib,json,math,sys
from pathlib import Path
from check_u_rib_base_contact import deck as original_deck,selected_faces
from check_u_rib_shell_links import MESHES,_nset
from check_s8r_normal_contact import rf
from check_u_rib_contact_observations import contact_print

CASES=("toward",)
SCOPE="SYNTHETIC_S8R_ALL_ORIGINAL_NODE_RF3_READ_ONLY_OBSERVATION"
SETS=("PLATE_EDGE_RF","RIB_END_RF","CENTER_RF")
NAME="ALL_ORIGINAL_RF"

def deck(n):
    if type(n) is not int or n not in MESHES:
        raise ValueError("S8R_ALL_ORIGINAL_SCOPE")
    topo,_,_=selected_faces(n)
    source=original_deck(n,"toward")
    lines=source.splitlines()
    marker="*MATERIAL,NAME=ARTIFICIAL"
    if lines.count(marker)!=1 or lines.count("*NODE FILE,OUTPUT=3D")!=1:
        raise ValueError("S8R_ALL_ORIGINAL_UNEXPECTED_DECK")
    extra=[]
    _nset(extra,NAME,sorted(topo["coords"]))
    pos=lines.index(marker)
    lines[pos:pos]=extra
    pos=lines.index("*NODE FILE,OUTPUT=3D")
    lines[pos:pos]=[f"*NODE PRINT,NSET={NAME}","U,RF"]
    result="\n".join(lines)+"\n"
    # Only two node-print cards and the ALL-original NSET have been inserted.
    if (result.count("*CONTACT PAIR")!=source.count("*CONTACT PAIR") or
        result.count("*ELEMENT,TYPE=S8R")!=2 or
        result.count(f"*NODE PRINT,NSET={NAME}")!=1 or
        result.count(f"*NSET,NSET={NAME}")!=1):
        raise ValueError("S8R_ALL_ORIGINAL_SCOPE_CHANGE")
    return result

def generate(folder,n):
    path=Path(folder)
    if path.exists() or path.is_symlink():
        raise ValueError("S8R_ALL_ORIGINAL_WORKSPACE_NOT_FRESH")
    payload=deck(n)
    path.mkdir(parents=True)
    (path/"panel.inp").write_text(payload,encoding="utf-8")

def _files(folder,n):
    path=Path(folder)/f"u_s8r_all_original_rf_n{n}_toward"
    out={ext:path/f"panel.{ext}" for ext in ("inp","dat","sta","frd")}
    for ext,p in out.items():
        if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<(64000000 if ext=="frd" else 10000000):
            raise ValueError("S8R_ALL_ORIGINAL_MISSING_"+ext)
    if out["inp"].read_bytes()!=deck(n).encode("utf-8"):
        raise ValueError("S8R_ALL_ORIGINAL_DECK_PROVENANCE")
    rows=[]
    for line in out["sta"].read_text(encoding="ascii").splitlines():
        v=line.split()
        if len(v)==7 and v[0]=="1":
            try: t=float(v[4])
            except ValueError as e:raise ValueError("S8R_ALL_ORIGINAL_BAD_TIME") from e
            if not math.isfinite(t):raise ValueError("S8R_ALL_ORIGINAL_BAD_TIME")
            rows.append(t)
    if not rows or abs(rows[-1]-1.)>1e-7:
        raise ValueError("S8R_ALL_ORIGINAL_INCOMPLETE")
    return out

def analyze_text(txt,n):
    topo,_,_=selected_faces(n)
    actual=rf(txt,NAME)
    expected=set(topo["coords"])
    if set(actual)!=expected:
        raise ValueError("S8R_ALL_ORIGINAL_NODE_SET_MISMATCH")
    ids={
       "PLATE_EDGE_RF":set(topo["clamped_plate"]),
       "RIB_END_RF":set(topo["clamped_rib_end"]),
       "CENTER_RF":{topo["center"]},
    }
    supports=set().union(*ids.values())
    if len(supports)!=sum(map(len,ids.values())):
        raise ValueError("S8R_ALL_ORIGINAL_SUPPORT_OVERLAP")
    reported={}
    for key, node_ids in ids.items():
        original=rf(txt,key)
        if set(original)!=node_ids:raise ValueError("S8R_ALL_ORIGINAL_SUPPORT_COVERAGE_"+key)
        for node in node_ids:
            if any(abs(a-b)>max(1e-8,1e-7*max(abs(a),abs(b))) for a,b in zip(original[node],actual[node])):
                raise ValueError("S8R_ALL_ORIGINAL_DUPLICATED_RF_CONFLICT_"+key)
        reported[key]=math.fsum(v[2] for v in original.values())
    free=expected-supports
    free_sum=math.fsum(actual[k][2] for k in free)
    supported_sum=math.fsum(reported.values())
    all_sum=math.fsum(v[2] for v in actual.values())
    if not all(math.isfinite(v) for v in (*reported.values(),free_sum,supported_sum,all_sum)):
        raise ValueError("S8R_ALL_ORIGINAL_NONFINITE_SUM")
    if abs((supported_sum+free_sum)-all_sum)>max(1e-8,1e-8*abs(all_sum)):
        raise ValueError("S8R_ALL_ORIGINAL_PARTITION_MISMATCH")
    observed=contact_print(txt)
    return {
        "mesh_n":n,"all_original_node_count":len(expected),
        "supported_original_node_count":len(supports),
        "other_original_node_count":len(free),
        "reported_support_rf3_by_set_n":reported,
        "reported_support_rf3_sum_n":supported_sum,
        "other_original_nodes_rf3_sum_n":free_sum,
        "all_original_nodes_rf3_sum_n":all_sum,
        "max_abs_other_original_node_rf3_n":max((abs(actual[k][2]) for k in free),default=0.),
        "contact_slave_cf_z_n":observed["slave_total_force_n"][2],
        "contact_print_area_mm2":observed["contact_area_mm2"],
        "expanded_internal_nodes_included":False,
        "global_mpc_force_balance":"NOT_ESTABLISHED",
        "engineering_acceptance":"NOT_ADMITTED"
    }

def observe(root):
    output={}
    for n in MESHES:
        files=_files(root,n)
        result=analyze_text(files["dat"].read_text(encoding="utf-8",errors="replace"),n)
        result["sha256"]={ext:hashlib.sha256(p.read_bytes()).hexdigest() for ext,p in files.items()}
        output[str(n)]=result
    return {"scope":SCOPE,"cases":output,
            "all_original_nodes_not_all_expanded_solver_nodes":True,
            "mpc_ownership":"NOT_ESTABLISHED",
            "engineering_acceptance":"NOT_ADMITTED"}

if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--generate":
        generate(sys.argv[2],int(sys.argv[3]))
    elif len(sys.argv)==2:
        print(json.dumps(observe(sys.argv[1]),sort_keys=True,allow_nan=False))
    else:
        raise SystemExit("usage: ROOT | --generate DIR N")
