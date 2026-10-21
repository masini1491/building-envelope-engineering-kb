"""Synthetic C3D20R CSTR sampling-bias STOP guard (not force reconstruction).

Distinct meanings: element-face geometric support area, printed contact area,
true integrated contact force. CSTR record multiplicity/weights are NOT available.
"""
import argparse
import json
import math
import statistics
from collections import defaultdict

from verify_c3d20r_contact_ip import PINS, open_pinned, read_member, parse_input, parse_cstr_final, dat_summary, zone

BASE_FACE_WIDTHS = {-23.5: 3.0, 0.0: 44.0, 23.5: 3.0}


def stop(reason):
    raise ValueError('C3D20R_IP_SAMPLING_' + reason)


def geometric_face_proxy(centers, stresses, n, true_contact_fz, printed_contact_area):
    """Counterexample ONLY: treats each entire active slave S1 face as loaded.

    Flat synthetic base geometry x spacing 1200/(2*n), y strip widths 3/44/3.
    CSTR records have no coordinates or weights; equal-record averaging within
    a whole active face is *not* numerical contact integration.
    """
    if type(n) is not int or n not in (16, 24):stop('SCOPE')
    if not math.isfinite(true_contact_fz) or true_contact_fz<=0:stop('SOLVER_FORCE')
    if not math.isfinite(printed_contact_area) or printed_contact_area<=0:stop('SOLVER_AREA')
    if not stresses or set(stresses)-set(centers):stop('INPUT_MEMBERSHIP')
    dx=1200.0/(2*n)
    all_cells=defaultdict(lambda: {'face_area_mm2':0.,'surface_area_pressure_proxy_n':0.,'count':0,'faces':0,'pressure_sum':0.})
    for eid, samples in stresses.items():
        if not samples or not all(isinstance(x,(int,float)) and math.isfinite(x) and x>=0 for x in samples):
            stop('CSTR_VALUE')
        x,y=centers[eid]
        if not isinstance(x,(int,float)) or not math.isfinite(x) or not 0<x<1200:stop('CENTROID_X')
        # Entire face midpoints are exact regular synthetic-grid coordinates.
        idx=x/dx-0.5
        if abs(idx-round(idx))>1e-7 or not 0<=round(idx)<2*n:stop('X_NOT_MESH_MIDPOINT')
        if y not in BASE_FACE_WIDTHS:stop('Y_NOT_SYNTHETIC_BASE')
        area=dx*BASE_FACE_WIDTHS[y]
        b=all_cells[zone(x)]
        b['face_area_mm2']+=area
        b['surface_area_pressure_proxy_n']+=area*statistics.mean(samples)
        b['count']+=len(samples);b['faces']+=1
        b['pressure_sum']+=sum(samples)
    result={}
    for name in ('end_0_150_mm','transition_150_300_mm','interior_300_600_mm'):
        b=all_cells[name]
        if not b['faces'] or not b['count']:stop('MISSING_REGION')
        result[name]={
            'active_face_count':b['faces'],
            'cstr_record_count':b['count'],
            'whole_face_geometric_area_mm2':b['face_area_mm2'],
            'unweighted_record_mean_n_mm2':b['pressure_sum']/b['count'],
            'whole_face_area_weighted_sample_mean_n_mm2':b['surface_area_pressure_proxy_n']/b['face_area_mm2'],
        }
    proxy=sum(b['surface_area_pressure_proxy_n'] for b in all_cells.values())
    face_area=sum(b['face_area_mm2'] for b in all_cells.values())
    return {'n':n,'all_active_faces_geometric_area_mm2':face_area,
            'solver_printed_contact_area_mm2':printed_contact_area,
            'geometric_face_area_to_printed_contact_area_ratio':face_area/printed_contact_area,
            'whole_face_pressure_proxy_n_INVALID_AS_CONTACT_FORCE':proxy,
            'solver_integrated_contact_fz_n':true_contact_fz,
            'invalid_proxy_to_solver_force_ratio':proxy/true_contact_fz,
            'zones':result,
            'proxy_is_contact_force':False,
            'element_face_contact_fraction':'NOT_KNOWN',
            'CSTR_point_coordinates_weights':'NOT_AVAILABLE'}


def replay(ip_zip):
    with open_pinned(ip_zip,'ip') as z:
        meshes={}
        for n in (16,24):
            prefix=f'ip{n}_toward/panel.'
            source=read_member(z,prefix+'inp').decode()
            dat=read_member(z,prefix+'dat').decode(errors='replace')
            centers=parse_input(source)
            groups,declared=parse_cstr_final(dat,centers)
            fz,area=dat_summary(dat)
            result=geometric_face_proxy(centers,groups,n,fz,area)
            if sum(x['cstr_record_count'] for x in result['zones'].values()) != declared:stop('ROWCOUNT')
            meshes[str(n)]=result
        return {'scope':'NEGATIVE_EVIDENCE_INTEGRATION_NOT_ADMITTED',
                'source_sha256':PINS['ip'],
                'regions':meshes,
                'contact_force_reconstruction':'REJECTED',
                'engineering_admission':'NOT_ADMITTED'}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('contact_ip_zip');p=ap.parse_args()
    print(json.dumps(replay(p.contact_ip_zip),indent=2,sort_keys=True,allow_nan=False))
