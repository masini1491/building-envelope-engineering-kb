/* Isolated, synthetic C caller for version-checked CalculiX resultsforc.c.
 * No original CalculiX source is redistributed by this harness.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "CalculiX.h"

ITG strcmp1(const char *src, const char *target) {
  size_t n = strlen(target);
  if (strncmp(src,target,n)!=0) return 1;
  for(size_t i=n;i<20;i++) if(src[i]!=' ' && src[i]!='\0') return 1;
  return 0;
}
void forparll(ITG *mt,ITG *nactdof,double *f,double *fn,ITG *nk,ITG *num_cpus) {
  (void)num_cpus;
  for(ITG i=0;i<*nk;i++) for(ITG j=0;j<*mt;j++)
    if(nactdof[(*mt)*i+j]>0) f[nactdof[(*mt)*i+j]-1]=fn[(*mt)*i+j];
}
void expect(int ok, const char *why) { if(!ok) { fprintf(stderr,"FAIL %s\n",why);exit(1); } }
void close_num(double actual,double want,const char *why) { expect(fabs(actual-want)<1e-12,why); }
static void scenario(double dep,double ind,int calculate_fn,int calculate_f) {
  ITG nk=2,mi[]={1,3},num_cpus=1,nmpc=1;
  ITG active[8]={0,0,0,0,0,0,0,1};
  ITG head[]={1};
  ITG chain[]={1,3,2, 2,3,0};
  double coef[]={1.,-1.}, fn[8]={0},f[]={-777.},fmpc[]={-777.};
  char labels[20];memset(labels,' ',sizeof(labels));memcpy(labels,"GENERIC",7);
  fn[3]=dep;fn[7]=ind;
  resultsforc(&nk,f,fn,active,head,chain,coef,labels,&nmpc,mi,fmpc,&calculate_fn,&calculate_f,&num_cpus);
  if(calculate_fn){
    close_num(fmpc[0],dep,"MPC multiplier of dependent node");
    close_num(fn[3],dep,"dependent node reconstituted");
    close_num(fn[7],ind,"independent node reconstituted");
  } else close_num(fmpc[0],-777.,"MPC multiplier untouched");
  if(calculate_f)close_num(f[0],calculate_fn?ind+dep:ind,"assembled active DOF system force");
  else close_num(f[0],-777.,"system force calculation disabled");
}
int main(void){
 scenario(10.,-10.,1,1);
 scenario(10.,0.,1,1);
 scenario(10.,-10.,1,0);
 scenario(10.,-10.,0,1);
 puts("CCX221_MPC_FORCE_BOOKKEEPING_ISOLATED_PASS_NOT_ENGINEERING_ORACLE");
 return 0;
}
