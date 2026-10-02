# Storage and retention — 2026-10-02

Five read-only canonical ZIPs are retained: **26,973,110,601 bytes** (25.121 GiB). No extracted waveform tree, second canonical download or full-format waveform derivative was created. Never delete these archives merely to reclaim the small audit footprint.

## Initial, observed peak and final footprint

- Initial repository: approximately **1.4 MiB**, source bytes 0; initial shell free-space reading approximately 35 GiB. These initial readings were rounded, not exact byte measurements.
- Observed peak of tracked audit categories: **27,532,648,448 allocated bytes** (25.642 GiB), snapshot `qc_exp1_complete` at 2026-10-02T14:42:51.870643+00:00.
- Final accounted footprint: **27,530,280,960 allocated bytes** (25.640 GiB), cutoff 2026-10-02T15:32:48.113340+00:00. Final free space at that cutoff: 48,332,800,000 bytes.
- Temporary bytes deleted: **872,619**. Large artifacts deleted: **0**. Canonical bytes deleted: **0**.

| Category | Retention | Logical bytes | Allocated bytes | Files |
| --- | --- | --- | --- | --- |
| canonical_source | KEEP — canonical | 26,973,110,601 | 26,973,122,560 | 5 |
| extracted_source | none created | 0 | 0 | 0 |
| derived_reproducible | none created | 0 | 0 | 0 |
| temporary_cache | DELETE — temporary | 0 | 0 | 0 |
| final_evidence | KEEP — scientific evidence | 115,555,513 | 116,293,632 | 278 |
| environment_regenerable | REGENERABLE | 417,046,721 | 440,864,768 | 10,480 |


“Peak” is the largest observed allocated-byte snapshot, not a claim of continuously measured maximum. Sparse partial-download logical length was never equated to occupied bytes. Later accounting/validation bookkeeping changes a few small report/JSON files after the cutoff. Early snapshots counted `evidence/` only; final evidence includes report/figure/code/config bytes as well. Pre-existing research documents and unrelated OS filesystem changes are outside these task categories. Free space rose during acquisition because other filesystem state changed; no unrecorded source deletion is inferred from that change.

## Retention decisions

**KEEP — canonical:** official archives plus [release/checksum manifest](evidence/download_manifest.json). All five are verified against official MD5 and have local SHA-256. Archives remain ZIP-addressable; extracting again requires only Python `zipfile` or `unzip` into a new `extracted_source/` folder. This audit reads the ZIP directly and requires no extraction.

**KEEP — scientific evidence:** all compact manifests, validity masks, original correction intervals, source metadata/code snapshots, current and superseded checkpoints, acquisition chunk ledgers, numerical tables, figures, logs, tests and reports. [Retention manifest](evidence/retention_manifest.json) lists every artifact at least 1 MiB with bytes/category/hash. Overlapping small/medium QC tables are retained because they support independent queries/checkpoints; no full waveform is duplicated by them.

**REGENERABLE:** the isolated Python environment, recreated from `requirements-audit.lock`. There are no large derived waveform caches. The exact executed full-QC code is retained as `audit_execution_code.zip`; current postprocessing source/config has fingerprints. No large generated artifact was deleted, so the policy requiring committed generating code/config before large-artifact deletion was not invoked. Repository changes are reviewable; a Git commit is not claimed.

**DELETE — temporary:** two verified range-probe byte buffers, the redundant local HTTP-header copy and Matplotlib font cache. Before deletion, all five canonical files remained, [pre-cleanup validation](evidence/validation_pre_cleanup.json) passed, source/config existed, and downstream scientific outputs/tests were verified. Original dated HTTP headers and obsolete checkpoint history were moved/retained as evidence. Byte-exact source offsets, hashes, deletion timestamps and recreation instructions are in `retention_manifest.json`. Font cache recreation is environment-dependent; it has no scientific content.

## Reproduction and future cleanup

Run the command sequence in the [main report](README.md). `bbbd-audit verify` rehashes canonical ZIPs if independent integrity checking is required. `bbbd-audit audit` reads bounded chunks directly from archives. `python -m bbbd_audit.retention` refreshes accounting without deleting data; `--cleanup` only deletes classified small task caches after strict pre-cleanup validation. Large derived cleanup must receive a separate provenance/downstream/source audit and be logged here. If disk pressure later warrants removing extracted copies, preserve all canonical archives/checksums and extraction instructions first.
