"""Patch verified external CalculiX 2.21 source IN PLACE for bounded diagnostic only.

Never copy upstream GPL sources into the public KB. Explicitly limited to
results.c and resultsmech.f; the pristine binary must be built first.
"""
from __future__ import annotations
import pathlib
import sys

C_HELPER = r'''
/* KB-CAND-007 isolated, read-only trace: no solver force modifications. */
static void kb_trace(ITG *nk, ITG mt, double *fn, ITG *nactdof,
                     double *f, ITG *ipompc, ITG *nodempc,
                     double *coefmpc, char *labmpc, ITG *nmpc,
                     double *fmpc, ITG *istep, ITG *iinc,
                     double *time, ITG calcul_fn, ITG calcul_f,
                     const char *phase){
  FILE *fp;
  ITG n,d,m,idx,term,maxactive=0;
  if(calcul_fn!=1 || getenv("KB_CCX_LEDGER")==NULL) return;
  fp=fopen("kb_force_ledger.tsv","a");
  if(fp==NULL) return;
  fprintf(fp,"KB_EVENT %s %d %d %.17g %d %d %d\n",phase,
          (int)*istep,(int)*iinc,*time,(int)*nk,(int)mt,(int)*nmpc);
  for(n=0;n<*nk;n++){
    for(d=1;d<mt;d++){
      ITG active=nactdof[mt*n+d];
      if(active>maxactive) maxactive=active;
      if(fn[mt*n+d]!=0.0)
        fprintf(fp,"KB_FN %s %d %d %d %.17g\n",phase,
                (int)(n+1),(int)d,(int)active,fn[mt*n+d]);
    }
  }
  if(phase[0]=='Q' && calcul_f==1){
    for(n=0;n<maxactive;n++)
      fprintf(fp,"KB_ACTIVE %d %.17g\n",(int)(n+1),f[n]);
  }
  if(phase[0]=='Q'){
    for(m=0;m<*nmpc;m++){
      ITG head=ipompc[m]-1;
      if(head<0) continue;
      if(nodempc[3*head+1]>3 ||
         strncmp(&labmpc[20*m],"FLUID",5)==0){
        fprintf(fp,"KB_MPC_NOT_EVALUATED %d\n",(int)(m+1));
        continue;
      }
      fprintf(fp,"KB_MPC %d %.*s %.17g\n",(int)(m+1),20,
              &labmpc[20*m],fmpc[m]);
      idx=head;
      for(term=0;idx>=0 && term<10000;term++){
        fprintf(fp,"KB_TERM %d %d %d %d %.17g\n",(int)(m+1),
                (int)(term+1),(int)nodempc[3*idx],
                (int)nodempc[3*idx+1],coefmpc[idx]);
        idx=nodempc[3*idx+2]-1;
      }
      if(term==10000) fprintf(fp,"KB_TERM_LIMIT %d\n",(int)(m+1));
    }
  }
  fclose(fp);
}
'''
# The iout>0 check keeps only output frames; the 2.21 caller owns both
# transform-dependent MPC sources and the following resultsforc call.
C_PRE='''  if((*iout>0) && getenv("KB_CCX_LEDGER")!=NULL)
    kb_trace(nk,mt,fn,nactdof,f,
       ((*mortar>1 && *mortartrafoflag==1)?ipompc2:ipompc),
       ((*mortar>1 && *mortartrafoflag==1)?nodempc2:nodempc),
       ((*mortar>1 && *mortartrafoflag==1)?coefmpc2:coefmpc),
       ((*mortar>1 && *mortartrafoflag==1)?labmpc2:labmpc),
       ((*mortar>1 && *mortartrafoflag==1)?nmpc2:nmpc),
       fmpc,istep,iinc,time,calcul_fn,calcul_f,"P");
'''
C_POST=C_PRE.replace('"P");','"Q");')
F_BEFORE='''!     KB diagnostic-only contact spring forces before accumulation.
              if((iout.gt.0).and.(lakonl(7:7).eq.'C')) then
                open(unit=91,file='kb_contact_ledger.tsv',
     &               status='unknown',position='append')
                do j=1,nope
                  write(91,*) 'KB_SPR',istep,iinc,i,j,konl(j),
     &                 fnl(1,j),fnl(2,j),fnl(3,j)
                enddo
                close(91)
              endif
'''

def replace_one(txt: str, anchor: str, new: str) -> str:
    count=txt.count(anchor)
    if count!=1: raise ValueError(f'ANCHOR_MISMATCH_{count}_{anchor[:40]}')
    return txt.replace(anchor,new,1)

def patch(root: pathlib.Path) -> None:
    source=root/'src'
    cpath=source/'results.c'
    fpath=source/'resultsmech.f'
    c=cpath.read_text(encoding='latin-1')
    f=fpath.read_text(encoding='latin-1')
    c=replace_one(c,'#include "mortar.h"','#include "mortar.h"\n#include <string.h>\n'+C_HELPER)
    c=replace_one(c,'  /* calculating the matrix system internal force vector */',
                  C_PRE+'\n  /* calculating the matrix system internal force vector */')
    c=replace_one(c,'  /* calculating the total energy if',
                  C_POST+'\n  /* calculating the total energy if')
    needle=('              do j=1,nope\n'
            '                do k=1,3\n'
            '                  fn(k,konl(j))=fn(k,konl(j))+fnl(k,j)\n'
            '                enddo\n'
            '              enddo')
    f=replace_one(f,needle,F_BEFORE+needle)
    cpath.write_text(c,encoding='latin-1')
    fpath.write_text(f,encoding='latin-1')
    print('KB_TRACE_PATCHED results.c resultsmech.f')

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('usage: ccx221_s8r_force_instrument.py CCX_DIR')
    patch(pathlib.Path(sys.argv[1]))
