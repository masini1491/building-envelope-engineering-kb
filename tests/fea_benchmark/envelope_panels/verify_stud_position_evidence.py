"""Pinned, fixed-count C3D20R interior-station movement evidence; NOT DESIGN.

Baseline counts/spring k/geometry unchanged within each comparison.
All force checks use k*ΔU and independent clean rib-end support RF3;
not contact CPRESS or measured stud/weld capacity.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile

from stud_position_trial import make as moved_make, LAYOUTS
from stud_pitch_trial import make as five_make
from stud_solid_trial import deck as four_deck, CASES
from verify_stud_solid_trial import field, sets
from verify_c3d20r_u_contact import status
from verify_pressure_contact_trial import nominal_pressure_equivalents
from check_u_rib_contact_observations import rf

PINS = {
    'moved':'445414375571a6d74aaf3e90859868b4ad3c6f57b5e1e51d21edb4750e858d02',
    'four':'03cda477016e945c5f76a5b88a0548a08027c62ec777e4d5e7afec4c6b0e7f7a',
    'five':'c249bb93622b66cd25aab87fa503c3b179ebde1ead2e632c47dd2f1ef0149279',
}
LIMIT_N=0.002


def stop(code):
    raise ValueError('STUD_POSITION_EVIDENCE_'+code)


def open_pinned(filename,label):
    file=Path(filename)
    if label not in PINS or file.is_symlink() or not file.is_file() or not 0<file.stat().st_size<32_000_000:
        stop('PINNED_SOURCE')
    with file.open('rb') as f:
        if hashlib.file_digest(f,'sha256').hexdigest()!=PINS[label]:
            stop('SHA256')
    return ZipFile(file)


def member(zipfile,name,limit=32_000_000):
    try:
        meta=zipfile.getinfo(name)
    except KeyError:
        stop('MISSING_EVIDENCE')
    if not 0<meta.file_size<limit:
        stop('EVIDENCE_SIZE')
    return zipfile.read(name)


def verify_result(inp,dat,sta,expected,pairs,n,k):
    if inp!=expected.encode('utf-8'):
        stop('INPUT_PROVENANCE')
    status(sta.decode('utf-8',errors='replace'))
    groups=sets(expected)
    if len(groups['STUD_PLATE'])!=len(pairs) or len(groups['STUD_RIB'])!=len(pairs):
        stop('STATION_COUNT')
    if tuple(zip(groups['STUD_PLATE'],groups['STUD_RIB']))!=pairs:
        stop('STATION_PAIR_IDENTITY')
    text=dat.decode('utf-8',errors='replace')
    plate=field(text,'STUD_PLATE',groups['STUD_PLATE'])
    rib=field(text,'STUD_RIB',groups['STUD_RIB'])
    center=field(text,'CENTER_RF',groups['CENTER_RF'])
    if set(plate)!=set(groups['STUD_PLATE']) or set(rib)!=set(groups['STUD_RIB']) or set(center)!=set(groups['CENTER_RF']):
        stop('NODE_COVERAGE')
    forces=[k*(plate[a][2]-rib[b][2]) for a,b in pairs]
    if len(forces)!=len(pairs) or min(forces)<=0 or not all(map(math.isfinite,forces)):
        stop('STATION_FORCE')
    if any(abs(forces[i]-forces[-1-i])>LIMIT_N for i in range(len(forces)//2)):
        stop('STATION_SYMMETRY')
    rib_rf=rf(text,'RIB_END_RF',expected_nodes=groups['RIB_END_RF'])['sum_rf3_n']
    plate_rf=rf(text,'PLATE_EDGE_RF',expected_nodes=groups['PLATE_EDGE_RF'])['sum_rf3_n']
    transfer=math.fsum(forces)
    reaction_residual=math.fsum((transfer,rib_rf))
    global_residual=math.fsum((rib_rf,plate_rf,-nominal_pressure_equivalents(n)['edge_pressure_n'],36.))
    if abs(reaction_residual)>LIMIT_N or abs(global_residual)>LIMIT_N:
        stop('REACTION_BALANCE')
    center_u3=math.fsum(v[2] for v in center.values())/len(center)
    if not math.isfinite(center_u3) or center_u3<=0:stop('CENTER_U3')
    return {'center_u3_mm':center_u3,'station_forces_n':forces,
            'sum_station_force_n':transfer,'peak_station_force_n':max(forces),
            'rib_end_rf3_n':rib_rf,'rib_reaction_residual_n':reaction_residual,
            'nominal_global_z_residual_n':global_residual}


def verify(moved_zip,four_zip,five_zip):
    with open_pinned(moved_zip,'moved') as znew,open_pinned(four_zip,'four') as zfour,open_pinned(five_zip,'five') as zfive:
        records=[];observations=[]
        for n in (8,16):
            for kcase in ('soft','stiff'):
                k=CASES[kcase]
                for layout,(parent,positions) in LAYOUTS.items():
                    changed,pairs_new=moved_make(n,layout,kcase)
                    if parent=='four_300':
                        source_z=zfour
                        old_name=f'stud_{n}_{kcase}/panel.'
                        old_deck=four_deck(n,kcase)
                        # Known four-link source retains canonical station order.
                        _,pairs_old=moved_make(n,layout,kcase)
                        from stud_solid_trial import add_studs
                        from pressure_contact_trial import deck as pressure_deck
                        old_deck,pairs_old=add_studs(pressure_deck(n,'unlinked'),n,kcase)
                    elif parent=='five_225':
                        source_z=zfive
                        old_name=f'pitch_{n}_five_225_{kcase}/panel.'
                        old_deck,pairs_old=five_make(n,parent,kcase)
                    else:stop('PROFILE')
                    new_name=f'position_{n}_{layout}_{kcase}/panel.'
                    before=verify_result(member(source_z,old_name+'inp'),member(source_z,old_name+'dat'),
                        member(source_z,old_name+'sta'),old_deck,pairs_old,n,k)
                    after=verify_result(member(znew,new_name+'inp'),member(znew,new_name+'dat'),
                        member(znew,new_name+'sta'),changed,pairs_new,n,k)
                    for z,key in ((znew,new_name),(source_z,old_name)):
                        if z.getinfo(key+'frd').file_size<=0:stop('EMPTY_FRD')
                    if len(pairs_old)!=len(pairs_new) or positions[0]!=150 or positions[-1]!=1050:
                        stop('CONTROL_VIOLATION')
                    diff=after['center_u3_mm']-before['center_u3_mm']
                    records.append({'mesh':n,'case':kcase,'k_per_station_n_per_mm':k,
                        'layout':layout,'baseline_profile':parent,'moved_positions_mm':positions,
                        'station_count':len(positions),'baseline':before,'moved':after,
                        'center_u3_change_mm':diff,
                        'center_u3_relative_change_percent':100*diff/before['center_u3_mm'],
                        'causal_scope':'CONTROLLED_INTERIOR_LOCATION_ONLY_SYNTHETIC'})
        for layout in LAYOUTS:
            for case in ('soft','stiff'):
                same=[r for r in records if r['layout']==layout and r['case']==case]
                if len(same)!=2:stop('MESH_COVERAGE')
                # Direction is consistent in the two available grids.
                if same[0]['center_u3_change_mm']*same[1]['center_u3_change_mm']<=0:
                    stop('MESH_DIRECTION_MISMATCH')
                observations.append({'layout':layout,'case':case,
                    'same_change_direction_n8_n16':True,
                    'mesh_magnitude_agreement':'NOT_ESTABLISHED'})
        return {'scope':'SYNTHETIC_C3D20R_FIXED_COUNT_LOCATION_COMPARATOR_NOT_DESIGN',
            'sha256':PINS,'cases':records,'cross_mesh_observations':observations,
            'max_moved_rib_balance_residual_n':max(abs(x['moved']['rib_reaction_residual_n']) for x in records),
            'max_moved_global_balance_residual_n':max(abs(x['moved']['nominal_global_z_residual_n']) for x in records),
            'same_stud_count_and_k':True,'synthetic_connector_model':'BILATERAL_Z_SPRING_ONLY',
            'true_stud_and_weld_stiffness_capacity':'NOT_ADMITTED',
            'engineering_acceptance':'NOT_ADMITTED'}


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('new_zip');p.add_argument('four_zip');p.add_argument('five_zip')
    a=p.parse_args()
    print(json.dumps(verify(a.new_zip,a.four_zip,a.five_zip),indent=2,sort_keys=True,allow_nan=False))
