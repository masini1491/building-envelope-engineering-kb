"""Stage 28 exact CalculiX 2.21 usermpc MEANROT term-role provenance.

Isolated GPL source patch only. Reports the internal angle/inhomogeneous
helper terms, not independently measured rotational support reactions.
"""
from __future__ import annotations
import hashlib
import argparse
from pathlib import Path

EXPECTED_SHA="97d49518ea8306d0ba9b88c0861c4bfb45487d45836f765d01b9d624548e2fe5"
SPEC="      save nodevector\n"
ELSE="      else\n!\n!        MPC definition finished: add a nonhomogeneous term\n"
NK="         nk=nk+1\n"
TAIL="      return\n      end\n"
DECL="""      integer audit_emit,audit_inhom_node,audit_status,audit_unit
      integer audit_index,audit_slot,audit_node,audit_dof,audit_role
      character*512 audit_path
"""
BODY="""      if(audit_emit.eq.1) then
         if(labmpc(nmpc)(1:7).eq.'MEANROT') then
            audit_path=' '
            call get_environment_variable('CCX_MPC_ROLES_FILE',
     &           audit_path,status=audit_status)
            if(audit_status.eq.0.and.len_trim(audit_path).gt.0) then
               open(newunit=audit_unit,file=trim(audit_path),
     &              status='unknown',position='append',
     &              iostat=audit_status)
               if(audit_status.ne.0) stop 87
               audit_index=ipompc(nmpc)
               audit_slot=0
               do
                  if(audit_index.le.0) exit
                  audit_slot=audit_slot+1
                  if(audit_slot.gt.96) stop 86
                  audit_node=nodempc(1,audit_index)
                  audit_dof=nodempc(2,audit_index)
                  audit_role=0
                  if(audit_node.eq.nodevector) audit_role=1
                  if(audit_node.eq.audit_inhom_node)
     &               audit_role=2
                  write(audit_unit,'(A,6(I0,A),I0)')
     &                 'ROLE_TERM,',nmpc,',',audit_slot,',',
     &                 audit_node,',',audit_dof,',',audit_role,',',
     &                 noderef,',',idirref
                  audit_index=nodempc(3,audit_index)
               enddo
               write(audit_unit,'(A,5(I0,A),I0)')
     &              'ROLE_END,',nmpc,',',audit_slot,',',
     &              nodevector,',',audit_inhom_node,',',
     &              noderef,',',idirref
               close(audit_unit,iostat=audit_status)
               if(audit_status.ne.0) stop 85
            endif
         endif
      endif
"""

def patch(text: str)->str:
    if any(text.count(x)!=1 for x in (SPEC,ELSE,NK,TAIL)):
        raise ValueError("UNRECOGNIZED_221_USERMPC_STRUCTURE")
    if "CCX_MPC_ROLES_FILE" in text:raise ValueError("ALREADY_INSTRUMENTED")
    return (text.replace(SPEC,DECL+SPEC,1)
        .replace(SPEC,SPEC+"      audit_emit=0\n      audit_inhom_node=0\n",1)
        .replace(ELSE,ELSE.replace("      else\n","      else\n         audit_emit=1\n",1),1)
        .replace(NK,NK+"         audit_inhom_node=nk\n",1)
        .replace(TAIL,BODY+TAIL,1))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path)
    a=p.parse_args()
    raw=a.source.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED_SHA:
        raise ValueError("USERMPC_EXACT_SOURCE_HASH_MISMATCH")
    altered=patch(raw.decode("latin1")).encode("latin1")
    a.source.write_bytes(altered)
    print("USERMPC_INSTRUMENTED_SHA256",hashlib.sha256(altered).hexdigest())

if __name__=="__main__":main()
