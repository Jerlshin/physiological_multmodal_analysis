"""Account for retained artifacts and remove only verified small task caches."""
import argparse
import json
import shutil
from pathlib import Path
from .io import ROOT, DATA, EVIDENCE, now, storage_snapshot, write_json
from .validate import sha

def run(cleanup=False):
    log_path=EVIDENCE/'retention_manifest.json'
    old=json.loads(log_path.read_text()) if log_path.exists() else {}
    deletions=old.get('deletions',[]);moves=old.get('moves',[])
    if cleanup:
        check=json.loads((EVIDENCE/'validation_pre_cleanup.json').read_text())
        if check['status']!='passed':raise ValueError('Verified evidence required before cleanup')
        storage_snapshot('before_verified_small_cache_cleanup')
        # These ledgers are evidence, not duplicate source data or disposable cache.
        for p in sorted((DATA/'canonical_source').glob('*.chunks.json')):
            dest=EVIDENCE/'download_chunks'/p.name;dest.parent.mkdir(parents=True,exist_ok=True)
            moves.append(dict(from_path=str(p.relative_to(ROOT)),to_path=str(dest.relative_to(ROOT)),bytes=p.stat().st_size,reason='retain local chunk verification ledger as scientific acquisition evidence'))
            shutil.move(p,dest)
        cache=DATA/'temporary_cache'
        for p in sorted(cache.glob('audit_*json')):
            dest=EVIDENCE/'superseded_checkpoints'/p.name;dest.parent.mkdir(parents=True,exist_ok=True)
            moves.append(dict(from_path=str(p.relative_to(ROOT)),to_path=str(dest.relative_to(ROOT)),bytes=p.stat().st_size,reason='retain interim checkpoint history; current exact masks/boundaries supersede it'))
            shutil.move(p,dest)
        headers=cache/'range_headers.txt'
        if headers.exists():
            dest=EVIDENCE/'http_headers/experiment1_initial_range.txt';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(headers,dest)
        for p in sorted(cache.rglob('*')):
            if not p.is_file():continue
            if p.is_symlink() or p.stat().st_size>1024**2:raise ValueError('Automatic cleanup restricted to small, local task caches')
            info=dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,allocated_bytes=p.stat().st_blocks*512,sha256=sha(p),deleted_utc=now(),retention='DELETE — temporary')
            if p.name=='experiment1_tail.bin':
                with (DATA/'canonical_source/experiment1.zip').open('rb') as f:f.seek(893203383);expected=f.read(65536)
                if p.read_bytes()!=expected:raise ValueError('Tail probe differs from canonical source')
                info['recreate']='Read experiment1.zip at byte offset 893203383 for 65536 bytes; no network needed.'
            elif p.name=='exp4_phenotype_region.bin':
                with (DATA/'canonical_source/experiment4.zip').open('rb') as f:f.seek(2653875113);expected=f.read(58188)
                if p.read_bytes()!=expected:raise ValueError('Metadata probe differs from canonical source')
                info['recreate']='Read experiment4.zip at byte offset 2653875113 for 58188 bytes; original metadata members also retained.'
            elif p.name=='range_headers.txt':info['recreate']='Copy evidence/http_headers/experiment1_initial_range.txt; dated original HTTP response retained.'
            elif p.parent.name=='matplotlib':info['recreate']='Re-run the figures module with MPLCONFIGDIR pointing to temporary_cache/matplotlib; font cache is environment-dependent and has no scientific result.'
            else:raise ValueError('Unclassified temporary artifact: '+str(p))
            deletions.append(info);p.unlink()
        for p in sorted(cache.rglob('*'),reverse=True):
            if p.is_dir() and not any(p.iterdir()):p.rmdir()
    current=storage_snapshot('final_retention_accounting')
    history=[json.loads(s) for s in (EVIDENCE/'disk_usage.jsonl').read_text().splitlines()]
    measured=[h for h in history if 'categories' in h]
    peak=max(measured,key=lambda h:sum(v['allocated_bytes'] for v in h['categories'].values()))
    downloads=json.loads((EVIDENCE/'download_manifest.json').read_text())
    hashes={r['filename']:r['sha256'] for r in downloads}
    large=[]
    for category,root in [('canonical_source',DATA/'canonical_source'),('final_evidence',EVIDENCE.parent),('derived_reproducible',DATA/'derived_reproducible')]:
        if not root.exists():continue
        for p in sorted(root.rglob('*')):
            if p.is_file() and p.stat().st_size>=1024**2:
                large.append(dict(path=str(p.relative_to(ROOT)),category=category,retention='KEEP — canonical' if category=='canonical_source' else 'KEEP — scientific evidence' if category=='final_evidence' else 'REGENERABLE',bytes=p.stat().st_size,allocated_bytes=p.stat().st_blocks*512,sha256=hashes[p.name] if category=='canonical_source' else sha(p)))
    result=dict(accounted_utc=current['time_utc'],initial=history[0],final_snapshot=current,observed_peak_snapshot=peak,large_artifacts=large,moves=moves,deletions=deletions,bytes_deleted=sum(d['bytes'] for d in deletions),canonical_bytes=sum(r['local_bytes'] for r in downloads),large_artifacts_deleted=False,environment='REGENERABLE: recreate .venv with requirements-audit.lock; no waveform data in it.',footprint_definition='Task categories include canonical data, all audit evidence/reports/figures/source/config and .venv. Pre-existing research files and unrelated filesystem use are excluded. Snapshot total is exact at its stated cutoff; later accounting/validation bookkeeping changes a few small files.',peak_limit='Observed peak from repeated allocated-byte snapshots, not continuous filesystem monitoring; earlier final_evidence category counted only evidence/ and therefore slightly understates historical report/code overhead.')
    write_json(log_path,result)
    categories=current['categories'];table='| Category | Retention | Logical bytes | Allocated bytes | Files |\n| --- | --- | --- | --- | --- |\n'
    labels={'canonical_source':'KEEP — canonical','extracted_source':'none created','derived_reproducible':'none created','temporary_cache':'DELETE — temporary','final_evidence':'KEEP — scientific evidence','environment_regenerable':'REGENERABLE'}
    for key,v in categories.items():table+=f"| {key} | {labels[key]} | {v['logical_bytes']:,} | {v['allocated_bytes']:,} | {v['files']:,} |\n"
    total=sum(v['allocated_bytes'] for v in categories.values());peak_total=sum(v['allocated_bytes'] for v in peak['categories'].values())
    report=f'''# Storage and retention — 2026-10-02

Five read-only canonical ZIPs are retained: **{result['canonical_bytes']:,} bytes** ({result['canonical_bytes']/1024**3:.3f} GiB). No extracted waveform tree, second canonical download or full-format waveform derivative was created. Never delete these archives merely to reclaim the small audit footprint.

## Initial, observed peak and final footprint

- Initial repository: approximately **1.4 MiB**, source bytes 0; initial shell free-space reading approximately 35 GiB. These initial readings were rounded, not exact byte measurements.
- Observed peak of tracked audit categories: **{peak_total:,} allocated bytes** ({peak_total/1024**3:.3f} GiB), snapshot `{peak['label']}` at {peak['time_utc']}.
- Final accounted footprint: **{total:,} allocated bytes** ({total/1024**3:.3f} GiB), cutoff {current['time_utc']}. Final free space at that cutoff: {current['free_bytes']:,} bytes.
- Temporary bytes deleted: **{result['bytes_deleted']:,}**. Large artifacts deleted: **0**. Canonical bytes deleted: **0**.

{table}

“Peak” is the largest observed allocated-byte snapshot, not a claim of continuously measured maximum. Sparse partial-download logical length was never equated to occupied bytes. Later accounting/validation bookkeeping changes a few small report/JSON files after the cutoff. Early snapshots counted `evidence/` only; final evidence includes report/figure/code/config bytes as well. Pre-existing research documents and unrelated OS filesystem changes are outside these task categories. Free space rose during acquisition because other filesystem state changed; no unrecorded source deletion is inferred from that change.

## Retention decisions

**KEEP — canonical:** official archives plus [release/checksum manifest](evidence/download_manifest.json). All five are verified against official MD5 and have local SHA-256. Archives remain ZIP-addressable; extracting again requires only Python `zipfile` or `unzip` into a new `extracted_source/` folder. This audit reads the ZIP directly and requires no extraction.

**KEEP — scientific evidence:** all compact manifests, validity masks, original correction intervals, source metadata/code snapshots, current and superseded checkpoints, acquisition chunk ledgers, numerical tables, figures, logs, tests and reports. [Retention manifest](evidence/retention_manifest.json) lists every artifact at least 1 MiB with bytes/category/hash. Overlapping small/medium QC tables are retained because they support independent queries/checkpoints; no full waveform is duplicated by them.

**REGENERABLE:** the isolated Python environment, recreated from `requirements-audit.lock`. There are no large derived waveform caches. The exact executed full-QC code is retained as `audit_execution_code.zip`; current postprocessing source/config has fingerprints. No large generated artifact was deleted, so the policy requiring committed generating code/config before large-artifact deletion was not invoked. Repository changes are reviewable; a Git commit is not claimed.

**DELETE — temporary:** two verified range-probe byte buffers, the redundant local HTTP-header copy and Matplotlib font cache. Before deletion, all five canonical files remained, [pre-cleanup validation](evidence/validation_pre_cleanup.json) passed, source/config existed, and downstream scientific outputs/tests were verified. Original dated HTTP headers and obsolete checkpoint history were moved/retained as evidence. Byte-exact source offsets, hashes, deletion timestamps and recreation instructions are in `retention_manifest.json`. Font cache recreation is environment-dependent; it has no scientific content.

## Reproduction and future cleanup

Run the command sequence in the [main report](README.md). `bbbd-audit verify` rehashes canonical ZIPs if independent integrity checking is required. `bbbd-audit audit` reads bounded chunks directly from archives. `python -m bbbd_audit.retention` refreshes accounting without deleting data; `--cleanup` only deletes classified small task caches after strict pre-cleanup validation. Large derived cleanup must receive a separate provenance/downstream/source audit and be logged here. If disk pressure later warrants removing extracted copies, preserve all canonical archives/checksums and extraction instructions first.
'''
    (EVIDENCE.parent/'storage_and_retention.md').write_text(report)
    print('Canonical retained',result['canonical_bytes'],'bytes; temporary deleted',result['bytes_deleted'],'bytes',flush=True)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--cleanup',action='store_true');args=parser.parse_args();run(args.cleanup)
