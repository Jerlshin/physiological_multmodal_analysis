# Analysis freeze — what is frozen, how it is enforced, the run book

2026-10-05. The protocol requires a time-stamped preregistration before any physiology–outcome computation (§16; readiness-verdict condition 1). This phase makes that condition **machine-enforced**: real outcomes are unreachable until the user authorizes access after the deposit.

## What is frozen

| Element | Frozen as | Bound by |
|---|---|---|
| Analysis contract | [protocol.md](../experimental_design/protocol.md) v1.0, commit `ef1df1b`, plus the estimand and evaluation-contract documents | SHA-256 in `freeze_manifest.json` → `documents` |
| Operational clarifications | [implementation_spec.md](implementation_spec.md) v1.1, IS-001…IS-029 | `documents` |
| Every numeric constant | `configs/g01r_protocol_v1.toml` (SHA-256 `f34f1b03…`); edits to protocol invariants are refused at load time | `documents`; recorded in every run |
| Analysis sets | 10 frozen sets plus 3 derived subsets, reproduced cell-for-cell from the design-phase manifest | `evidence/population/*` |
| Feature dictionary and code | `src/g01r` (every file), plus the reused `bbbd_audit/io.py`, `qc.py` and the design simulation generator | `code` (per-file SHA-256 and aggregate) |
| Analysis plan as code | `g01r/registry.py`: 17 entries (H1_H2, H3_1…H3_7, D_state, D_BC, D_CAS, D_E5, D_transport, D_E1, X_explanatory, S_identity_probe), of which H3_7 and D_state are derived from H1_H2 | `code`, `registry` |
| Feature tables | `data/derived/g01r/features/{processed,raw}/exposure_features.parquet` (outcome-blind) | `features` |
| Signal caches | EEG, HR, gaze and pupil caches for both routes | `signal_caches` (tree hash over per-file SHA-256) |
| Derived synchrony caches | Every `syn_cache` and `corrca_stats` entry present at the freeze, reproduced bit for bit by the frozen code ([cache_consistency.json](evidence/validation/cache_consistency.json)) | `derived_caches` → `analysis_freeze/derived_cache_index.json` (append-only, IS-029) |
| QC and validation evidence | `evidence/feature_qc/feature_qc.json`, `evidence/validation/{v1,v2}_summary.csv`, `validation_verdict.json` (fixes the detection procedure), `cache_consistency.json` | `evidence` |
| Data | The five verified archives (SHA-256/MD5 from the download manifest) | `data` |
| Seeds | Base seed 20261004; label-addressed streams | `seeds`, config |
| Environment | Python 3.14.5; numpy 2.5.3, scipy 1.18.1, pandas 3.0.6, pyarrow 25.0.1, mlflow-skinny 3.16.1; exact lock `requirements-baseline.lock` | Lock file in `documents`; installed versions in `environment` (recorded; `verify-freeze` prints any difference, which is not a verification criterion) |

## Enforcement

1. **Single door.** `outcomes.load_real_outcomes` is the only code path to real outcomes. A static test forbids outcome sources anywhere else in `src/g01r`.
2. **Authorization checks.** The loader requires an `Authorization` that `freeze.load_authorization` returns only if:
   - `analysis_freeze/AUTHORIZATION.json` exists with an author, a UTC time, the preregistration identifier, a statement, the manifest SHA-256 and the git commit;
   - the manifest SHA-256 matches;
   - `verify_manifest` finds no difference in documents, evidence, features, registry, code, signal caches, frozen derived-cache entries or data.

   The loader repeats these checks itself at every access instead of trusting the object it is given.
3. **Committed freeze.** `g01r authorize` refuses unless every bound repository file is tracked and unmodified in git, and records the commit, so the authorization always points at a commit that contains the frozen state.
4. **Frozen configuration only.** `g01r run` refuses overrides; only the frozen configuration can produce confirmatory runs. Smoke and dry runs record `frozen=false` and their overrides.
5. **Audit trail.** Each real-outcome access is appended to `analysis_freeze/outcome_access_log.jsonl`. The authorization record is append-only.

## Run book after authorization

| Step | Command | Expected wall time (5 workers) | Output |
|---|---|---|---|
| 0 | `python -m g01r verify-freeze` | 1 min | `VERIFIED` |
| 1 | `python -m g01r run --analysis H1_H2` | ≈ 3–4 h (nested CV dominates; ~35% of its synchrony plans are cached and verified) | H1 decision, H2 Holm family, every regime-A model, state and cell-weighted intervals, shortcut diagnostics (i, iii) |
| 2 | `python -m g01r run --analysis H3_1_partial,H3_6_gpa` | < 1 h (same splits as step 1; synchrony cached) | H3.1, H3.6 |
| 3 | `python -m g01r run --analysis H3_2_eye30,H3_2_eye70,H3_3_four,H3_4_raw,H3_5_alpha` | ≈ 20–30 h (5 cold nested CVs) | H3.2–H3.5 |
| 4 | `python -m g01r run --analysis D_BC,D_CAS,D_E5,D_transport,D_E1,X_explanatory,S_identity_probe` | 3–4 h | Descriptive, explanatory and diagnostic analyses |
| 5 | `python -m g01r report --experiment g01r-confirmatory --out results/report` | 1 s | Tables (CSV plus markdown) |

H3.7 (cell-weighted) and the state interval come from step 1 (`derived` registry entries).

The order follows protocol §17.5: H1, then H2, then H3, then the descriptive analyses. It is an execution order only: every step is completed and reported whatever the H1 result ([preregistration §13, §15](preregistration.md#15-execution-order)). Interpretation follows the pre-declared [decision table](../experimental_design/estimand_and_hypotheses.md#6-pre-declared-interpretation-of-h1). The H1 permutation p-value, point estimate, futility bound and nested-CV interval are all produced by step 1.
