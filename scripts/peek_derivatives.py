import sys,zipfile,gzip
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from bbbd_audit.io import release,HTTPRangeFile,EVIDENCE
f=next(f for f in release()["files"] if f["key"]=="experiment4.zip")
r=HTTPRangeFile(f["links"]["self"],f["size"]);r.blocksize=65536
with zipfile.ZipFile(r) as z:
    for desc in ['gaze_interpolation_timestamps','pupil_interpolation_timestamps','rpeak_timestamps','gaze_visualangle_eyetrack','pupil_eyetrack','filteredECG','head_eyetrack']:
        n=next(n for n in z.namelist() if n.startswith('derivatives/') and desc+'.tsv.gz' in n)
        b=z.read(n)
        print(n);print(gzip.decompress(b).decode()[:800])
