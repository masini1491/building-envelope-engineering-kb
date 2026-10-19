"""Source-pinned synthetic shell DOF5 moment conjugacy experiment.

No material, shell, MPC or contact stiffness mutation. Research only.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

PINS={8:'e0360eed38d6708075200c499a870e38e79f120eaa88ff7427c497e7f0cef2cf',16:'90becf2d6530482a88991f7e038ee63162f52ec41e9943ddfb16be612c7ee6cf'}
ANGLES={'minus2':-2e-5,'minus1':-1e-5,'zero':0.0,'plus1':1e-5,'plus2':2e-5}
CONTACT='*CONTACT PAIR,INTERACTION=SYNTH_NORMAL,TYPE=SURFACE TO SURFACE\nRIB_BASE_UNDERSIDE,PLATE_TOP\n'
PRINT='*CONTACT PRINT,SLAVE=RIB_BASE_UNDERSIDE,MASTER=PLATE_TOP\nCF,CFN,CNUM\n'
CENTER='CENTER_RF,3,3,0.02000000\n'
ENERGY='*EL PRINT,ELSET=PLATE,TOTALS=ONLY\nELSE\n*EL PRINT,ELSET=RIB,TOTALS=ONLY\nELSE\n'

def error(code): raise ValueError('CCX221_ROT_'+code)
def replace_one(s,a,b):
    if s.count(a)!=1:error('ANCHOR')
    return s.replace(a,b,1)

def make(ref:Path,out:Path,mesh:int,contact:bool,name:str):
    raw=ref.read_bytes();digest=hashlib.sha256(raw).hexdigest()
    if digest!=PINS[mesh]:error('PROVENANCE')
    if name not in ANGLES:error('ANGLE')
    text=raw.decode('ascii')
    if text.count('PLATE_EDGE_RF,1,6,0.\n')!=1 or text.count(CENTER)!=1:error('SUPPORT_CONTEXT')
    angle=ANGLES[name]
    ns=re.search(r'(?m)^\*NSET,NSET=PLATE_EDGE_RF\s*\n([^*]+)',text)
    if ns is None:error('EDGE_NSET')
    node_ids=[int(x) for x in re.findall(r'\d+',ns.group(1))]
    coords={int(parts[0]):float(parts[1]) for row in text.split('*NODE\n',1)[1].split('*ELEMENT,',1)[0].splitlines() if len(parts:=[y.strip() for y in row.split(',')])==4}
    if len(set(node_ids))!=len(node_ids) or not node_ids or any(i not in coords for i in node_ids):error('EDGE_NODES')
    shape=[(i,(coords[i]-600.0)/600.0) for i in node_ids]
    if max(w for i,w in shape)!=1 or min(w for i,w in shape)!=-1:error('ROT_SHAPE')
    cards=''.join(f'{i},5,5,{angle*w:.10f}\n' for i,w in shape)
    text=replace_one(text,CENTER,CENTER+cards)
    if not contact:
        text=replace_one(text,CONTACT,'')
        text=replace_one(text,PRINT,'')
        if '*CONTACT PRINT' in text or '*CONTACT PAIR' in text:error('NO_CONTACT_FAILED')
    else:
        text=replace_one(text,PRINT,'*CONTACT PRINT,SLAVE=RIB_BASE_UNDERSIDE,MASTER=PLATE_TOP,TOTALS=YES\nCF,CFN,CNUM,CELS\n')
    text=replace_one(text,'*END STEP\n',ENERGY+'*END STEP\n')
    dest=out/f'n{mesh}'/('contact' if contact else 'no_contact')/name
    dest.mkdir(parents=True,exist_ok=False)
    payload=text.encode('ascii')
    (dest/'panel.inp').write_bytes(payload)
    return {'mesh':mesh,'branch':'contact' if contact else 'no_contact',
            'angle_rad':angle,'test_dof':5,'support_group':'PLATE_EDGE_RF','mode':'LINEAR_X_ANTISYMMETRIC_NOT_RIGID_ROTATION','input_sha256':hashlib.sha256(payload).hexdigest(),
            'source_sha256':digest}

def generate(input_root:Path, output_root:Path, meshes=(8,16), branches=('contact','no_contact')):
    if output_root.exists():error('OUTPUT_EXISTS')
    rows={}
    for n in meshes:
        src=input_root/f'u_s8r_rf_projection_n{n}_toward'/'panel.inp'
        for b in branches:
            for name in ANGLES:
                key=f'n{n}/{b}/{name}'
                rows[key]=make(src,output_root,n,b=='contact',name)
    (output_root/'manifest.json').write_text(json.dumps({'admission':'NOT_ADMITTED','cases':rows},sort_keys=True,indent=2)+'\n')
    return rows

if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('inputs',type=Path);pa.add_argument('out',type=Path)
    args=pa.parse_args();print('ROT5_INPUT_COUNT',len(generate(args.inputs,args.out)))
