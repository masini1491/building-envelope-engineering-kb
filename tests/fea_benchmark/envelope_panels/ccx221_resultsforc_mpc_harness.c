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

static void weighted_three_term(double a,double b,double c,double dep,double n2,double n3,double multiplier,double e2,double e3) {
  ITG nk=3,mi[]={1,3},cpu=1,nmpc=1,calc_fn=1,calc_f=1;
  ITG active[12]={0,0,0,0,0,0,0,1,0,0,0,2};
  ITG head[]={1},chain[]={1,3,2, 2,3,3, 3,3,0};
  double coef[]={a,b,c},fn[12]={0},f[]={-777.,-777.},fm[]={-777.};
  char label[20];memset(label,' ',20);memcpy(label,"GENERIC",7);
  fn[3]=dep;fn[7]=n2;fn[11]=n3;
  resultsforc(&nk,f,fn,active,head,chain,coef,label,&nmpc,mi,fm,&calc_fn,&calc_f,&cpu);
  close_num(fm[0],multiplier,"weighted multiplier");
  close_num(f[0],e2,"weighted reduced independent DOF2");
  close_num(f[1],e3,"weighted reduced independent DOF3");
  close_num(fn[3],dep,"weighted dependent restored");
  close_num(fn[7],n2,"weighted independent2 restored");
  close_num(fn[11],n3,"weighted independent3 restored");
}
static void two_independent_mpcs(void) {
  ITG nk=4,mi[]={1,3},cpu=1,nmpc=2,calc_fn=1,calc_f=1;
  ITG active[16]={0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,2};
  ITG head[]={1,3},chain[]={1,3,2, 2,3,0, 3,3,4, 4,3,0};
  double coef[]={1.,-1.,2.,-1.},fn[16]={0},f[]={-777.,-777.},fm[]={-777.,-777.};
  char label[40];memset(label,' ',40);memcpy(label,"GENERIC",7);memcpy(label+20,"GENERIC",7);
  fn[3]=10.;fn[7]=-10.;fn[11]=8.;fn[15]=-4.;
  resultsforc(&nk,f,fn,active,head,chain,coef,label,&nmpc,mi,fm,&calc_fn,&calc_f,&cpu);
  close_num(fm[0],10.,"first multiplier");close_num(fm[1],4.,"second multiplier");
  close_num(f[0],0.,"first reduced force");close_num(f[1],0.,"second reduced force");
  close_num(fn[3],10.,"first dep restored");close_num(fn[7],-10.,"first ind restored");
  close_num(fn[11],8.,"second dep restored");close_num(fn[15],-4.,"second ind restored");
}

int main(void){
 scenario(10.,-10.,1,1);
 scenario(10.,0.,1,1);
 scenario(10.,-10.,1,0);
 scenario(10.,-10.,0,1);
 /* Distinguish reduced generalized force from raw-Z arithmetic: c=(1,-2) */
 weighted_three_term(1.,-2.,0.,10.,-20.,0.,10.,0.,0.);
 weighted_three_term(1.,-.6,-.4,10.,-6.,-4.,10.,0.,0.);
 weighted_three_term(2.,-1.,-1.,10.,-5.,-5.,5.,0.,0.);
 two_independent_mpcs();
 puts("CCX221_MPC_FORCE_BOOKKEEPING_ISOLATED_PASS_NOT_ENGINEERING_ORACLE");
 return 0;
}
