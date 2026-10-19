"""Fail-closed input-card load scope gate for six frozen DOF5 cases.

This is input-only provenance, not a dynamic solver external-force ledger.
"""
from __future__ import annotations
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
SOURCE_SHA = 'd9b36c420feca6a5f8cd50dc8cb07dbba6c2ebbbf0224abb4df57fbfd2291a8b'
MANIFEST_SHA = 'd4af3bb7edbd06b5acba0343f07a8932281cd3221d35036daea31bdf6025fd9b'
CASES = tuple(f'n{n}/no_contact/{trial}' for n in (8,16) for trial in ('minus1','zero','plus1'))

ALLOWED = frozenset({'STEP', 'END STEP', 'BOUNDARY', 'STATIC', 'NODE', 'ELEMENT',
    'NSET', 'ELSET', 'SHELL SECTION', 'MATERIAL', 'ELASTIC', 'SOLID SECTION',
    'SURFACE', 'CONTACT PAIR', 'SURFACE INTERACTION', 'SURFACE BEHAVIOR',
    'HEADING', 'OUTPUT', 'NODE PRINT', 'EL PRINT', 'NODE FILE', 'EL FILE',
    'CONTROLS', 'AMPLITUDE', 'DENSITY', 'INITIAL CONDITIONS', 'RESTART',
    'TIME POINTS', 'CONTACT OUTPUT', 'NODE OUTPUT', 'ELEMENT OUTPUT'})
FORBIDDEN = frozenset({'CLOAD','DLOAD','DSLOAD','DFLUX','TEMPERATURE','FILM',
    'RADIATE','CFLUX','DISTRIBUTING COUPLING','MPC','EQUATION','DYNAMIC',
    'BUCKLE','FREQUENCY','MODAL DYNAMIC','BASE MOTION','GRAVITY'})

def reject(code):
    raise ValueError('CCX221_LOAD_SCOPE_' + code)

def classify(deck: str) -> dict:
    if not isinstance(deck, str) or not deck.strip():
        reject('EMPTY')
    cards=[]
    for line in deck.splitlines():
        s=line.strip()
        if not s or s.startswith('**'):
            continue
        if s.startswith('*'):
            key=s[1:].split(',',1)[0].strip().upper()
            if not key or key in FORBIDDEN:
                reject('FORBIDDEN_' + re.sub(r'\W+', '_',key))
            if key not in ALLOWED:
                reject('UNRECOGNIZED_' + re.sub(r'\W+', '_',key))
            if re.search(r'(?i)(^|,)\s*(OP|AMPLITUDE|LOAD CASE|USER)\s*=',s):
                reject('UNSUPPORTED_OPTION')
            cards.append(key)
    if cards.count('STEP') != 1 or cards.count('END STEP') != 1:
        reject('STEP_COUNT')
    if cards.count('BOUNDARY') != 2:
        reject('BOUNDARY_COUNT')
    if cards.count('STATIC') != 1:
        reject('STATIC_COUNT')
    return {'step_cards':1,'boundary_cards':2,
            'explicit_load_cards':0,'scope':'INPUT_CARDS_ONLY',
            'external_force_vector':'NOT_OBSERVED',
            'spc_dual':'NOT_ESTABLISHED'}

def audit_zip(source: Path):
    if hashlib.sha256(source.read_bytes()).hexdigest()!=SOURCE_SHA:
        reject('SOURCE_PIN')
    cases={}
    with zipfile.ZipFile(source) as z:
        m=z.read('manifest.json')
        if hashlib.sha256(m).hexdigest()!=MANIFEST_SHA:
            reject('MANIFEST_PIN')
        manifest=json.loads(m)['cases']
        for key in CASES:
            raw=z.read(key+'/panel.inp')
            if hashlib.sha256(raw).hexdigest()!=manifest[key]['input_sha256']:
                reject('INPUT_PIN')
            cases[key]=classify(raw.decode('ascii'))
    return {'status':'INPUT_ONLY_LOAD_SCOPE_NOT_PHYSICAL_DUAL', 'cases':cases,
            'independent_external_spc_dual':'NOT_ESTABLISHED',
            'engineering_acceptance':'NOT_ADMITTED'}

if __name__=='__main__':
    if len(sys.argv)!=2:
        raise SystemExit('usage: verify_ccx221_rot5_load_scope.py source.zip')
    print(json.dumps(audit_zip(Path(sys.argv[1])),indent=2,sort_keys=True))
