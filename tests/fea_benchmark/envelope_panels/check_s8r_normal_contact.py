"""Isolated S8R unilateral normal contact smoke, synthetic only."""
import hashlib,json,math,re,sys
from pathlib import Path
CASES=("approach","opening","disconnected")
MESHES=(1,2)
SCOPE="ISOLATED_TWO_S8R_UNILATERAL_CONTACT"

def topology(n):
    if type(n)!=int or n not in MESHES:raise ValueError("S8R_BAD_MESH")
    nodes={};groups=[];ids=1
    for body,z in (("LOW",0.),("HIGH",1.)):
        grid={}
        for j in range(2*n+1):
            for i in range(2*n+1):
                if i%2 and j%2:continue
                grid[i,j]=ids;nodes[ids]=(i/(2*n),j/(2*n),z);ids+=1
        es=[]
        for j in range(n):
            for i in range(n):
                x,y=2*i,2*j
                es.append(tuple(grid[a,b] for a,b in ((x,y),(x+2,y),(x+2,y+2),(x,y+2),(x+1,y),(x+2,y+1),(x+1,y+2),(x,y+1))))
        groups.append((body,tuple(grid.values()),es))
    return nodes,groups

def deck(n,case):
    if case not in CASES:raise ValueError("S8R_BAD_CASE")
    coords,groups=topology(n)
    lines=["*HEADING","Synthetic S8R face-contact oracle; NOT actual curtain wall","*NODE"]
    lines += [f"{i},{x:.8f},{y:.8f},{z:.8f}" for i,(x,y,z) in coords.items()]
    surfaces={}; eid=1
    for name,ids,els in groups:
        lines.append(f"*ELEMENT,TYPE=S8R,ELSET={name}")
        surfaces[name]=[]
        for e in els:
            lines.append(str(eid)+","+",".join(map(str,e)));surfaces[name].append(eid);eid+=1
        lines.append(f"*NSET,NSET={name}_NODES")
        lines.extend(",".join(map(str,ids[i:i+12])) for i in range(0,len(ids),12))
    lines+=["*MATERIAL,NAME=SYNTHETIC","*ELASTIC","1000.,0.",
            "*SHELL SECTION,ELSET=LOW,MATERIAL=SYNTHETIC","1.",
            "*SHELL SECTION,ELSET=HIGH,MATERIAL=SYNTHETIC","1."]
    if case!="disconnected":
        lines+=["*SURFACE,NAME=LOW_TOP,TYPE=ELEMENT"]
        lines += [f"{i},SPOS" for i in surfaces["LOW"]]
        lines+=["*SURFACE,NAME=HIGH_BOTTOM,TYPE=ELEMENT"]
        lines += [f"{i},SNEG" for i in surfaces["HIGH"]]
        lines+=["*SURFACE INTERACTION,NAME=NORMAL",
                "*SURFACE BEHAVIOR,PRESSURE-OVERCLOSURE=LINEAR",
                "100000.,0.001,0.001",
                "*CONTACT PAIR,INTERACTION=NORMAL,TYPE=SURFACE TO SURFACE",
                "HIGH_BOTTOM,LOW_TOP"]
    v=-.002 if case!="opening" else .002
    lines+=["*BOUNDARY","LOW_NODES,1,6,0.","HIGH_NODES,1,2,0.",
            "HIGH_NODES,4,6,0.","*STEP,NLGEOM=YES,INC=100",
            "*STATIC","0.1,1.,0.00001,0.1","*BOUNDARY",
            f"HIGH_NODES,3,3,{v:.8f}","*NODE PRINT,NSET=LOW_NODES","U,RF",
            "*NODE PRINT,NSET=HIGH_NODES","U,RF","*END STEP",""]
    s="\n".join(lines)
    if s.count("*ELEMENT,TYPE=S8R")!=2 or s.count("*CONTACT PAIR")!=(case!="disconnected"):raise ValueError("S8R_DECK_INVALID")
    return s

def generate(path,n,case):
    p=Path(path)
    if p.exists() or p.is_symlink():raise ValueError("S8R_FRESH_WORKSPACE")
    p.mkdir(parents=True);(p/"panel.inp").write_text(deck(n,case))

