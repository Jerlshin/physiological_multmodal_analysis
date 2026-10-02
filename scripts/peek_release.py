"""Small release metadata inspection while full archives are being acquired."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from bbbd_audit.io import release, HTTPRangeFile, EVIDENCE, write_json
import zipfile

for f in sorted(release()["files"],key=lambda f:f["key"]):
    r=HTTPRangeFile(f["links"]["self"],f["size"])
    r.blocksize=65536
    with zipfile.ZipFile(r) as z:
        selected=[n for n in z.namelist() if "/" not in n or n.startswith("phenotype/")]
        subjects=sorted(set(n.split("/")[0] for n in z.namelist() if n.startswith("sub-")))
        if subjects:
            prefix=subjects[0]+"/ses-01/"
            selected += [n for n in z.namelist() if n.startswith(prefix) and n.endswith((".json","channels.tsv","events.tsv")) and "stim01" in n or n.startswith(prefix) and n.endswith((".json","channels.tsv","events.tsv")) and "stim04" in n]
        out=EVIDENCE/"release_metadata"/f["key"].replace(".zip","")
        for n in selected:
            if n.endswith("/"): continue
            p=out/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
        print(f["key"],len(selected),r.transferred,"bytes fetched",flush=True)
