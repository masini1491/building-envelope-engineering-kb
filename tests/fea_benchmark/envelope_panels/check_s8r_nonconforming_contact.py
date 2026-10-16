"""Nonconforming S8R shell face contact; synthetic research only."""
import hashlib,json,math,sys
from pathlib import Path
from check_s8r_normal_contact import topology,rf,check as conforming_check,CASES
PAIRS=((1,2),(2,1))
SCOPE="NONCONFORMING_S8R_SYNTHETIC_CONTACT"

def bad(code):
    raise ValueError("NONCONFORMING_S8R_"+code)

def faces(nlow,nhigh):
    if type(nlow)!=int or type(nhigh)!=int or (nlow,nhigh) not in PAIRS:
        bad("PAIR")
    allnodes={};groups=[];nextid=1
    for n,idx in ((nlow,0),(nhigh,1)):
        coords,raw=topology(n)
        name,ids,elements=raw[idx]
        remap={}
        for old in ids:
            remap[old]=nextid
            allnodes[nextid]=coords[old]
            nextid+=1
        group=(name,tuple(remap[k] for k in ids),
               tuple(tuple(remap[k] for k in element) for element in elements))
        groups.append(group)
        if len(group[1])!=3*n*n+4*n+1 or len(group[2])!=n*n:
            bad("COUNT")
        area=0.
        for element in group[2]:
            a,b,c,d=[allnodes[k] for k in element[:4]]
            det=(b[0]-a[0])*(d[1]-a[1])-(b[1]-a[1])*(d[0]-a[0])
            if abs(det-1/(n*n))>1e-8:bad("NORMAL_OR_AREA")
            if any(abs(allnodes[k][2]-idx)>1e-8 for k in element):
                bad("MIDSURFACE_OFFSET")
            area+=det
        if abs(area-1)>1e-8:bad("FACE_AREA")
    if set(groups[0][1])&set(groups[1][1]):
        bad("SHARED_NODE")
    return allnodes,groups

def deck(nlow,nhigh,case):
    if case not in CASES:bad("CASE")
    coords,groups=faces(nlow,nhigh)
    s=["*HEADING","Nonconforming isolated S8R; NOT ENGINEERING DESIGN","*NODE"]
    s.extend(f"{k},{x:.8f},{y:.8f},{z:.8f}" for k,(x,y,z) in coords.items())
    elid=1;surface={}
    for name,ids,els in groups:
        s.append(f"*ELEMENT,TYPE=S8R,ELSET={name}")
        surface[name]=[]
        for e in els:
            s.append(str(elid)+","+",".join(map(str,e)))
            surface[name].append(elid)
            elid+=1
        s.append(f"*NSET,NSET={name}_NODES")
        s.extend(",".join(map(str,ids[i:i+12])) for i in range(0,len(ids),12))
    s+=["*MATERIAL,NAME=SYNTHETIC","*ELASTIC","1000.,0.",
        "*SHELL SECTION,ELSET=LOW,MATERIAL=SYNTHETIC","1.",
        "*SHELL SECTION,ELSET=HIGH,MATERIAL=SYNTHETIC","1."]
    if case!="disconnected":
        s+=["*SURFACE,NAME=LOW_TOP,TYPE=ELEMENT"]
        s += [f"{k},SPOS" for k in surface["LOW"]]
        s+=["*SURFACE,NAME=HIGH_BOTTOM,TYPE=ELEMENT"]
        s += [f"{k},SNEG" for k in surface["HIGH"]]
        s+=["*SURFACE INTERACTION,NAME=NORMAL",
            "*SURFACE BEHAVIOR,PRESSURE-OVERCLOSURE=LINEAR",
            "100000.,0.001,0.001",
            "*CONTACT PAIR,INTERACTION=NORMAL,TYPE=SURFACE TO SURFACE",
            "HIGH_BOTTOM,LOW_TOP"]
    displacement=.002 if case=="opening" else -.002
    s+=["*BOUNDARY","LOW_NODES,1,6,0.","HIGH_NODES,1,2,0.",
        "HIGH_NODES,4,6,0.","*STEP,NLGEOM=YES,INC=100",
        "*STATIC","0.1,1.,0.00001,0.1","*BOUNDARY",
        f"HIGH_NODES,3,3,{displacement:.8f}",
        "*NODE PRINT,NSET=LOW_NODES","U,RF",
        "*NODE PRINT,NSET=HIGH_NODES","U,RF","*END STEP",""]
    out="\n".join(s)
    if out.count("*ELEMENT,TYPE=S8R")!=2 or out.count("*CONTACT PAIR")!=int(case!="disconnected"):
        bad("DECK")
    return out

