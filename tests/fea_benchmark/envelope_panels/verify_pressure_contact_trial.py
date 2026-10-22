"""Bounded nominal pressure/force and clearance comparator; not design acceptance."""
import json, math, re, sys
from pathlib import Path
from pressure_contact_trial import deck, APPLIED_TOTAL_Z_N
from verify_c3d20r_u_contact import parse_input, status, deformed_gap
from check_u_rib_contact_observations import rf, contact_print


def fail(code): raise ValueError('C3D20R_PRESSURE_'+code)


def nominal_pressure_equivalents(n):
    """Fixed geometry only; exact deck provenance constrains n to 8/16.

    A C3D20R S1 quadratic face integrates -p*A/12 at each corner and
    +p*A/3 at each midside. Summing over all four fixed perimeter edges
    produces p*A*(2*n+1)/3, while the free center corner is -p*A/3.
    """
    if type(n) is not int or n not in (8,16,24):fail('PRESSURE_SCOPE')
    cell_force=APPLIED_TOTAL_Z_N/(n*n)
    return {'edge_pressure_n':cell_force*(2*n+1)/3,
            'center_pressure_n':-cell_force/3}


def verify(root, include_n24=False):
    report=[]
    for n in ((8,16,24) if include_n24 else (8,16)):
        for case in (('toward','unlinked') if n==24 else ('toward','unlinked','clearance')):
            folder=Path(root)/f'p{n}_{case}'
            paths={e:folder/f'panel.{e}' for e in ('inp','dat','sta','frd')}
            if any(not f.is_file() or f.is_symlink() for f in paths.values()):fail('MISSING_FILE')
            inp=paths['inp'].read_text()
            if inp!=deck(n,case):fail('DECK_MISMATCH')
            groups,nodes,bodies=parse_input(inp)
            increments=status(paths['sta'].read_text())
            dat=paths['dat'].read_text(errors='replace')
            totals={key:rf(dat,key,expected_nodes=members)['sum_rf3_n'] for key,members in groups.items()}
            # RF includes loads AND reactions. Subtract known uniform P1 nodal
            # loads on fixed plate edges; CENTER_RF is FREE, not a support.
            # For a flat C3D20R quadratic face: corner -A/12, midside +A/3.
            equiv=nominal_pressure_equivalents(n)
            raw_print_sum=math.fsum(totals.values())
            support=math.fsum((totals['PLATE_EDGE_RF'],totals['RIB_END_RF'],
                               -equiv['edge_pressure_n']))
            nominal_residual=support+APPLIED_TOTAL_Z_N
            # 2.5% screen is retained, with an additional 0.002 N strict gate.
            # Exact NLGEOM deformed-face pressure integration is not claimed.
            if abs(nominal_residual)>min(0.002,0.025*APPLIED_TOTAL_Z_N):
                fail('CORRECTED_FORCE_SCREEN')
            if abs(totals['CENTER_RF']-equiv['center_pressure_n'])>0.002:
                fail('CENTER_CONSISTENT_LOAD')
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
            report.append({'mesh':n,'case':case,'completed_increments':increments,'raw_observed_rf3_n':totals,
                           'raw_printed_rf3_sum_n':raw_print_sum,
                           'fixed_edge_equivalent_pressure_n':equiv['edge_pressure_n'],
                           'free_center_equivalent_pressure_n':equiv['center_pressure_n'],
                           'reconstructed_support_reaction_z_n':support,
                           'nominal_force_n':APPLIED_TOTAL_Z_N,'nominal_z_residual_n':nominal_residual,
                           'contact':surface,'deformed_node_envelope_gap_mm':gap})
    return {'scope':'SYNTHETIC_C3D20R_QUADRATIC_FACE_PRESSURE_SCREEN_ONLY',
            'cases':report,'load_direction_and_follower_pressure_integral':'NOT_INDEPENDENTLY_ESTABLISHED',
            'mesh_contact_distribution_convergence':'NOT_ESTABLISHED',
            'engineering_acceptance':'NOT_ADMITTED'}

if __name__=='__main__':
    if len(sys.argv) not in (2,3) or (len(sys.argv)==3 and sys.argv[2]!='--include-n24'):
        raise SystemExit('usage: ROOT [--include-n24]')
    print(json.dumps(verify(sys.argv[1],include_n24=len(sys.argv)==3),sort_keys=True,indent=2,allow_nan=False))
