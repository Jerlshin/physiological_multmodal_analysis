# G01-R analysis freeze — record

Written 2026-10-05, immediately after the freeze commit. This file is not bound by the freeze manifest: it identifies the freeze, so it cannot be part of it. Committed separately.

## Identifiers

| Item | Value |
|---|---|
| Freeze commit | `6ba87fe6efe324ec087d1b5fb4a81e909b5ed354` (branch `main`, 2026-10-05T11:36:34+02:00) |
| Freeze tag | `g01r-freeze-v1` (annotated; tag object `71ecb20f00381115122f65a083c10e1ba9a73e99`) |
| Protocol v1.0 commit | `ef1df1b3014ccc85f5ac956bd192b6b0d39c3e34` (protocol text unchanged since) |
| Freeze manifest | `analysis_freeze/freeze_manifest.json`, SHA-256 `a2594996ac122348ffacff8a0a100f7dc035aa6848c7df23b0ca939e310f2149` |
| Derived-cache index | `analysis_freeze/derived_cache_index.json`, SHA-256 `6c96e77a43ea99afe09ab97457a80a456cfa0e1057076edc6974d0bd299b2fb8` (7,903 synchrony entries, 71 CorrCA units) |
| Configuration | `configs/g01r_protocol_v1.toml`, SHA-256 `f34f1b03b65723dc30c07f4eb0f848150cd2672877e310ab2290244627d63fff` |
| Code (aggregate over 35 bound files) | `ead83bb691b2…` (full value in the manifest, `code.sha256`) |

## Status at the freeze commit

| Check | Result |
|---|---|
| Unit tests | 101 tests, all pass (run on the clean committed tree) |
| `g01r verify-freeze` | `VERIFIED`; no uncommitted bound files |
| Validation verdict | All protocol §17.3 targets met; detection procedure: person-block permutation (fallback not triggered) |
| Derived caches | Bit-identical under the frozen code: 71/71 CorrCA units, 740/740 synchrony plans ([cache_consistency.json](../docs/research/baseline_implementation/evidence/validation/cache_consistency.json)) |
| H3 interpretation | IS-028 confirmed by the user as final (BID-026) |
| **Outcome lock** | **Active.** No `AUTHORIZATION.json`; no `outcome_access_log.jsonl`, so no real outcome has ever been read through the loader; `freeze.load_authorization` refuses; `g01r run` refuses (tested) |

## Preregistration snapshot

| Item | Value |
|---|---|
| File | `dist/g01r-freeze-v1.zip` (git-ignored; not committed) |
| SHA-256 | `4afcc4298a01a399d184a80196f5ab16e8afe1babb1295c890df52162f91a2b2` |
| Size | 3,945,482 bytes; 298 files; 9.0 MB uncompressed |
| Rebuild (byte-identical) | `git archive --format=zip --prefix=g01r-freeze-v1/ -o dist/g01r-freeze-v1.zip g01r-freeze-v1` |

**Scope.** The archive holds the code (`src/`, `tests/`, `scripts/`, `configs/`), the dependency locks, the freeze manifest and cache index, and the documentation of every project phase. The exclusions are declared in `.gitattributes` (`export-ignore`), so the archive is defined by the tag itself:

- local OS artifacts (`.DS_Store`);
- `docs/research/dataset_exploration/evidence/`, apart from `download_manifest.json` (archive checksums only). This folder holds participant-level BBBD-derived tables, including quiz outcomes; author `.mat` files; third-party code archives; and quiz materials;
- two search logs and a search-record file that contain publisher signed-access URLs.

BBBD data, signal and synchrony caches, feature tables and run results are never in the repository (git-ignored).

**Audit of the archive.**

- No `.parquet`, `.npy`, `.mat`, `.xlsx`, `.zip` or `.DS_Store` file.
- No table with participant-level outcome columns.
- No credential or signed-URL token.
- No `data/`, `results/` or authorization file.
- All 49 bound repository files are present with their manifest SHA-256, so a reviewer can check the freeze from the archive alone.

## Remaining preregistration fields (user)

1. Authors and affiliations.
2. Freeze commit: `6ba87fe6efe324ec087d1b5fb4a81e909b5ed354` (tag `g01r-freeze-v1`).
3. Deposit date.
4. Optional attachment: `g01r-freeze-v1.zip` with SHA-256 `4afcc4298a01a399d184a80196f5ab16e8afe1babb1295c890df52162f91a2b2`.

## After the preregistration DOI

```sh
cd /Users/jerlshin/FieldOfInterest/ResearchWork/NTU_research
PYTHONPATH=src .venv/bin/python -m g01r verify-freeze        # VERIFIED, no notes
PYTHONPATH=src .venv/bin/python -m g01r authorize --preregistration <DOI> --by "<name>"
git add analysis_freeze/AUTHORIZATION.json && git commit -m "Record G01-R outcome-access authorization"
PYTHONPATH=src .venv/bin/python -m g01r run --analysis H1_H2 --workers 5   # ≈ 3–4 h
git add analysis_freeze/outcome_access_log.jsonl && git commit -m "Log G01-R H1/H2 outcome access"
```

Then follow the run book in [analysis_freeze.md](../docs/research/baseline_implementation/analysis_freeze.md#run-book-after-authorization).
