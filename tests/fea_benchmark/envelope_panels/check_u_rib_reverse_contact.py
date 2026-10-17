"""Diagnostic-only reversed master/slave S8R contact pairing."""
import hashlib,json,math,sys
from pathlib import Path
from check_u_rib_base_contact import deck as source_deck,MESHES
from check_u_rib_contact_observations import rf,contact_print
CASES=("toward","away")
SCOPE="SYNTHETIC_U_RIB_CONTACT_REVERSED_PAIR_OBSERVATION_NOT_ADMITTED"
def deck(n,case):
    if type(n) is not int or n not in MESHES or case not in CASES:raise ValueError("SWAP_SCOPE")
    original=source_deck(n,case)
    # CONTACT PAIR and CONTACT PRINT use different complete keyword lines.
    # Replace only those exact lines; do not alter any geometry or constraints.
    pair="RIB_BASE_UNDERSIDE,PLATE_TOP"
    reverse="PLATE_TOP,RIB_BASE_UNDERSIDE"
    print_old="*CONTACT PRINT,SLAVE=RIB_BASE_UNDERSIDE,MASTER=PLATE_TOP"
    print_new="*CONTACT PRINT,SLAVE=PLATE_TOP,MASTER=RIB_BASE_UNDERSIDE"
    lines=original.splitlines()
    if lines.count(pair)!=1 or lines.count(print_old)!=1:
        raise ValueError("SWAP_ORIGIN")
    return original.replace(pair+"\n",reverse+"\n",1).replace(
        print_old+"\n",print_new+"\n",1)
def generate(folder,n,case):
    p=Path(folder)
    if p.exists() or p.is_symlink():raise ValueError("SWAP_WORKDIR")
    p.mkdir(parents=True)
    (p/"panel.inp").write_text(deck(n,case),encoding="utf-8")
def observe(root):
    out={}
    for n in MESHES:
        out[str(n)]={}
        for case in CASES:
            p=Path(root)/f"u_reverse_contact_n{n}_{case}"
            files={ext:p/f"panel.{ext}" for ext in ("inp","sta","dat","frd")}
            if any(f.is_symlink() or not f.is_file() or not 0<f.stat().st_size<64000000 for f in files.values()):
                raise ValueError("SWAP_MISSING_ARTIFACT")
            if files["inp"].read_bytes()!=deck(n,case).encode():raise ValueError("SWAP_DECK_MISMATCH")
            st=files["sta"].read_text(encoding="ascii")
            times=[float(t[4]) for line in st.splitlines() if len(t:=line.split())==7 and t[0]=="1"]
            if not times or abs(times[-1]-1.)>1e-7:raise ValueError("SWAP_INCOMPLETE")
            dat=files["dat"].read_text(encoding="utf-8",errors="replace")
            groups={name:rf(dat,name) for name in ("PLATE_EDGE_RF","RIB_END_RF","CENTER_RF")}
            surface=contact_print(dat,"PLATE_TOP","RIB_BASE_UNDERSIDE")
            raw=sum(v["sum_rf3_n"] for v in groups.values())
            out[str(n)][case]={"rf":groups,"raw_rf3_sum_n":raw,"contact":surface,
                                "sha256":{ext:hashlib.sha256(f.read_bytes()).hexdigest() for ext,f in files.items()},
                                "independent_balance":"NOT_ESTABLISHED","engineering_acceptance":"NOT_ADMITTED"}
    return {"scope":SCOPE,"cases":out,"contact_oracle":"NOT_ESTABLISHED",
            "engineering_acceptance":"NOT_ADMITTED"}
if __name__=="__main__":
    if len(sys.argv)==5 and sys.argv[1]=="--generate":
        generate(sys.argv[2],int(sys.argv[3]),sys.argv[4])
    elif len(sys.argv)==2:print(json.dumps(observe(sys.argv[1]),sort_keys=True,allow_nan=False))
    else:raise SystemExit("usage")
