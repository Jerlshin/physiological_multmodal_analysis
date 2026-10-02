"""Version-pinned acquisition and bounded-memory ZIP access."""
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/dataset_exploration/evidence"
DATA = ROOT / "data/bbbd"

def now():
    return datetime.now(timezone.utc).isoformat()

def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, allow_nan=False, default=str) + "\n")
    os.replace(tmp, path)

def release():
    d = json.loads((EVIDENCE / "zenodo_record_22968459.json").read_text())
    if d["id"] != 22968459 or d["metadata"]["version"] != "1.1" or d["metadata"]["publication_date"] != "2026-09-25":
        raise ValueError("Stale/wrong release; refusing acquisition")
    return d

class HTTPRangeFile(io.RawIOBase):
    """Seekable read-only remote ZIP with one MiB LRU blocks; rejects ignored ranges."""
    def __init__(self, url, size):
        self.url, self.size, self.pos = url, size, 0
        self.blocksize, self.cache, self.transferred = 1048576, {}, 0
    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos
    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        if self.pos < 0: raise ValueError("negative seek")
        return self.pos
    def read(self, n=-1):
        n = max(0, self.size-self.pos) if n < 0 else min(n, max(0,self.size-self.pos))
        out = []
        while n:
            start = (self.pos // self.blocksize) * self.blocksize
            if start not in self.cache:
                end = min(self.size-1, start+self.blocksize-1)
                b = subprocess.check_output(["curl","-L","--fail","--retry","4","--retry-delay","2","--connect-timeout","20","--max-time","120","-sS","-r",f"{start}-{end}",self.url])
                if len(b) != end-start+1: raise IOError("Server ignored range or truncated response")
                self.transferred += len(b)
                if len(self.cache) >= 8: self.cache.pop(next(iter(self.cache)))
                self.cache[start] = b
            block = self.cache[start]
            take = min(n,len(block)-(self.pos-start))
            out.append(block[self.pos-start:self.pos-start+take])
            n -= take; self.pos += take
        return b"".join(out)

def inventory():
    import pandas as pd
    rows, retrieval = [], []
    for f in sorted(release()["files"], key=lambda x:x["key"]):
        local = DATA / "canonical_source" / f["key"]
        handle = open(local,"rb") if local.exists() else HTTPRangeFile(f["links"]["self"],f["size"])
        with zipfile.ZipFile(handle) as z:
            for i in z.infolist():
                rows.append(dict(archive=f["key"],path=i.filename,bytes=i.file_size,compressed_bytes=i.compress_size,crc32=f"{i.CRC:08x}",compression=i.compress_type,is_directory=i.is_dir(),offset=i.header_offset))
        retrieval.append(dict(archive=f["key"],time_utc=now(),remote_directory_bytes=getattr(handle,"transferred",0)))
        handle.close()
        print("Inventoried",f["key"],sum(x["archive"]==f["key"] for x in rows),flush=True)
    pd.DataFrame(rows).to_parquet(EVIDENCE/"archive_members.parquet",index=False,compression="zstd")
    write_json(EVIDENCE/"directory_retrieval.json",retrieval)

def storage_snapshot(label):
    totals = {}
    roots = {"canonical_source":DATA/"canonical_source","extracted_source":DATA/"extracted_source","derived_reproducible":DATA/"derived_reproducible","temporary_cache":DATA/"temporary_cache","final_evidence":EVIDENCE.parent,"environment_regenerable":ROOT/".venv"}
    for k,p in roots.items():
        files = [q for q in p.rglob("*") if q.is_file()] if p.exists() else []
        if k=='final_evidence':
            files += [q for folder in ['src','tests','scripts'] for q in (ROOT/folder).rglob('*.py')]
            files += [ROOT/n for n in ['audit_config.json','requirements-audit.lock','pyproject.toml','.gitignore'] if (ROOT/n).is_file()]
        totals[k] = {"logical_bytes":sum(q.stat().st_size for q in files),"allocated_bytes":sum(q.stat().st_blocks*512 for q in files),"files":len(files)}
    d = dict(label=label,time_utc=now(),categories=totals,free_bytes=shutil.disk_usage(ROOT).free,accounting_schema_version=2,note='final_evidence includes reports, figures and generating infrastructure; earlier schema counted evidence/ only')
    with (EVIDENCE/"disk_usage.jsonl").open("a") as f: f.write(json.dumps(d)+"\n")
    return d

def verify_file(path, expected):
    sha,md5 = hashlib.sha256(),hashlib.md5()
    with Path(path).open("rb") as f:
        while b:=f.read(8*1024*1024): sha.update(b); md5.update(b)
    if Path(path).stat().st_size != expected["size"] or "md5:"+md5.hexdigest()!=expected["checksum"]:
        raise ValueError(f"Size/checksum mismatch: {path}")
    return sha.hexdigest(), md5.hexdigest()

def verified_entry(row, expected, local_bytes):
    """A cached verification is valid only for this exact official release identity."""
    return (row.get('status')=='verified' and row.get('release_id')==22968459
            and row.get('version')=='1.1' and row.get('release_date')=='2026-09-25'
            and row.get('official_checksum')==expected['checksum']
            and 'md5:'+row.get('computed_md5','')==expected['checksum']
            and row.get('official_bytes')==expected['size']
            and row.get('local_bytes')==local_bytes==expected['size']
            and len(row.get('sha256',''))==64)

def segmented_transfer(part, f, workers=6, chunk=16*1024*1024):
    """Bounded parallel range download with durable per-chunk resume ledger.

    No temporary full copies: write validated ranges directly to a single sparse
    .part file. Resume trust is limited to locally hashed chunks; official MD5
    validates the complete archive before promotion.
    """
    ledger_path=part.with_suffix(part.suffix+".chunks.json")
    if ledger_path.exists():
        ledger=json.loads(ledger_path.read_text())
        if ledger["official_checksum"]!=f["checksum"] or ledger["bytes"]!=f["size"]: raise ValueError("Stale partial ledger")
    else:
        prefix=part.stat().st_size if part.exists() else 0
        ledger=dict(official_checksum=f["checksum"],bytes=f["size"],chunk_bytes=chunk,completed={})
        if prefix:
            with part.open("rb") as inp:
                for start in range(0,prefix-chunk+1,chunk):
                    b=inp.read(chunk); ledger["completed"][str(start)]=hashlib.sha256(b).hexdigest()
    # Validate resumable ranges rather than trusting a completion flag.
    if part.exists():
        with part.open("rb") as inp:
            for s,h in list(ledger["completed"].items()):
                start=int(s); inp.seek(start); b=inp.read(min(chunk,f["size"]-start))
                if hashlib.sha256(b).hexdigest()!=h: del ledger["completed"][s]
    fd=os.open(part,os.O_CREAT|os.O_RDWR,0o600)
    def fetch(start):
        end=min(start+chunk,f["size"])-1
        b=subprocess.check_output(["curl","-L","--fail","--retry","8","--retry-delay","5","--connect-timeout","30","--max-time","180","--silent","--show-error","-r",f"{start}-{end}",f["links"]["self"]])
        if len(b)!=end-start+1: raise IOError("Invalid range length")
        written=0
        while written<len(b): written+=os.pwrite(fd,b[written:],start+written)
        os.fsync(fd)
        return start,hashlib.sha256(b).hexdigest()
    try:
        todo=[s for s in range(0,f["size"],chunk) if str(s) not in ledger["completed"]]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures=[pool.submit(fetch,s) for s in todo]
            last=time.monotonic()
            for fut in as_completed(futures):
                start,h=fut.result(); ledger["completed"][str(start)]=h
                write_json(ledger_path,ledger)
                if time.monotonic()-last>30:
                    done=sum(min(chunk,f["size"]-int(s)) for s in ledger["completed"])
                    print(f["key"],done,"/",f["size"],"verified local chunk bytes",flush=True)
                    storage_snapshot("download_progress_"+f["key"]);last=time.monotonic()
        os.ftruncate(fd,f["size"]);os.fsync(fd)
    finally: os.close(fd)

def download(order=(4,5,2,3,1)):
    """Resume .part only for this pinned release; atomically promote after MD5 verification."""
    (DATA/'canonical_source').mkdir(parents=True,exist_ok=True)
    manifest_path = EVIDENCE/"download_manifest.json"
    old = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    entries = {x["filename"]:x for x in old}
    files = {f["key"]:f for f in release()["files"]}
    storage_snapshot("before_download")
    for exp in order:
        f = files[f"experiment{exp}.zip"]
        path = DATA/"canonical_source"/f["key"]
        part = path.with_suffix(".zip.part")
        row = entries.get(f["key"],dict(filename=f["key"],source_url=f["links"]["self"],record_url="https://zenodo.org/records/22968459",release_id=22968459,version="1.1",release_date="2026-09-25",official_bytes=f["size"],official_checksum=f["checksum"],extraction_status="not_extracted_stream_from_zip"))
        if path.exists() and verified_entry(row,f,path.stat().st_size):
            print("Already verified",path.name,flush=True); continue
        row.update(source_url=f['links']['self'],release_id=22968459,version='1.1',release_date='2026-09-25',official_bytes=f['size'],official_checksum=f['checksum'])
        row["download_started_utc"] = row.get("download_started_utc",now())
        row["status"] = "in_progress"
        entries[f["key"]]=row; write_json(manifest_path,list(entries.values()))
        if not path.exists():
            # Sparse file logical length does not measure downloaded bytes.
            allocated=part.stat().st_blocks*512 if part.exists() else 0
            needed=max(0,f["size"]-allocated)
            if shutil.disk_usage(ROOT).free < needed+2*1024**3: raise OSError("Insufficient space with 2 GiB reserve")
            print("Downloading",f["key"],needed,"remaining bytes",flush=True)
            try: segmented_transfer(part,f)
            except Exception as e:
                row.update(status="partial_resumable",download_error=str(e),local_bytes=part.stat().st_size if part.exists() else 0)
                write_json(manifest_path,list(entries.values())); raise
            sha,md5 = verify_file(part,f)
            os.replace(part,path); path.chmod(0o444)
        else: sha,md5=verify_file(path,f)
        row.update(status="verified",local_bytes=path.stat().st_size,sha256=sha,computed_md5=md5,download_completed_utc=now(),archive_readable=zipfile.is_zipfile(path))
        write_json(manifest_path,list(entries.values()))
        storage_snapshot("verified_"+path.name)
        print("Verified",path.name,sha,flush=True)

def open_archive(exp):
    f = next(f for f in release()["files"] if f["key"]==f"experiment{exp}.zip")
    path = DATA/"canonical_source"/f["key"]
    if not path.exists(): raise FileNotFoundError("Acquire and verify archive first")
    manifest=json.loads((EVIDENCE/"download_manifest.json").read_text())
    if not any(r["filename"]==path.name and verified_entry(r,f,path.stat().st_size) for r in manifest):
        raise ValueError("Unverified source refused")
    return zipfile.ZipFile(path)
