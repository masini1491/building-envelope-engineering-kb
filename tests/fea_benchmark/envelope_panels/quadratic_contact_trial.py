"""Bounded synthetic C3D8 -> C3D20R contact trial; no design admission."""
from pathlib import Path
import sys
from probe_c3d8_u_contact import deck as linear_deck, model, MESHES, CASES, CLEARANCE_CASE

EDGES=((0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
       (0,4),(1,5),(2,6),(3,7))
SETS=('PLATE_EDGE_RF','RIB_END_RF','CENTER_RF')

def deck(n, case):
    if type(n) is not int or n not in MESHES or case not in CASES+(CLEARANCE_CASE,):
        raise ValueError('C3D20R_SCOPE')
    original=linear_deck(n,case)
    nodes,elements,plate,rib,ps,rs,center=model(n,case)
    if set(nodes)!=set(range(1,len(nodes)+1)) or set(elements)!=set(range(1,len(elements)+1)):
        raise ValueError('C3D20R_SOURCE_TOPOLOGY')
    mids={}; converted={}
    for eid,(_,corners) in elements.items():
        if len(corners)!=8 or len(set(corners))!=8 or not set(corners)<=set(nodes):
            raise ValueError('C3D20R_SOURCE_CONNECTIVITY')
        extra=[]
        for a,b in EDGES:
            edge=tuple(sorted((corners[a],corners[b])))
            if edge not in mids:
                xyz=tuple((nodes[edge[0]][k]+nodes[edge[1]][k])/2 for k in range(3))
                mids[edge]=(len(nodes)+len(mids)+1,xyz)
            extra.append(mids[edge][0])
        converted[eid]=(*corners,*extra)
    source_sets=dict(zip(SETS,(ps,rs,center)))
    result=[];lines=original.splitlines();i=0
    while i<len(lines):
        line=lines[i];header=line.strip()
        if header=='*NODE':
            result.append(line);i+=1
            while i<len(lines) and not lines[i].startswith('*'):
                result.append(lines[i]);i+=1
            result.extend(f'{nid},{x:.8f},{y:.8f},{z:.8f}' for nid,(x,y,z) in mids.values())
            continue
        if header.startswith('*ELEMENT,TYPE=C3D8,ELSET='):
            result.append(line.replace('TYPE=C3D8','TYPE=C3D20R'));i+=1
            while i<len(lines) and not lines[i].startswith('*'):
                if lines[i].strip():
                    eid=int(lines[i].split(',',1)[0]);v=(eid,*converted[eid])
                    result.append(','.join(map(str,v[:16]))+',')
                    result.append(','.join(map(str,v[16:])))
                i+=1
            continue
        if header.startswith('*NSET,NSET=') and header.split('=',1)[1] in source_sets:
            group=header.split('=',1)[1];old=source_sets[group];oldset=set(old)
            extra=[nid for (a,b),(nid,_) in mids.items() if a in oldset and b in oldset]
            values=tuple(old)+tuple(extra)
            result.append(line)
            result.extend(','.join(map(str,values[j:j+12])) for j in range(0,len(values),12))
            i+=1
            while i<len(lines) and not lines[i].startswith('*'):i+=1
            continue
        result.append(line.replace('Synthetic explicit C3D8 open-U','Synthetic explicit C3D20R open-U'));i+=1
    content='\n'.join(result)+'\n'
    if (content.count('*ELEMENT,TYPE=C3D20R')!=2 or
        content.count('*CONTACT PAIR')!=int(case!='unlinked') or
        content.count('*SURFACE,')!=original.count('*SURFACE,')):
        raise ValueError('C3D20R_CONTRACT')
    return content

if __name__=='__main__':
    if len(sys.argv)!=5 or sys.argv[1]!='--generate':
        raise SystemExit('usage: --generate EMPTY_DIR MESH CASE')
    folder=Path(sys.argv[2])
    if folder.exists() or folder.is_symlink():raise ValueError('C3D20R_NOT_FRESH')
    text=deck(int(sys.argv[3]),sys.argv[4])
    folder.mkdir(parents=True)
    (folder/'panel.inp').write_text(text,encoding='utf-8')
