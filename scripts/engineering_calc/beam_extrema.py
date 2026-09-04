"""Within-element extrema for constant-UDL Euler-Bernoulli beam results.

This is a deterministic post-processor for ``beam.solve_beam``. It does not select the
structural model or infer supports, releases, stiffness, loads, or design criteria.
"""
from dataclasses import dataclass
from math import isfinite
from .beam import BeamElement, BeamResult

@dataclass(frozen=True)
class ElementExtrema:
    element_index: int
    max_abs_shear: float
    max_abs_shear_x: float
    max_abs_moment: float
    max_abs_moment_x: float
    max_abs_deflection: float
    max_abs_deflection_x: float

@dataclass(frozen=True)
class BeamExtrema:
    max_abs_shear: float
    max_abs_shear_element: int
    max_abs_shear_x: float
    max_abs_moment: float
    max_abs_moment_element: int
    max_abs_moment_x: float
    max_abs_deflection: float
    max_abs_deflection_element: int
    max_abs_deflection_x: float

def _quad_roots(a,b,c):
    scale=max(abs(a),abs(b),abs(c),1.0); tol=scale*1e-14
    if abs(a)<=tol:
        return [] if abs(b)<=tol else [-c/b]
    d=b*b-4*a*c
    if d < -tol: return []
    d=max(d,0.0)**0.5
    return [(-b-d)/(2*a),(-b+d)/(2*a)]

def _bisect(fn,a,b):
    fa=fn(a); fb=fn(b)
    for _ in range(80):
        m=(a+b)/2; fm=fn(m)
        if abs(fm)<=1e-12 or abs(b-a)<=1e-12*max(1.0,abs(m)): return m
        if fa*fm<=0: b=m; fb=fm
        else: a=m; fa=fm
    return (a+b)/2

def _rotation_roots(L,theta0,M0,V0,q,EI):
    def theta(x): return theta0+M0*x/EI+V0*x*x/(2*EI)+q*x**3/(6*EI)
    points=[0.0,L]+[x for x in _quad_roots(q/2,V0,M0) if 0<x<L]
    points=sorted(set(points)); roots=[]
    scale=max(abs(theta(x)) for x in points); tol=max(scale*1e-12,1e-14)
    roots += [x for x in points if abs(theta(x))<=tol]
    for a,b in zip(points,points[1:]):
        if theta(a)*theta(b)<0: roots.append(_bisect(theta,a,b))
    return roots

def beam_extrema(*,node_positions,elements,result:BeamResult):
    """Return element/global |V|, |M| and |deflection| maxima and local x locations.

    Scope is limited to adjacent-node elements with constant UDL, matching the current
    ``solve_beam`` model. Point loads are supported when represented by explicit nodes.
    """
    positions=tuple(float(x) for x in node_positions)
    if len(elements)!=len(result.element_end_forces): raise ValueError("elements/result length mismatch")
    out=[]
    for i,(el,end) in enumerate(zip(elements,result.element_end_forces)):
        L=positions[el.end]-positions[el.start]; q=float(el.udl); EI=float(el.elastic_modulus)*float(el.inertia)
        if L<=0 or EI<=0 or not all(isfinite(v) for v in (L,q,EI)): raise ValueError("invalid beam element")
        # FE local end-action convention: physical M(0+)=-start_moment, V(0+)=start_shear.
        M0=-end.start_moment; V0=end.start_shear; v0=result.displacements[el.start]; t0=result.rotations[el.start]
        shear=lambda x: V0+q*x
        moment=lambda x: M0+V0*x+q*x*x/2
        deflection=lambda x: v0+t0*x+M0*x*x/(2*EI)+V0*x**3/(6*EI)+q*x**4/(24*EI)
        vc=[0.0,L]; mc=[0.0,L]
        if q:
            x=-V0/q
            if 0<x<L: mc.append(x)
        dc=[0.0,L]+_rotation_roots(L,t0,M0,V0,q,EI)
        vx=max(vc,key=lambda x:abs(shear(x))); mx=max(mc,key=lambda x:abs(moment(x))); dx=max(dc,key=lambda x:abs(deflection(x)))
        out.append(ElementExtrema(i,abs(shear(vx)),vx,abs(moment(mx)),mx,abs(deflection(dx)),dx))
    if not out: raise ValueError("at least one element is required")
    vs=max(out,key=lambda x:x.max_abs_shear); ms=max(out,key=lambda x:x.max_abs_moment); ds=max(out,key=lambda x:x.max_abs_deflection)
    return tuple(out), BeamExtrema(vs.max_abs_shear,vs.element_index,vs.max_abs_shear_x,ms.max_abs_moment,ms.element_index,ms.max_abs_moment_x,ds.max_abs_deflection,ds.element_index,ds.max_abs_deflection_x)
