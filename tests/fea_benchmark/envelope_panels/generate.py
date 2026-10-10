"""Synthetic glass and aluminum panel FEA benchmark models; NOT capacity checks."""
from __future__ import annotations
import argparse
from pathlib import Path

CONFIG={
 "glass":dict(E=70000.0,nu=0.20,t=2.0,edge="simple",q_small=0.0001,q_large=0.6,coefficient=0.00406),
 "aluminum":dict(E=69000.0,nu=0.33,t=2.0,edge="clamped",q_small=0.0001,q_large=0.6,coefficient=0.00126)
}
A=100.
def build(material,n,load,out):
    if material not in CONFIG or n not in (4,8,16) or load not in ("small","large"):
        raise ValueError("invalid fixture")
    c=CONFIG[material];out.mkdir(parents=True,exist_ok=True);nodes={}
    def node(i,j):
        p=(i,j)
        if p not in nodes:nodes[p]=len(nodes)+1
        return nodes[p]
    elems=[]
    for j in range(n):
        for i in range(n):
            positions=[(2*i,2*j),(2*i+2,2*j),(2*i+2,2*j+2),(2*i,2*j+2),(2*i+1,2*j),(2*i+2,2*j+1),(2*i+1,2*j+2),(2*i,2*j+1)]
            elems.append([node(*p) for p in positions])
    lines=["*HEADING",f"synthetic {material} {c['edge']} plate, n={n}, {load}","*NODE"]
    lines.extend(f"{v},{A*i/(2*n):.7f},{A*j/(2*n):.7f},0." for (i,j),v in nodes.items())
    lines+=["*ELEMENT,TYPE=S8R,ELSET=PLATE"]
    lines.extend(f"{i},"+",".join(str(x) for x in elem) for i,elem in enumerate(elems,1))
    lines+=["*MATERIAL,NAME=ISOTROPIC","*ELASTIC",f"{c['E']},{c['nu']}","*SHELL SECTION,ELSET=PLATE,MATERIAL=ISOTROPIC",str(c["t"])]
    edge=[v for (i,j),v in nodes.items() if i in (0,2*n) or j in (0,2*n)]
    lines+=["*NSET,NSET=EDGE"]+[",".join(map(str,edge[k:k+12])) for k in range(0,len(edge),12)]
    all_nodes=list(nodes.values())
    lines+=["*NSET,NSET=NALL"]+[",".join(map(str,all_nodes[k:k+12])) for k in range(0,len(all_nodes),12)]
    lines+=["*NSET,NSET=CENTER",str(nodes[(n,n)]),"*BOUNDARY"]
    if c["edge"]=="clamped":lines+=["EDGE,1,6,0."]
    else:
        lines+=["EDGE,3,3,0.",f"{nodes[(0,0)]},1,2,0.",f"{nodes[(2*n,0)]},2,2,0."]
    lines+=["*STEP,NLGEOM","*STATIC","0.05,1.,0.00001,0.1","*DLOAD",f"PLATE,P,{c['q_'+load]}","*NODE FILE,OUTPUT=3D","U,RF","*NODE PRINT,NSET=CENTER","U","*NODE PRINT,NSET=EDGE","RF","*NODE PRINT,NSET=NALL","U,RF","*END STEP"]
    (out/"panel.inp").write_text("\n".join(lines)+"\n",encoding="utf-8")
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--material",choices=CONFIG,required=True)
    parser.add_argument("--n",type=int,required=True)
    parser.add_argument("--load",choices=["small","large"],required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    build(a.material,a.n,a.load,a.output)
