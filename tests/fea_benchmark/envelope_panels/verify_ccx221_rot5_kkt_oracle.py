"""Independent rational KKT / externally applied virtual-work control.

This oracle deliberately does NOT use CalculiX's fmpc or ELSE and cannot
admit physical shell reaction moments. It validates virtual-work algebra,
constraint transformation, nonhomogeneous SPC offsets, and applied loads.
"""
from __future__ import annotations
from fractions import Fraction as F


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), F(0))


def mv(A, u):
    return [dot(row, u) for row in A]


def transpose(A):
    return list(map(list, zip(*A)))


def solve(A, b):
    """Exact Gauss-Jordan solver; reject singular/invalid dimensions."""
    n=len(A)
    if not n or len(b)!=n or any(len(row)!=n for row in A):
        raise ValueError('KKT_SHAPE')
    m=[[F(v) for v in row]+[F(b[i])] for i,row in enumerate(A)]
    for j in range(n):
        pivot=next((i for i in range(j,n) if m[i][j]),None)
        if pivot is None:raise ValueError('KKT_SINGULAR')
        m[j],m[pivot]=m[pivot],m[j]
        p=m[j][j]
        m[j]=[v/p for v in m[j]]
        for i in range(n):
            if i!=j:
                scale=m[i][j]
                m[i]=[x-scale*y for x,y in zip(m[i],m[j])]
    return [row[-1] for row in m]


def exact_constraint_work(K,C,external,g,grad_g):
    """KKT: K u - f + C^T lambda=0, C u=g.

    Applied generalized holding force is -lambda^T g' (not lambda^T g').
    No numerical derivatives, no CCX force bookkeeping.
    """
    n=len(K);m=len(C)
    if n==0 or m==0 or len(external)!=n or len(g)!=m or len(grad_g)!=m:
        raise ValueError('KKT_SHAPE')
    if any(len(x)!=n for x in K) or any(len(x)!=n for x in C):
        raise ValueError('KKT_SHAPE')
    if any(K[i][j]!=K[j][i] for i in range(n) for j in range(n)):
        raise ValueError('KKT_ASYMMETRIC')
    zero=[[F(0)]*m for _ in range(m)]
    matrix=[list(K[i])+list(transpose(C)[i]) for i in range(n)]
    matrix += [list(C[i])+list(zero[i]) for i in range(m)]
    y=solve(matrix,list(external)+list(g))
    u=y[:n];lam=y[n:]
    # Differentiate the full saddle-point system analytically, including
    # unconstrained DOFs (n > m).  Assumes fixed K, C and applied nodal f.
    # C*u'=g' and K*u'+C^T*lambda'=0; no finite differences or CCX data.
    tangent_solution=solve(matrix,[F(0)]*n+list(grad_g))
    tangent=tangent_solution[:n]
    lambda_tangent=tangent_solution[n:]
    residual=[a-b+c for a,b,c in zip(mv(K,u),external,mv(transpose(C),lam))]
    tangent_residual=[a+b for a,b in zip(mv(K,tangent),mv(transpose(C),lambda_tangent))]
    if (any(residual) or any(tangent_residual) or mv(C,u)!=list(g)
            or mv(C,tangent)!=list(grad_g)):
        raise ValueError('KKT_RESIDUAL')
    energy_power=dot(mv(K,u),tangent)
    external_power=dot(external,tangent)
    applied_power=energy_power-external_power
    dual_power=-dot(lam,grad_g)
    if dual_power!=applied_power:raise ValueError('KKT_VIRTUAL_WORK_MISMATCH')
    return dict(u=u,lam=lam,tangent=tangent,energy_power=energy_power,
                external_power=external_power,applied_power=applied_power,
                dual_power=dual_power,stationarity_residual=F(0),
                tangent_stationarity_residual=F(0))


def reference_48():
    a=F(100);k=F(120);theta=F(1,50000)
    return exact_constraint_work([[k,0],[0,k]],[[1,0],[0,1]],[0,0],
                                 [-a*theta,a*theta],[-a,a])


def reference_inhomogeneous():
    a=F(100);theta=F(1,50000);offset=F(1,10);beta=F(2)
    C=[[1,0,-1],[0,1,-1],[0,0,1]]
    return exact_constraint_work([[F(120),0,0],[0,F(120),0],[0,0,F(10)]],C,
                                 [F(0),F(0),F(1)],
                                 [-a*theta,a*theta,offset+beta*theta],[-a,a,beta])


def reference_rectangular_mpc():
    """3 translations, two ideal MPC constraints, one free translation.

    u1-u3=-100 theta, u2-u3=+100 theta; theta=2e-5 rad.
    K=diag(120,240,60) N/mm; external f3=1 N.  Independent
    equilibrium/virtual-work solution: u3=19/10500 mm,
    u3'=-200/7 mm/rad, Q_theta=656/7 N.mm.
    """
    a=F(100);theta=F(1,50000)
    return exact_constraint_work([[F(120),0,0],[0,F(240),0],[0,0,F(60)]],
                                 [[1,0,-1],[0,1,-1]],
                                 [F(0),F(0),F(1)],
                                 [-a*theta,a*theta],[-a,a])
