"""Two isolated C3D8 cubes; unilateral normal contact numeric smoke, NOT facade design."""
import hashlib, json, math, re, sys
from pathlib import Path

CASES = {"compression": -.002, "opening": .002}
E, NU, K = 1000., 0., 100000.  # entirely synthetic; N-mm-MPa
SCOPE = "SYNTHETIC_TWO_C3D8_FRICTIONLESS_NORMAL_CONTACT"
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?"

def deck(case):
    if case not in CASES:
        raise ValueError("CONTACT_UNKNOWN_CASE")
    coords = [(0,0,0),(1,0,0),(1,1,0),(0,1,0),
              (0,0,1),(1,0,1),(1,1,1),(0,1,1),
              (0,0,1),(1,0,1),(1,1,1),(0,1,1),
              (0,0,2),(1,0,2),(1,1,2),(0,1,2)]
    out = ["*HEADING", "two independent cubes - NOT DESIGN", "*NODE"]
    out += [f"{i},{x},{y},{z}" for i,(x,y,z) in enumerate(coords,1)]
    out += ["*ELEMENT,TYPE=C3D8,ELSET=LOWER","1,1,2,3,4,5,6,7,8",
            "*ELEMENT,TYPE=C3D8,ELSET=UPPER","2,9,10,11,12,13,14,15,16",
            "*NSET,NSET=BASE","1,2,3,4","*NSET,NSET=DRIVEN","13,14,15,16",
            "*NSET,NSET=LOWER_FACE","5,6,7,8","*NSET,NSET=UPPER_FACE","9,10,11,12",
            "*MATERIAL,NAME=ARTIFICIAL","*ELASTIC",f"{E},{NU}",
            "*SOLID SECTION,ELSET=LOWER,MATERIAL=ARTIFICIAL",
            "*SOLID SECTION,ELSET=UPPER,MATERIAL=ARTIFICIAL",
            "*SURFACE,NAME=LOWER_TOP,TYPE=ELEMENT","1,S2",
            "*SURFACE,NAME=UPPER_BOTTOM,TYPE=ELEMENT","2,S1",
            "*SURFACE INTERACTION,NAME=NORMAL",
            "*SURFACE BEHAVIOR,PRESSURE-OVERCLOSURE=LINEAR",
            f"{K},0.001,0.001",
            "*CONTACT PAIR,INTERACTION=NORMAL,TYPE=SURFACE TO SURFACE",
            "UPPER_BOTTOM,LOWER_TOP",
            "*BOUNDARY","BASE,1,3,0.","13,1,2,0.","14,2,2,0.",
            "*STEP,NLGEOM=YES,INC=100","*STATIC","0.1,1.,0.00001,0.1",
            "*BOUNDARY",f"DRIVEN,3,3,{CASES[case]:.8f}",
            "*NODE PRINT,NSET=BASE","U,RF",
            "*NODE PRINT,NSET=DRIVEN","U,RF",
            "*NODE PRINT,NSET=LOWER_FACE","U",
            "*NODE PRINT,NSET=UPPER_FACE","U",
            "*END STEP",""]
    result="\n".join(out)
    if result.count("*CONTACT PAIR")!=1 or result.count("*ELEMENT,TYPE=C3D8")!=2 or any(x in result for x in ("*FRICTION","*EQUATION","SPRING2","*PLASTIC","*CLOAD")):
        raise ValueError("CONTACT_DECK_SCOPE_ERROR")
    return result

def generate(folder,case):
    if case not in CASES or folder.exists() or folder.is_symlink():
        raise ValueError("CONTACT_FRESH_WORKSPACE_REQUIRED")
    folder.mkdir(parents=True)
    (folder/"panel.inp").write_text(deck(case),encoding="utf-8")

def completed(text):
    stamp=[]
    for line in text.splitlines():
        fields=line.split()
        if len(fields)==7 and fields[0]=="1":
            stamp.append(float(fields[4]))
    if not stamp or not math.isfinite(stamp[-1]) or abs(stamp[-1]-1.)>1e-7:
        raise ValueError("CONTACT_SOLVER_NOT_COMPLETED")

