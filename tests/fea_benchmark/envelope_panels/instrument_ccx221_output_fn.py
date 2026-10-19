"""Research-only, opt-in iout=2 original nodal internal force; NOT SPC dual."""
import pathlib
import sys

ANCHOR = '  /* calculating the total energy if'
SNAPSHOT = r'''  /* KB_CCX221_OUTPUT_FN: output-stage original nodal internal force only. */
  if(*iout==2){
    const char *kb_probe=getenv("KB_CCX221_OUTPUT_FN");
    if(kb_probe && kb_probe[0]=='1' && kb_probe[1]=='\0'){
      FILE *kb_file=fopen("kb_ccx221_output_fn.tsv","a");
      if(!kb_file){
        fprintf(stderr,"KB_OUTPUT_FN_OPEN_FAILED\n");
        exit(1);
      }
      ITG kb_i,kb_d;
      fprintf(kb_file,"KB_OUTPUT_FN_BEGIN %" ITGFORMAT " %" ITGFORMAT " %" ITGFORMAT " %" ITGFORMAT "\n",*istep,*iinc,*nk,mi[1]+1);
      for(kb_i=0;kb_i<*nk;kb_i++){
        for(kb_d=0;kb_d<mi[1]+1;kb_d++){
          fprintf(kb_file,"KB_OUTPUT_FN %" ITGFORMAT " %" ITGFORMAT " %.17g %" ITGFORMAT "\n",kb_i+1,kb_d,fn[(mi[1]+1)*kb_i+kb_d],nactdof[(mi[1]+1)*kb_i+kb_d]);
        }
      }
      fprintf(kb_file,"KB_OUTPUT_FN_END\n");
      if(fclose(kb_file)!=0){
        fprintf(stderr,"KB_OUTPUT_FN_CLOSE_FAILED\n");
        exit(1);
      }
    }
  }

'''
def instrument(source):
    if source.count(ANCHOR)!=1 or 'KB_CCX221_OUTPUT_FN' in source:
        raise ValueError('KB_OUTPUT_FN_ANCHOR_OR_ALREADY_PATCHED')
    return source.replace(ANCHOR,SNAPSHOT+ANCHOR,1)

if __name__=='__main__':
    if len(sys.argv)!=2:
        raise SystemExit('usage: instrument_ccx221_output_fn.py ccx_2.21')
    path=pathlib.Path(sys.argv[1])/'src/results.c'
    path.write_text(instrument(path.read_text()))