def generate(path,nlow,nhigh,case):
    p=Path(path)
    if p.exists() or p.is_symlink():bad("FRESH_WORKSPACE")
    p.mkdir(parents=True)
    (p/"panel.inp").write_text(deck(nlow,nhigh,case))

def observe(root,nlow,nhigh,case):
    path=Path(root)/f"s8r_nonconform_{nlow}_{nhigh}_{case}"
    files={k:path/("panel."+k) for k in ("inp","sta","dat","frd")}
    for k,f in files.items():
        if f.is_symlink() or not f.is_file() or not 0<f.stat().st_size<(64000000 if k=="frd" else 10000000):
            bad("MISSING_"+k)
    if files["inp"].read_bytes()!=deck(nlow,nhigh,case).encode():
        bad("DECK_PROVENANCE")
    complete=[]
    for line in files["sta"].read_text().splitlines():
        p=line.split()
        if len(p)==7 and p[0]=="1":
            t=float(p[4])
            if not math.isfinite(t):bad("STA_NONFINITE")
            complete.append(t)
    if not complete or abs(complete[-1]-1.)>1e-7:bad("NO_FINAL_TIME")
    raw=files["dat"].read_text(errors="replace")
    _,groups=faces(nlow,nhigh)
    bottom=rf(raw,"LOW_NODES")
    top=rf(raw,"HIGH_NODES")
    if set(bottom)!=set(groups[0][1]) or set(top)!=set(groups[1][1]):
        bad("NODE_COVERAGE")
    lo=sum(v[2] for v in bottom.values())
    hi=sum(v[2] for v in top.values())
    if not math.isfinite(lo+hi) or abs(lo+hi)>max(.01,.025*abs(hi)):
        bad("FORCE_BALANCE")
    return {"lower_rf3_n":lo,"upper_rf3_n":hi,
            "sha256":{k:hashlib.sha256(f.read_bytes()).hexdigest() for k,f in files.items()}}

def compare(results,baseline):
    if not math.isfinite(baseline) or baseline<=.01:bad("BASELINE")
    strengths=[]
    for p in PAIRS:
        a=results[p,"approach"]
        if not(a["lower_rf3_n"]>.01 and a["upper_rf3_n"]<-.01):
            bad("COMPRESSION")
        for c in ("opening","disconnected"):
            o=results[p,c]
            if abs(o["lower_rf3_n"])>.01 or abs(o["upper_rf3_n"])>.01:
                bad("TENSILE_OR_DISCONNECTED_TRANSFER")
        measured=abs(a["upper_rf3_n"])
        if not .65<measured/baseline<1.35:
            bad(f"CONFORMING_COMPARISON_{p}_{measured:.8g}_{baseline:.8g}")
        strengths.append(measured)
    if not .7<strengths[0]/strengths[1]<1.3:bad("MESH_ORDER_REVERSAL")
    return strengths

def check(root):
    prior=conforming_check(root)
    if prior["scope"]!="ISOLATED_TWO_S8R_UNILATERAL_CONTACT":
        bad("BASELINE_SCOPE")
    baseline=abs(prior["cases"]["2"]["approach"]["upper_rf3_n"])
    d={(p,c):observe(root,p[0],p[1],c) for p in PAIRS for c in CASES}
    strengths=compare(d,baseline)
    return {"scope":SCOPE,"cases":{f"{a}_{b}":{c:d[(a,b),c] for c in CASES} for a,b in PAIRS},
            "conforming_2_2_force_n":baseline,"nonconforming_forces_n":strengths,
            "absolute_force_independent_oracle":"NOT_ESTABLISHED",
            "open_u_geometry":"NOT_MODELED","engineering_acceptance":"NOT_ADMITTED"}

if __name__=="__main__":
    if len(sys.argv)==6 and sys.argv[1]=="--generate":
        generate(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),sys.argv[5])
    elif len(sys.argv)==2:
        print(json.dumps(check(sys.argv[1]),sort_keys=True,allow_nan=False))
        print("NONCONFORMING_S8R_BOUNDED_CONTACT_SCREEN_PASS_NOT_DESIGN")
    else:raise SystemExit("usage: --generate DIR LOW HIGH CASE | ROOT")
