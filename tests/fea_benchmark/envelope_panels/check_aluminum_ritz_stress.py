"""Approximate independent Kirchhoff bending reference for one low-load S8R plate.

Three symmetric Rayleigh-Ritz polynomials, satisfying all four clamped edges.
The external analytical plate approximation is NOT exact 3D shell stress,
an integration-point extreme, or an engineering design acceptance.
"""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path

# Exact polynomial integrals over [-1,1] of f0=(1-s*s)^2,
# f1=s*s*(1-s*s)^2 and their derivatives; no CCX output used.
_M=((256/315,256/3465),(256/3465,256/15015))
_G=((256/105,0.),(0.,256/1155))
_H=((128/5,128/35),(128/35,384/35))
_L=(16/15,16/105)
_BASIS=((0,0),(1,0),(0,1))
DEFLECTION_REL_TOL=0.12
BENDING_STRESS_REL_TOL=0.30
MEMBRANE_REL_TOL=0.18


def _solve3(matrix, rhs):
    a=[list(map(float,row))+[float(rhs[i])] for i,row in enumerate(matrix)]
    for pivot in range(3):
        best=max(range(pivot,3),key=lambda row:abs(a[row][pivot]))
        if abs(a[best][pivot])<=1e-16:
            raise ValueError("RITZ_STIFFNESS_SINGULAR")
        a[pivot],a[best]=a[best],a[pivot]
        for i in range(pivot+1,3):
            factor=a[i][pivot]/a[pivot][pivot]
            for j in range(pivot,4):
                a[i][j]-=factor*a[pivot][j]
    out=[0.]*3
    for i in range(2,-1,-1):
        out[i]=(a[i][3]-sum(a[i][j]*out[j] for j in range(i+1,3)))/a[i][i]
    if not all(math.isfinite(x) for x in out):
        raise ValueError("RITZ_RESULT_NONFINITE")
    return out


def reference(config):
    keys=("width_mm","height_mm","thickness_mm","youngs_modulus_mpa",
          "poisson_ratio","pressure_n_mm2")
    if not isinstance(config,dict):
        raise ValueError("RITZ_CONFIG_INVALID")
    vals=[config.get(k) for k in keys]
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in vals):
        raise ValueError("RITZ_CONFIG_NONFINITE")
    a,b,t,e,nu,q=map(float,vals)
    if min(a,b,t,e,q)<=0 or not 0<nu<0.49 or min(a,b)/t<15:
        raise ValueError("RITZ_CONFIG_OUTSIDE_PLATE_SCOPE")
    d=e*t**3/(12*(1-nu**2));jac=a*b/4
    def stiffness(left,right):
        xi,yi=left;xj,yj=right
        return d*jac*(
            16/a**4*_H[xi][xj]*_M[yi][yj]
            +16/b**4*_M[xi][xj]*_H[yi][yj]
            +16*nu/(a*a*b*b)*(
                _G[xi][xj]*_G[yi][yj]+_G[xi][xj]*_G[yi][yj])
            +32*(1-nu)/(a*a*b*b)*_G[xi][xj]*_G[yi][yj])
    # The mixed second-derivative integrals equal -G by integration by parts.
    k=[[stiffness(i,j) for j in _BASIS] for i in _BASIS]
    f=[q*jac*_L[x]*_L[y] for x,y in _BASIS]
    w=_solve3(k,f)
    # f0(0)=1, f1(0)=0, f0''(0)=-4, f1''(0)=2.
    wxx=4/a**2*(-4*w[0]+2*w[1])
    wyy=4/b**2*(-4*w[0]+2*w[2])
    sx=abs(-e*t/(2*(1-nu**2))*(wxx+nu*wyy))
    sy=abs(-e*t/(2*(1-nu**2))*(wyy+nu*wxx))
    if not all(math.isfinite(x) and x>0 for x in (w[0],sx,sy)):
        raise ValueError("RITZ_REFERENCE_NONPHYSICAL")
    return {"center_deflection_mm":w[0],"center_surface_bending_stress_mpa":{"SXX":sx,"SYY":sy},
            "reference_type":"THREE_TERM_KIRCHHOFF_CLAMPED_RITZ_APPROXIMATION"}


