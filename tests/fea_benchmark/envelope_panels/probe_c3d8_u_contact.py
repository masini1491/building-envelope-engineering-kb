"""Explicit-C3D8 U-rib versus plate contact control; synthetic, not design."""
from __future__ import annotations
import sys
from pathlib import Path

MESHES = (8, 16, 24)
CASES = ("toward", "away", "unlinked")
CLEARANCE_CASE = "clearance"
CLEARANCE_MM = 0.1  # synthetic initial geometry offset, NOT a field tolerance


def model(n, case):
    if type(n) is not int or n not in MESHES or case not in CASES+(CLEARANCE_CASE,):
        raise ValueError("U_SOLID_SCOPE")
    nodes, ids, elements, plate, rib_base = {}, {}, {}, [], []
    body_by_node = {}

    def node(body, x, y, z):
        key = (body, round(x, 7), round(y, 7), round(z, 7))
        if key not in ids:
            k = len(ids) + 1
            ids[key] = k
            nodes[k] = (x, y, z)
            body_by_node[k] = body
        return ids[key]

    def cell(body, x0, x1, y0, y1, z0, z1):
        eid = len(elements) + 1
        elements[eid] = (body, tuple(node(body, x, y, z) for x,y,z in (
            (x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
            (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))))
        return eid

    xs = [1200*i/n for i in range(n+1)]
    ys = [-150+300*i/n for i in range(n+1)]
    for i in range(n):
        for j in range(n):
            plate.append(cell("PLATE",xs[i],xs[i+1],ys[j],ys[j+1],-1.5,1.5))
    xr = [1200*i/(2*n) for i in range(2*n+1)]
    for i in range(2*n):
        for y0,y1 in ((-25.,-22.),(-22.,22.),(22.,25.)):
            rib_base.append(cell("RIB",xr[i],xr[i+1],y0,y1,1.5,4.5))
        for y0,y1 in ((-25.,-22.),(22.,25.)):
            for z0,z1 in ((4.5,26.5),(26.5,51.5)):
                cell("RIB",xr[i],xr[i+1],y0,y1,z0,z1)
    ps = tuple(k for k,(x,y,z) in nodes.items() if body_by_node[k]=="PLATE" and
               (x in (0.,1200.) or y in (-150.,150.)))
    rs = tuple(k for k,(x,y,z) in nodes.items() if body_by_node[k]=="RIB" and x in (0.,1200.))
    center=(ids[("PLATE",600.,0.,-1.5)],ids[("PLATE",600.,0.,1.5)])
    if not ps or not rs or set(ps)&set(rs) or set(center)&set(ps):
        raise ValueError("U_SOLID_SUPPORT")
    if case==CLEARANCE_CASE:
        # Lift the ENTIRE independent U-solid; keep connection-free topology and supports.
        nodes={k:(x,y,z+(CLEARANCE_MM if body_by_node[k]=="RIB" else 0.))
               for k,(x,y,z) in nodes.items()}
    if len(elements)!=n*n+14*n or len(rib_base)!=6*n:
        raise ValueError("U_SOLID_TOPOLOGY")
    return nodes,elements,tuple(plate),tuple(rib_base),ps,rs,center


def deck(n,case):
    nodes,elements,plate,base,ps,rs,center=model(n,case)
    out=["*HEADING",f"Synthetic explicit C3D8 open-U n={n} {case} NOT DESIGN","*NODE"]
    out += [f"{k},{x:.8f},{y:.8f},{z:.8f}" for k,(x,y,z) in nodes.items()]
    for body in ("PLATE","RIB"):
        out.append(f"*ELEMENT,TYPE=C3D8,ELSET={body}")
        out += [str(k)+","+",".join(map(str,conn)) for k,(b,conn) in elements.items() if b==body]
    for name,group in (("PLATE_EDGE_RF",ps),("RIB_END_RF",rs),("CENTER_RF",center)):
        out.append("*NSET,NSET="+name)
        out += [",".join(map(str,group[i:i+12])) for i in range(0,len(group),12)]
    out += ["*MATERIAL,NAME=SYNTH","*ELASTIC","69000.,0.33",
            "*SOLID SECTION,ELSET=PLATE,MATERIAL=SYNTH",
            "*SOLID SECTION,ELSET=RIB,MATERIAL=SYNTH"]
    if case!="unlinked":
        out += ["*SURFACE,NAME=PLATE_TOP,TYPE=ELEMENT"] + [f"{k},S2" for k in plate]
        out += ["*SURFACE,NAME=RIB_BASE_UNDERSIDE,TYPE=ELEMENT"] + [f"{k},S1" for k in base]
        out += ["*SURFACE INTERACTION,NAME=NORMAL",
                "*SURFACE BEHAVIOR,PRESSURE-OVERCLOSURE=LINEAR","100000.,0.001,0.001",
                "*CONTACT PAIR,INTERACTION=NORMAL,TYPE=SURFACE TO SURFACE",
                "RIB_BASE_UNDERSIDE,PLATE_TOP"]
    displ = -0.02 if case in ("away",CLEARANCE_CASE) else 0.02
    out += ["*BOUNDARY","PLATE_EDGE_RF,1,3,0.","RIB_END_RF,1,3,0.",
            "*STEP,NLGEOM=YES,INC=100","*STATIC","0.1,1.,0.00001,0.1",
            "*BOUNDARY",f"CENTER_RF,3,3,{displ:.8f}"]
    for name in ("PLATE_EDGE_RF","RIB_END_RF","CENTER_RF"):
        out += ["*NODE PRINT,NSET="+name,"U,RF"]
    out += ["*NODE FILE,OUTPUT=3D","U"]
    if case!="unlinked":
        out += ["*CONTACT PRINT,SLAVE=RIB_BASE_UNDERSIDE,MASTER=PLATE_TOP","CF,CFN,CNUM"]
    out += ["*END STEP",""]
    inp="\n".join(out)
    if inp.count("*ELEMENT,TYPE=C3D8")!=2 or inp.count("*CONTACT PAIR")!=(case!="unlinked"):
        raise ValueError("U_SOLID_DECK_CONTRACT")
    return inp

if __name__=="__main__":
    if len(sys.argv)!=5 or sys.argv[1]!="--generate":
        raise SystemExit("usage: --generate EMPTY_DIRECTORY n CASE")
    folder=Path(sys.argv[2])
    if folder.exists() or folder.is_symlink():
        raise ValueError("U_SOLID_WORKSPACE_NOT_FRESH")
    inp=deck(int(sys.argv[3]),sys.argv[4])
    folder.mkdir(parents=True)
    (folder/"panel.inp").write_text(inp,encoding="utf-8")
