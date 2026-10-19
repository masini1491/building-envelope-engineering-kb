"""Read-only CalculiX 2.21 DOF5 / MEANROTBS generalized-force diagnostic.

Patch only a *copied*, source-hash-pinned GPL tree outside the public KB.
Never modify equations, contact behavior, constraints or force vectors. The
recorded fmpc is internal bookkeeping, NOT an admitted physical dual.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
from ccx221_rot5_owner_instrument import OWNER_1, OWNER_2, TRACE_1, TRACE_2, insert_once

GEN_SHA = '5cd4c1adc7875c069d09f1bad3f91b38e9f2462547771c05ee07db29a2ac6a75'
RESULTS_SHA = 'c0f3ea576b174ae3378938af7a25a190e8004a75a54498ac2da4f5580dbf1759'
C_HELPER = r'''
/* KB-CAND-007 research only. fmpc is not an independently measured dual. */
static void kb_rot_dual_trace(const char *phase, ITG *nk, ITG mt,
   ITG *nboun, ITG *nodeboun, ITG *ndirboun, double *xboun,
   double *fn, ITG *nactdof, ITG *ipompc, ITG *nodempc,
   double *coefmpc, char *labmpc, ITG *nmpc, double *fmpc,
   ITG *istep, ITG *iinc, double *time){
  FILE *fp;
  ITG k,n,d,m,idx,term;
  if(getenv("KB_ROT_DUAL")==NULL || fabs(*time-1.0)>1.e-7) return;
  fp=fopen("kb_rot_dual.tsv","a");
  if(!fp) return;
  fprintf(fp,"KB_ROT_PHASE %s %d %d %.17g %d %d %d\n",phase,
      (int)*istep,(int)*iinc,*time,(int)*nk,(int)*nboun,(int)*nmpc);
  for(k=0;k<*nboun;k++){
    n=nodeboun[k]; d=ndirboun[k];
    if(n<1 || n>*nk || d<1 || d>3) continue;
    fprintf(fp,"KB_ROT_SPC %s %d %d %d %d %.17g %.17g\n",phase,
        (int)(k+1),(int)n,(int)d,(int)nactdof[mt*(n-1)+d],
        xboun[k],fn[mt*(n-1)+d]);
  }
  if(phase[0]=='Q'){
    for(m=0;m<*nmpc;m++){
      if(strncmp(&labmpc[20*m],"MEANROT",7)!=0) continue;
      idx=ipompc[m]-1;
      if(idx<0) continue;
      fprintf(fp,"KB_ROT_MPC %d %.17g\n",(int)(m+1),fmpc[m]);
      for(term=1;idx>=0 && term<=10000;term++){
        fprintf(fp,"KB_ROT_TERM %d %d %d %d %.17g\n",(int)(m+1),
            (int)term,(int)nodempc[3*idx],(int)nodempc[3*idx+1],
            coefmpc[idx]);
        idx=nodempc[3*idx+2]-1;
      }
      if(idx>=0) fprintf(fp,"KB_ROT_TERM_LIMIT %d\n",(int)(m+1));
    }
  }
  fclose(fp);
}
'''
PRE = '''  if((*iout>0) && (calcul_fn==1))
    kb_rot_dual_trace("P",nk,mt,nboun,nodeboun,ndirboun,xboun,
        fn,nactdof,((*mortar>1 && *mortartrafoflag==1)?ipompc2:ipompc),
        ((*mortar>1 && *mortartrafoflag==1)?nodempc2:nodempc),
        ((*mortar>1 && *mortartrafoflag==1)?coefmpc2:coefmpc),
        ((*mortar>1 && *mortartrafoflag==1)?labmpc2:labmpc),
        ((*mortar>1 && *mortartrafoflag==1)?nmpc2:nmpc),
        fmpc,istep,iinc,time);
'''
POST = PRE.replace('"P",','"Q",')

def patch(root: Path) -> None:
    src = root/'src'
    gen = src/'gen3dboun.f'
    cfile = src/'results.c'
    g = gen.read_bytes()
    c = cfile.read_bytes()
    if hashlib.sha256(g).hexdigest()!=GEN_SHA or hashlib.sha256(c).hexdigest()!=RESULTS_SHA:
        raise ValueError('CCX221_DUAL_SOURCE_PIN_MISMATCH')
    g_new = insert_once(insert_once(g.decode('latin-1'), OWNER_1, TRACE_1), OWNER_2, TRACE_2)
    original = c.decode('latin-1')
    if original.count('#include "mortar.h"')!=1 or original.count('  /* calculating the matrix system internal force vector */')!=1 or original.count('  /* calculating the total energy if')!=1:
        raise ValueError('CCX221_DUAL_C_ANCHOR_MISMATCH')
    c_new = original.replace('#include "mortar.h"','#include "mortar.h"\n#include <string.h>\n'+C_HELPER,1)
    c_new = c_new.replace('  /* calculating the matrix system internal force vector */',PRE+'  /* calculating the matrix system internal force vector */',1)
    c_new = c_new.replace('  /* calculating the total energy if',POST+'  /* calculating the total energy if',1)
    gen.write_bytes(g_new.encode('latin-1'))
    cfile.write_bytes(c_new.encode('latin-1'))
    print('CCX221_ROT5_DUAL_PATCHED_READ_ONLY_GEN3DBOUN_RESULTS')

if __name__=='__main__':
    import sys
    if len(sys.argv)!=2: raise SystemExit('usage: ccx221_rot5_dual_instrument.py CCX_ROOT')
    patch(Path(sys.argv[1]))