def compare(config, coordinates, stress, center_deflection_mm):
    if (not isinstance(coordinates,dict) or not coordinates
            or set(coordinates)!=set(stress)
            or type(center_deflection_mm) not in (float,int)
            or not math.isfinite(center_deflection_mm) or center_deflection_mm<=0):
        raise ValueError("RITZ_OBSERVATIONS_INVALID")
    ref=reference(config)
    a,b,t=config["width_mm"],config["height_mm"],config["thickness_mm"]
    tolerance=max(1e-5,1e-6*max(a,b,t))
    surfaces={"+":[], "-":[]}
    for node,xyz in coordinates.items():
        if (type(node) is not int or node<=0 or len(xyz)!=3
                or len(stress[node])!=6
                or any(type(v) not in (int,float) or not math.isfinite(v)
                       for v in (*xyz,*stress[node]))):
            raise ValueError("RITZ_FIELD_MALFORMED")
        x,y,z=xyz
        if (abs(x-a/2)<=tolerance and abs(y-b/2)<=tolerance
                and abs(abs(z)-t/2)<=tolerance):
            surfaces["+" if z>0 else "-"].append(stress[node])
    if not 1<=len(surfaces["+"])<=16 or not 1<=len(surfaces["-"])<=16:
        raise ValueError("RITZ_CENTER_SURFACE_COVERAGE_MISSING")
    def mean(side,index):
        return sum(item[index] for item in surfaces[side])/len(surfaces[side])
    diffs={}
    for comp,index in (("SXX",0),("SYY",1)):
        top,bottom=mean("+",index),mean("-",index)
        bending=abs((top-bottom)/2)
        membrane=abs((top+bottom)/2)
        expected=ref["center_surface_bending_stress_mpa"][comp]
        relative=abs(bending-expected)/expected
        if relative>BENDING_STRESS_REL_TOL:
            raise ValueError("RITZ_CENTER_BENDING_STRESS_DISAGREEMENT:"+comp)
        if membrane/expected>MEMBRANE_REL_TOL:
            raise ValueError("RITZ_MEMBRANE_COMPONENT_TOO_LARGE:"+comp)
        diffs[comp]={"observed_bending_mpa":bending,"reference_bending_mpa":expected,
                     "relative_difference":relative,"membrane_fraction":membrane/expected}
    d_error=abs(center_deflection_mm-ref["center_deflection_mm"])/ref["center_deflection_mm"]
    if d_error>DEFLECTION_REL_TOL:
        raise ValueError("RITZ_CENTER_DEFLECTION_DISAGREEMENT")
    return {"verification_scope":"LOW_LOAD_ORIGINAL_S8R_CENTER_U_AND_EXPANDED_C3D20_CENTER_SURFACE_STRESS",
            "reference_type":ref["reference_type"],
            "reference_is_exact_3d_field":False,
            "center_deflection_relative_difference":d_error,
            "center_bending_stress":diffs,
            "expanded_center_nodes_per_surface":{s:len(v) for s,v in surfaces.items()},
            "screening_tolerances":{"deflection":DEFLECTION_REL_TOL,
                                    "bending_stress":BENDING_STRESS_REL_TOL,
                                    "membrane":MEMBRANE_REL_TOL},
            "stress_source":"CCX_FRD_EXTRAPOLATED_AVERAGED_EXPANDED_NODES",
            "integration_point_stress_extreme":"NOT_OBSERVED",
            "support_rotation_reaction":"NOT_OBSERVED",
            "engineering_acceptance":"NOT_ADMITTED",
            "aluminum_design_manual_capacity":"NOT_COMPUTED"}


def check_fixture(root:Path):
    from check_aluminum_ritz import expected_input,center_z
    from check_aluminum_elastic_scaling import _load_case
    from check_expanded_frd import read_expanded_frd
    config=expected_input("thicker_square",16)
    observed=_load_case(root,config)
    center=center_z(root/"run"/"panel.dat")
    return compare(config,observed["expanded_xyz"],observed["STRESS"],center)


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("USAGE: check_aluminum_ritz_stress.py SCALING_BASELINE_DIR")
    print(json.dumps(check_fixture(Path(sys.argv[1])),sort_keys=True,allow_nan=False))
    print("THREE_TERM_APPROXIMATE_PLATE_FIELD_SCREENING_PASS; NO DESIGN ADMISSION")
