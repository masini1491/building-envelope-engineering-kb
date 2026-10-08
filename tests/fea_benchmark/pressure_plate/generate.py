"""Generate synthetic S8R square thin-plate uniform pressure benchmarks.

N-mm units. All plate boundaries w=0, two in-plane rigid-mode anchors.
Small-deflection oracle: w_c = 0.00406 * q * a**4 / D.
This is NOT ASTM E1300 or a validated glass/metal panel capacity model.
"""
from __future__ import annotations
import argparse
from pathlib import Path

A=100.0
THICKNESS=1.0
E=210000.0
POISSON=0.3
PRESSURES={"small":0.0001,"large":0.5}
def build(n: int, case: str, directory: Path) -> None:
    if n not in (4,8,16) or case not in PRESSURES:
        raise ValueError("invalid benchmark mesh or load")
    directory.mkdir(parents=True,exist_ok=True)
    nodes={}
    def node(i,j):
        key=(i,j)
        if key not in nodes:
            nodes[key]=len(nodes)+1
        return nodes[key]
    elems=[]
    for j in range(n):
        for i in range(n):
            p=[(2*i,2*j),(2*i+2,2*j),(2*i+2,2*j+2),(2*i,2*j+2),
               (2*i+1,2*j),(2*i+2,2*j+1),(2*i+1,2*j+2),(2*i,2*j+1)]
            elems.append([node(*v) for v in p])
    lines=["*HEADING",f"Synthetic simply supported uniform pressure square S8R n={n} case={case}","*NODE"]
    for (i,j),id in nodes.items():
        lines.append(f"{id},{A*i/(2*n):.8f},{A*j/(2*n):.8f},0.")
    lines.append("*ELEMENT,TYPE=S8R,ELSET=PLATE")
    for k,e in enumerate(elems,1): lines.append(f"{k},"+",".join(map(str,e)))
    lines.extend(["*MATERIAL,NAME=ELASTIC","*ELASTIC",f"{E},{POISSON}",
                  "*SHELL SECTION,ELSET=PLATE,MATERIAL=ELASTIC",f"{THICKNESS}"])
    boundary=[id for (i,j),id in nodes.items() if i in (0,2*n) or j in (0,2*n)]
    lines+=["*NSET,NSET=EDGE"]+[",".join(map(str,boundary[k:k+12])) for k in range(0,len(boundary),12)]
    center=nodes.get((n,n))
    if center is None:
        raise ValueError("no center node")
    lines+=["*NSET,NSET=CENTER",str(center),"*BOUNDARY","EDGE,3,3,0.",
            f"{nodes[(0,0)]},1,2,0.",f"{nodes[(2*n,0)]},2,2,0.",
            "*STEP,NLGEOM","*STATIC","0.05,1.0,0.00001,0.1",
            "*DLOAD",f"PLATE,P,{PRESSURES[case]}",
            "*NODE PRINT,NSET=CENTER","U",
            "*NODE PRINT,NSET=EDGE","RF","*END STEP"]
    (directory/"plate.inp").write_text("\n".join(lines)+"\n",encoding="utf-8")
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--n",type=int,required=True)
    p.add_argument("--case",choices=tuple(PRESSURES),required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    build(a.n,a.case,a.output)