def field(raw,kind,node_set):
    if kind not in ("forces","displacements") or node_set not in ("BASE","DRIVEN","LOWER_FACE","UPPER_FACE"):
        raise ValueError("CONTACT_OUTPUT_QUERY_OUT_OF_SCOPE")
    rx=r"(?im)^\s*"+kind+r"\s+\([^\n]*\)\s+for set\s+"+node_set+r"\s+and time\s+("+NUMBER+r")\s*$"
    found=list(re.finditer(rx,raw))
    if not found or abs(float(found[-1].group(1).replace("D","E"))-1.)>1e-7:
        raise ValueError("CONTACT_FINAL_FIELD_MISSING")
    rows={}
    rxrow=re.compile(r"\s*(\d+)\s+("+NUMBER+r")\s+("+NUMBER+r")\s+("+NUMBER+r")\s*")
    for line in raw[found[-1].end():].splitlines():
        if not line.strip():
            if rows: break
            continue
        m=rxrow.fullmatch(line)
        if m is None:
            if rows: break
            continue
        i=int(m.group(1))
        val=tuple(float(m.group(j).replace("D","E")) for j in (2,3,4))
        if i in rows or not all(map(math.isfinite,val)):
            raise ValueError("CONTACT_BAD_FIELD")
        rows[i]=val
    if not rows: raise ValueError("CONTACT_EMPTY_FIELD")
    return rows

def oracle(case,base,driven,lower,upper):
    if case not in CASES or any(set(g)!=set(range(lo,hi)) for g,lo,hi in
      ((base,1,5),(driven,13,17),(lower,5,9),(upper,9,13))):
        raise ValueError(f"CONTACT_NODE_COVERAGE:{case}:base={sorted(base)}:driven={sorted(driven)}:lower={sorted(lower)}:upper={sorted(upper)}")
    if any(len(v)!=3 or any(type(z) not in (float,int) or not math.isfinite(z) for z in v)
           for g in (base,driven,lower,upper) for v in g.values()):
        raise ValueError("CONTACT_BAD_VECTOR")
    rb=sum(v[2] for v in base.values())
    rt=sum(v[2] for v in driven.values())
    if abs(rb+rt)>max(.002,.015*abs(rt)):
        raise ValueError("CONTACT_FORCE_BALANCE")
    gaps=[upper[i+4][2]-lower[i][2] for i in range(5,9)]
    if case=="compression":
        # E*A*delta/(L1+L2) = 1 N; penalty adds only synthetic compliance.
        if not -.0-1.2<rt<-.8 or rb<=0 or not all(-.00035<g<.00035 for g in gaps):
            raise ValueError(f"CONTACT_COMPRESSION_ORACLE_FAIL:driven={rt:.9g}:base={rb:.9g}:gaps={gaps!r}")
    else:
        if abs(rt)>.02 or abs(rb)>.02 or not all(g>.0015 for g in gaps):
            raise ValueError("CONTACT_OPENING_ORACLE_FAIL")
    return {"driven_z_force_n":rt,"base_z_force_n":rb,
            "interface_gap_mm":gaps,"compression_1d_oracle_n":1.,
            "engineering_acceptance":"NOT_ADMITTED"}

def inspect(root,case):
    if case not in CASES: raise ValueError("CONTACT_UNKNOWN_CASE")
    folder=root/("normal_contact_"+case)
    paths={k:folder/("panel."+k) for k in ("inp","sta","dat","frd")}
    for k,p in paths.items():
        if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=(64000000 if k=="frd" else 10000000):
            raise ValueError("CONTACT_MISSING_ARTIFACT:"+k)
    if paths["inp"].read_bytes()!=deck(case).encode():
        raise ValueError("CONTACT_DECK_PROVENANCE_INVALID")
    completed(paths["sta"].read_text(encoding="ascii"))
    raw=paths["dat"].read_text(encoding="utf-8",errors="replace")
    result=oracle(case,field(raw,"forces","BASE"),field(raw,"forces","DRIVEN"),
                  field(raw,"displacements","LOWER_FACE"),field(raw,"displacements","UPPER_FACE"))
    result["artifact_sha256"]={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in paths.items()}
    return result

def assess(root):
    return {"scope":SCOPE,"cases":{c:inspect(root,c) for c in CASES},
            "synthetic_elastic_mpa":E,"synthetic_poisson":NU,"synthetic_penalty_mpa_per_mm":K,
            "real_panel_rib_contact":"NOT_ADMITTED","stud_capacity":"NOT_ADMITTED",
            "material_capacity":"NOT_ADMITTED","engineering_acceptance":"NOT_ADMITTED"}

if __name__=="__main__":
    if len(sys.argv)==4 and sys.argv[1]=="--generate":
        generate(Path(sys.argv[2]),sys.argv[3])
    elif len(sys.argv)==2:
        print(json.dumps(assess(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
        print("ISOLATED_NORMAL_CONTACT_UNILATERAL_ORACLE_PASS; NOT_DESIGN_ADMITTED")
    else:
        raise SystemExit("USAGE: check_contact_normal_pair.py ROOT | --generate DIR CASE")