def rf(txt,name):
    num=r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:(?:[EeDd][+-]?\d+)|(?:[+-]\d{2,3}))?"
    hdr=re.compile(r"(?im)^\s*forces\s+\([^\n]*\)\s+for set\s+"+name+r"\s+and time\s+("+num+r")\s*$")
    hits=list(hdr.finditer(txt))
    if not hits or abs(float(hits[-1].group(1).replace("D","E"))-1.)>1e-7:raise ValueError("S8R_RF_FINAL_MISSING")
    pat=re.compile(r"\s*(\d+)\s+("+num+r")\s+("+num+r")\s+("+num+r")\s*")
    data={}
    for row in txt[hits[-1].end():].splitlines():
        m=pat.fullmatch(row)
        if m:
            i=int(m.group(1))
            def value(k):
                return float(re.sub(r"(?<=\d)([+-]\d{2,3})$",r"E\1",m.group(k).replace("D","E")))
            v=tuple(value(k) for k in (2,3,4))
            if i in data or not all(math.isfinite(x) for x in v):raise ValueError("S8R_RF_BAD_VALUE")
            data[i]=v
        elif data:break
    if not data:raise ValueError("S8R_RF_EMPTY")
    return data

def result(root,n,case):
    p=Path(root)/f"s8r_contact_n{n}_{case}"
    files={k:p/("panel."+k) for k in ("inp","sta","dat","frd")}
    for k,f in files.items():
        if f.is_symlink() or not f.is_file() or not 0<f.stat().st_size<(64000000 if k=="frd" else 10000000):
            raise ValueError("S8R_MISSING_ARTIFACT:"+k)
    if files["inp"].read_bytes()!=deck(n,case).encode():raise ValueError("S8R_DECK_PROVENANCE")
    times=[]
    for row in files["sta"].read_text().splitlines():
        f=row.split()
        if len(f)==7 and f[0]=="1":times.append(float(f[4]))
    if not times or abs(times[-1]-1.)>1e-7:raise ValueError("S8R_SOLVER_NOT_FINISHED")
    txt=files["dat"].read_text(errors="replace")
    _,groups=topology(n);lower=rf(txt,"LOW_NODES");upper=rf(txt,"HIGH_NODES")
    if set(lower)!=set(groups[0][1]) or set(upper)!=set(groups[1][1]):raise ValueError("S8R_RF_NODE_COVERAGE")
    lo=sum(v[2] for v in lower.values());hi=sum(v[2] for v in upper.values())
    if abs(lo+hi)>max(.01,.025*abs(hi)):raise ValueError("S8R_RF_BALANCE")
    return {"lower_rf3_n":lo,"upper_rf3_n":hi,"sha256":{k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in files.items()}}

def check(root):
    data={(n,c):result(root,n,c) for n in MESHES for c in CASES}
    for n in MESHES:
        a=data[n,"approach"];o=data[n,"opening"];u=data[n,"disconnected"]
        if not (a["lower_rf3_n"]>.01 and a["upper_rf3_n"]<-.01):
            raise ValueError("S8R_APPROACH_CONTACT_TRANSFER_NOT_ESTABLISHED")
        for d in (o,u):
            if abs(d["lower_rf3_n"])>.01 or abs(d["upper_rf3_n"])>.01:
                raise ValueError("S8R_TENSILE_OR_UNLINKED_TRANSFER")
    ratio=abs(data[1,"approach"]["upper_rf3_n"])/abs(data[2,"approach"]["upper_rf3_n"])
    if not .7<ratio<1.3:raise ValueError("S8R_MESH_SENSITIVITY_UNBOUNDED")
    return {"scope":SCOPE,"two_mesh_force_ratio":ratio,"cases":{str(n):{c:data[n,c] for c in CASES} for n in MESHES},
            "absolute_contact_force_oracle":"NOT_ESTABLISHED","engineering_acceptance":"NOT_ADMITTED"}

if __name__=="__main__":
    if len(sys.argv)==5 and sys.argv[1]=="--generate":generate(sys.argv[2],int(sys.argv[3]),sys.argv[4])
    elif len(sys.argv)==2:
        print(json.dumps(check(sys.argv[1]),sort_keys=True))
        print("ISOLATED_S8R_UNILATERAL_CONTACT_SCREEN_PASS_NOT_DESIGN")
    else:raise SystemExit("usage: ROOT or --generate DIR MESH CASE")
