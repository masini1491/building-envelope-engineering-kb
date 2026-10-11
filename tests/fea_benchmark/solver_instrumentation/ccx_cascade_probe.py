"""Stage 30: bounded exact CalculiX cascade.c entry/exit MPC observation.

Captures source-internal term counts, not shell reaction moments or support
forces. Only instruments a SHA-pinned isolated GPL-2.0 solver build.
"""
from pathlib import Path
import hashlib
import argparse

EXPECTED_SHA="430911d6f9f91078c0efb826ba103656a504e46ec0d3ce74356b91b4333336c4"
INCLUDE='#include "CalculiX.h"\n'
START='  coefmpc=*coefmpcp;\n'
END='  *coefmpcp=coefmpc;\n'
HELPER=r'''
/* Bounded experimental cascade audit; GPL-2.0-only contribution. */
static void kb_cascade_trace(const char *phase,ITG *ipompc,ITG *nodempc,
                             char *labmpc,ITG nmpc){
    const char *path=getenv("CCX_CASCADE_AUDIT_FILE");
    static unsigned long call_id=0;
    unsigned long sequence;
    ITG i,count=0,term_total=0,max_terms=0;
    FILE *file,*detail_file=NULL;
    const char *detail_path=getenv("CCX_CASCADE_DETAIL_FILE");
    if(path==NULL || path[0]=='\0') return;
    if(strcmp(phase,"IN")==0) call_id++;
    sequence=call_id;
    if(nmpc<0 || nmpc>1000000) exit(74);
    if(detail_path!=NULL && detail_path[0]!='\0'){
        detail_file=fopen(detail_path,"a");
        if(detail_file==NULL)exit(69);
    }
    for(i=0;i<nmpc;i++){
        ITG index,local_count=0;
        if(strncmp(&labmpc[20*i],"MEANROT",7)!=0)continue;
        count++;
        index=ipompc[i];
        if(index<=0)exit(73);
        while(index>0){
            local_count++;
            if(local_count>96)exit(72);
            index=nodempc[3*index-1];
        }
        term_total+=local_count;
        if(detail_file!=NULL){
            fprintf(detail_file,"CASCADE_DETAIL_V1,%lu,%s,%lld,%lld\n",
                    sequence,phase,(long long)(i+1),(long long)local_count);
        }
        if(local_count>max_terms)max_terms=local_count;
    }
    file=fopen(path,"a");
    if(file==NULL)exit(71);
    fprintf(file,"CASCADE_V1,%lu,%s,%lld,%lld,%lld\n",
            sequence,phase,(long long)count,
            (long long)term_total,(long long)max_terms);
    if(fclose(file)!=0)exit(70);
    if(detail_file!=NULL && fclose(detail_file)!=0)exit(68);
}
'''

def patch(s:str)->str:
    if any(s.count(t)!=1 for t in (INCLUDE,START,END)):
        raise ValueError("UNKNOWN_CASCADE_SOURCE_STRUCTURE")
    if "CCX_CASCADE_AUDIT_FILE" in s:raise ValueError("ALREADY_INSTRUMENTED")
    return (s.replace(INCLUDE,INCLUDE+HELPER,1)
        .replace(START,START+'  kb_cascade_trace("IN",ipompc,nodempc,labmpc,*nmpc);\n',1)
        .replace(END,END+'  kb_cascade_trace("OUT",ipompc,nodempc,labmpc,*nmpc);\n',1))

def main():
    a=argparse.ArgumentParser();a.add_argument("source",type=Path)
    p=a.parse_args().source
    raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA:
        raise ValueError("CASCADE_EXACT_SOURCE_HASH_MISMATCH")
    data=patch(raw.decode("latin1")).encode("latin1")
    p.write_bytes(data)
    print("CASCADE_INSTRUMENTED_SHA256",hashlib.sha256(data).hexdigest())

if __name__=="__main__":main()
