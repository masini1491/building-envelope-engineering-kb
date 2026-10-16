"""Bounded actual-shape synthetic plate/open-U S8R unilateral contact probe.

Only the U-rib base underside is a contact face. Studs deliberately remain absent.
Displacement-driven, not a wind design load or real connection test.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

from check_u_rib_shell_links import E, NU, MESHES, _configuration, _nset, mesh
from check_u_rib_interface_geometry import audit
from check_s8r_normal_contact import rf

CASES=("toward","away","unlinked")
SCOPE="SYNTHETIC_PLATE_OPEN_U_S8R_BASE_ONLY_UNILATERAL_CONTACT"
DRIVE_MM=.02
PENALTY=100000.

def reject(msg):
    raise ValueError("OPEN_U_CONTACT_"+msg)

def selected_faces(n):
    topo=mesh(n)
    geometry=audit(n)
    if (geometry["geometric_interface_gap_mm"]!=0. or
            geometry["transverse_contact_mesh"]!="NONCONFORMING" or
            geometry["rib_base_s8r_midsurface_strip_width_mm"]!=47.):
        reject("GEOMETRIC_ADMISSION")
    count_plate=len(topo["plate"])
    plate_ids=list(range(1,count_plate+1))
    rib_ids=[count_plate+4*i+j+1 for i in range(n) for j in (1,2)]
    if len(rib_ids)!=2*n or len(set(rib_ids))!=2*n:
        reject("RIB_BASE_SURFACE_SELECTION")
    for eid in rib_ids:
        e=topo["rib"][eid-count_plate-1]
        if any(abs(topo["coords"][k][2]-3.)>1e-8 for k in e):
            reject("RIB_WALL_MIXED_INTO_BASE")
    if topo["center"] in topo["clamped_plate"] or topo["center"] in topo["clamped_rib_end"]:
        reject("CENTER_SUPPORT_CONFLICT")
    return topo,plate_ids,rib_ids

def deck(n,case):
    if type(n)!=int or n not in MESHES or case not in CASES:
        reject("OUTSIDE_FIXED_CASES")
    topo,plate_ids,rib_ids=selected_faces(n)
    lines=["*HEADING",f"Synthetic panel/open-U shell contact n={n} case={case} NOT DESIGN","*NODE"]
    lines.extend(f"{nid},{x:.8f},{y:.8f},{z:.8f}" for nid,(x,y,z) in sorted(topo["coords"].items()))
    for name,els,start in (("PLATE",topo["plate"],1),
                           ("RIB",topo["rib"],1+len(topo["plate"]))):
        lines.append(f"*ELEMENT,TYPE=S8R,ELSET={name}")
        lines.extend(f"{start+i},"+",".join(map(str,e)) for i,e in enumerate(els))
    g=_configuration()
    lines.extend(["*MATERIAL,NAME=ARTIFICIAL","*ELASTIC",f"{E:.8f},{NU:.8f}",
                  "*SHELL SECTION,ELSET=PLATE,MATERIAL=ARTIFICIAL",
                  f"{g['inputs']['panel_thickness_mm']:.8f}",
                  "*SHELL SECTION,ELSET=RIB,MATERIAL=ARTIFICIAL",
                  f"{g['inputs']['rib_thickness_mm']:.8f}"])
    if case!="unlinked":
        lines.append("*SURFACE,NAME=PLATE_TOP,TYPE=ELEMENT")
        lines.extend(f"{eid},SPOS" for eid in plate_ids)
        lines.append("*SURFACE,NAME=RIB_BASE_UNDERSIDE,TYPE=ELEMENT")
        lines.extend(f"{eid},SNEG" for eid in rib_ids)
        lines.extend(["*SURFACE INTERACTION,NAME=SYNTH_NORMAL",
                      "*SURFACE BEHAVIOR,PRESSURE-OVERCLOSURE=LINEAR",
                      f"{PENALTY:.8f},0.001,0.001",
                      "*CONTACT PAIR,INTERACTION=SYNTH_NORMAL,TYPE=SURFACE TO SURFACE",
                      "RIB_BASE_UNDERSIDE,PLATE_TOP"])
    for name,nodes in (("PLATE_EDGE_RF",topo["clamped_plate"]),
                       ("RIB_END_RF",topo["clamped_rib_end"]),
                       ("CENTER_RF",(topo["center"],))):
        _nset(lines,name,nodes)
    displacement=DRIVE_MM if case!="away" else -DRIVE_MM
    lines.extend(["*BOUNDARY","PLATE_EDGE_RF,1,6,0.","RIB_END_RF,1,6,0.",
                  "*STEP,NLGEOM=YES,INC=100","*STATIC","0.1,1.,0.00001,0.1",
                  "*BOUNDARY",f"CENTER_RF,3,3,{displacement:.8f}",
                  "*NODE PRINT,NSET=PLATE_EDGE_RF","U,RF",
                  "*NODE PRINT,NSET=RIB_END_RF","U,RF",
                  "*NODE PRINT,NSET=CENTER_RF","U,RF",
                  "*NODE FILE,OUTPUT=3D","U"])
    if case!="unlinked":
        lines.extend(["*CONTACT PRINT","CF,CFN,CNUM"])
    lines.extend(["*END STEP",""])
    output="\n".join(lines)
    if (output.count("*ELEMENT,TYPE=S8R")!=2 or
            output.count("*CONTACT PAIR")!=int(case!="unlinked") or
            any(k in output for k in ("*ELEMENT,TYPE=SPRING2","*EQUATION","*RIGID BODY",
                                       "*PLASTIC","*CLOAD","*DLOAD","*FRICTION"))):
        reject("DECK_SCOPE_ESCALATION")
    return output

def generate(folder,n,case):
    target=Path(folder)
    if target.exists() or target.is_symlink():reject("WORKSPACE_NOT_FRESH")
    target.mkdir(parents=True)
    (target/"panel.inp").write_text(deck(n,case),encoding="utf-8")

def measure(root,n,case):
    target=Path(root)/f"u_base_contact_n{n}_{case}"
    files={ext:target/("panel."+ext) for ext in ("inp","sta","dat","frd")}
    for ext,p in files.items():
        size=64000000 if ext=="frd" else 10000000
        if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<size:
            reject("ARTIFACT_MISSING_"+ext)
    if files["inp"].read_bytes()!=deck(n,case).encode("utf-8"):
        reject("DECK_PROVENANCE")
    times=[]
    for line in files["sta"].read_text(encoding="ascii").splitlines():
        v=line.split()
        if len(v)==7 and v[0]=="1":
            f=float(v[4])
            if not math.isfinite(f):reject("STATUS_NONFINITE")
            times.append(f)
    if not times or abs(times[-1]-1.)>1e-7:reject("STEP_INCOMPLETE")
    txt=files["dat"].read_text(encoding="utf-8",errors="replace")
    topo,_,_=selected_faces(n)
    sums={}
    for label,nodes in (("PLATE_EDGE_RF",topo["clamped_plate"]),
                        ("RIB_END_RF",topo["clamped_rib_end"]),
                        ("CENTER_RF",(topo["center"],))):
        data=rf(txt,label)
        if set(data)!=set(nodes):reject("RF_NODE_COVERAGE_"+label)
        sums[label]=math.fsum(row[2] for row in data.values())
    total=math.fsum(sums.values())
    scale=sum(abs(v) for v in sums.values())
    if not all(math.isfinite(v) for v in sums.values()):
        reject("RF_NONFINITE")
    if abs(total)>max(.0002,0.025*scale):
        reject(f"RF_GLOBAL_Z_IMBALANCE_{total:.9g}")
    return {"plate_edge_rf3_n":sums["PLATE_EDGE_RF"],
            "rib_end_rf3_n":sums["RIB_END_RF"],
            "driven_center_rf3_n":sums["CENTER_RF"],
            "summed_support_rf3_n":total,
            "sha256":{k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in files.items()}}

def validate(observations):
    rib_forces=[]
    for n in MESHES:
        compression=observations[n,"toward"]
        opening=observations[n,"away"]
        baseline=observations[n,"unlinked"]
        # All reactions are direct solver-observed RF; no inferred stud forces.
        rib=compression["rib_end_rf3_n"]
        if not rib<-.00001:
            reject(f"TOWARD_NO_COMPRESSION_TRANSFER_{n}_{rib:.9g}")
        for case,data in (("away",opening),("unlinked",baseline)):
            if abs(data["rib_end_rf3_n"])>.0002:
                reject(f"UNWANTED_RIB_TRANSFER_{n}_{case}")
        if abs(compression["driven_center_rf3_n"]-baseline["driven_center_rf3_n"])<.00001:
            reject(f"CONTACT_NO_DRIVE_RESPONSE_{n}")
        rib_forces.append(abs(rib))
    ratio=rib_forces[0]/rib_forces[1]
    if not .35<ratio<2.8:
        reject(f"TWO_MESH_TRANSFER_DIFFERENCE_{ratio:.8g}")
    return {"rib_reaction_ratio_n8_to_n16":ratio,
            "contact_pressure_distribution_oracle":"NOT_ESTABLISHED",
            "stud_connection":"NOT_MODELED",
            "engineering_acceptance":"NOT_ADMITTED"}

def check(root):
    data={(n,c):measure(root,n,c) for n in MESHES for c in CASES}
    verdict=validate(data)
    return {"scope":SCOPE,"cases":{str(n):{c:data[n,c] for c in CASES} for n in MESHES},
            "displacement_control_mm":DRIVE_MM,
            "contact_penalty_synthetic":PENALTY,**verdict}

if __name__=="__main__":
    if len(sys.argv)==5 and sys.argv[1]=="--generate":
        generate(sys.argv[2],int(sys.argv[3]),sys.argv[4])
    elif len(sys.argv)==2:
        print(json.dumps(check(sys.argv[1]),sort_keys=True,allow_nan=False))
        print("OPEN_U_BASE_ONLY_UNILATERAL_CONTACT_BOUNDED_SCREEN_PASS_NOT_DESIGN")
    else:raise SystemExit("usage: ROOT | --generate DIR MESH CASE")
