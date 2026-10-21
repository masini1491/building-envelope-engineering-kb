"""Bounded nominal pressure/force and clearance comparator; not design acceptance."""
import json, math, re, sys
from pathlib import Path
from pressure_contact_trial import deck, APPLIED_TOTAL_Z_N
from verify_c3d20r_u_contact import parse_input, status, deformed_gap
from check_u_rib_contact_observations import rf, contact_print


def fail(code): raise ValueError('C3D20R_PRESSURE_'+code)


def verify(root):
    report=[]
    for n in (8,16):
        for case in ('toward','unlinked','clearance'):
            folder=Path(root)/f'p{n}_{case}'
            paths={e:folder/f'panel.{e}' for e in ('inp','dat','sta','frd')}
            if any(not f.is_file() or f.is_symlink() for f in paths.values()):fail('MISSING_FILE')
            inp=paths['inp'].read_text()
            if inp!=deck(n,case):fail('DECK_MISMATCH')
            groups,nodes,bodies=parse_input(inp)
            increments=status(paths['sta'].read_text())
            dat=paths['dat'].read_text(errors='replace')
            totals={key:rf(dat,key,expected_nodes=members)['sum_rf3_n'] for key,members in groups.items()}
            support=math.fsum(totals.values())
            nominal_residual=support+APPLIED_TOTAL_Z_N
            # P1 is follower pressure under NLGEOM. 2.5% is a SCREEN only, not an exact external-force oracle.
            if abs(nominal_residual)>0.025*APPLIED_TOTAL_Z_N:fail('NOMINAL_FORCE_SCREEN')
            if abs(totals['CENTER_RF'])>0.002:fail('FREE_CENTER_NOT_FREE')
            if case=='unlinked':
                if 'statistics for slave set' in dat:fail('FALSE_CONTACT')
                if abs(totals['RIB_END_RF'])>0.002:fail('UNLINKED_TRANSFER')
                surface=None;gap=None
            else:
                surface=contact_print(dat)
                if case=='clearance':
                    if surface['contact_area_mm2']!=0 or any(abs(v)>0 for v in surface['slave_total_force_n']):
                        fail('CLEARANCE_CONTACT_ACTIVE')
                    if abs(totals['RIB_END_RF'])>0.002:fail('CLEARANCE_RIB_TRANSFER')
                    gap=deformed_gap(paths['frd'].read_text(errors='replace'),nodes,bodies)
                else:
                    gap=None
                    if surface['contact_area_mm2']<=0 or surface['slave_total_force_n'][2]<=0:
                        fail('NO_TOWARD_CONTACT')
                    if abs(totals['RIB_END_RF']+surface['slave_total_force_n'][2])>0.002:
                        fail('CONTACT_RIB_IMBALANCE')
            report.append({'mesh':n,'case':case,'completed_increments':increments,'support_rf3_n':totals,
                           'nominal_force_n':APPLIED_TOTAL_Z_N,'nominal_z_residual_n':nominal_residual,
                           'contact':surface,'deformed_node_envelope_gap_mm':gap})
    return {'scope':'SYNTHETIC_FOLLOWER_PRESSURE_2P5_PERCENT_SCREEN_ONLY',
            'cases':report,'load_direction_and_follower_pressure_integral':'NOT_INDEPENDENTLY_ESTABLISHED',
            'mesh_contact_distribution_convergence':'NOT_ESTABLISHED',
            'engineering_acceptance':'NOT_ADMITTED'}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: ROOT')
    print(json.dumps(verify(sys.argv[1]),sort_keys=True,indent=2,allow_nan=False))
