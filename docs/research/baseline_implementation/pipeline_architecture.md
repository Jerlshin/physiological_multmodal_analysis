# Pipeline architecture — `src/g01r`

The production pipeline for the [frozen protocol](../experimental_design/protocol.md). The audit package `src/bbbd_audit` is reused unchanged for verified archive access and for the audit's own QC estimators. No other library dependency was added to the scientific stack: numpy, scipy, pandas and pyarrow are unchanged. MLflow-skinny with SQLite was added for tracking only.

## Data flow

```
configs/g01r_protocol_v1.toml  (frozen constants, SHA-256 in every run)
        │
population.py   audited bookkeeping (column-whitelisted) ──► 10 frozen sets, verified cell-for-cell
        │                                                     against the design-phase manifest
signals.py      verified ZIP members ──► video-trimmed EEG (+ zero-code mask), gaze, pupil, intervals,
        │                                 saccades, R-peaks; raw exports for the sensitivity route
features/       reference_free.py (RF1–RF6, RF-P)   quality.py (Q, audit estimator)   covariates.py (C)
        │       raw_route.py (prespecified raw EEG cleaning)
        │       extract.py ──► exposure_features.parquet + per-exposure signal cache (outcome-blind)
        │       synchrony.py ──► CorrCA (exact pairwise sufficient statistics) + reference-mean ISC
references.py   ReferencePlan per split: regime A (leave-self-out), C (cross-fitted halves),
        │       transport (source cohort), explanatory (full LSO) — leakage assertions on construction
design.py       blocks C | Q | RF_* | SYN_* | NOISE (+ indicators); SYN computed per plan, cached by plan hash
splits.py       person-grouped experiment-stratified folds; LOVO x person folds; label-addressed seeds
pipeline.py     protocol §8 order inside every split; runners for A, B/C, transport, CAS policy
models.py       ridge only; 13-value grid x n_train; person-grouped inner 5-fold CV; clip [0, 1]
metrics.py      person-balanced / cell-weighted skill, ΔRMSE/ΔMAE (items), calibration, state,
        │       within-content, per-video / per-experiment, skill ÷ reliable share
inference.py    person-block Freedman–Lane permutation; nested CV (Bates 2024); corrected-t futility;
        │       Holm; two-way bootstrap; declared fallback; H1 decision table
registry.py     every prespecified analysis as data (sets, regimes, models, tests, intervals)
analysis.py     executes registry entries in parallel; outcomes only via OutcomeSource
outcomes.py     ONLY module that may read outcomes; real outcomes require a verified authorization
freeze.py       freeze manifest (hash binding) + authorization gate
tracking.py     file run store (source of truth) mirrored to MLflow (SQLite)
provenance.py   git state, code hash, environment, data release identity
validate.py     V1 production re-simulation; V2 real-feature null calibration
feature_qc.py   outcome-blind feature QC and the 15 % REVISE trigger
report.py       collates tracked runs into the prespecified tables
cli.py          `python -m g01r <command>`
```

## Outcome firewall

1. **One door.** `outcomes.py` is the only module that names an outcome column or outcome table. A static test enforces this (`test_only_outcomes_module_names_outcome_sources`).
2. **Whitelisted reads.** Other reads of audit tables that also contain outcomes use explicit column whitelists, which are tested.
3. **Authorization gate.** `load_real_outcomes` raises `OutcomeAccessDenied` unless it receives a verified `Authorization`. An Authorization exists only when both of these hold:
   - `analysis_freeze/AUTHORIZATION.json` (written by the user, after the preregistration deposit) references the SHA-256 of `freeze_manifest.json`;
   - that manifest still verifies against the working tree: code, config, documents, dependency lock, evidence, feature tables, signal caches, the frozen synchrony/CorrCA cache entries (append-only) and data archives.

   The loader re-checks both conditions itself at every access. `authorize` also refuses unless every bound file is committed, and records the commit. Every real-outcome access is appended to `analysis_freeze/outcome_access_log.jsonl`.
4. **Training-only outcomes.** `Pipeline.fit_split` receives training outcomes only. Test outcomes are used afterwards, for scoring. A test changes test labels and asserts that predictions are unchanged.
5. **No outcomes during development.** Every validation and dry run uses `OutcomeSource("synthetic")`: draws from the design-phase outcome-only psychometric parameters on the real incidence.

## Leakage controls (evaluation contract §4) → implementation → test

| Rule | Implementation | Test(s) |
|---|---|---|
| 1. Everything is fitted inside the training split | `impute_train_mean`, `ridge_path` (training mean/SD), `choose_lambda` (inner CV on training), `content_offsets(y_train)`, CorrCA on `plan.corrca_fit`, SYN references from the plan | `test_imputation_uses_training_rows_only`, `test_content_offsets_A_and_B`, `test_regime_A`, `test_corrca_recovers_shared_component_and_respects_fit_scope` |
| 2. CorrCA fit scope | Regime A: `corrca_fit = train`. Regime C: training cells only, so never the held-out video. Transport: source cohort | `test_regime_A`, `test_regime_C` (no held-out video in the fit), `test_transport` |
| 3. Leave-self-out and test references | `reference_correlations` subtracts the target's own row. Plans assert that no target shares a person with its reference and that the reference watched the same content | `test_reference_correlation_leaves_self_out`, `test_reference_mean_uses_valid_people…`, plan `check()` |
| 4. A test person's other cells are never used | Person-grouped folds; `fit_split` asserts no person overlap; regime-C training references are training people only | `test_split_rejects_person_overlap`, `test_bc_splits_hold_out_person_and_canonical_video`, `test_regime_C` |
| 5. No outcome-derived quantity enters features or Q | Outcome firewall; feature tables contain no outcome columns | `test_only_outcomes_module…`, `test_no_outcome_columns`, `test_whitelists_contain_no_outcome_columns` |
| 6. The E5 first view is never paired with the E5 quiz | Tested exposure = E5 session 2 repeat (`population.TESTED`) | `test_reproduces_frozen_manifest_and_counts` |
| 7. No step fits across the release | Extraction is strictly per exposure; every cross-person statistic (CorrCA, references, content effects, standardization) is computed per split | Architecture; the fit-scope tests above |
| 8. Pupil and raw routes rerun everything | Separate registry entries (`H3_3_four`, `H3_4_raw`) run the full runner with their own provider/route | Registry |
| 9. Frozen thresholds, sets, features, grid, seeds | TOML with invariant checks (edits are refused); freeze manifest hash binding | `test_protocol_constants`, `test_edited_frozen_value_is_refused`, `FreezeGate` tests |

## Reproducibility guarantees

- **Determinism.** Every random draw is label-addressed (`rng.py`). All analyses on a set share folds and permutations. EEG projections are computed per plan in float64, so synchrony features are bit-identical across batching and parallelism; verified on real data.
- **Split identity.** Recorded as the SHA-256 of the fold arrays. **Set identity** is the SHA-256 of the cell keys.
- **Per-run records.** Each run records:
  - the config SHA-256 and any overrides, with `frozen=False` whenever overrides exist;
  - the protocol commit;
  - git HEAD and dirty files;
  - the code SHA-256 over every source file;
  - environment versions;
  - archive SHA-256s;
  - the outcome source.
- **Artifacts per regime-A run:** per-repetition predictions for every model, cells, outer folds, permutation null distributions, selected penalties and `result.json`. These are enough to rebuild every table and figure, and to run later ablations, without refitting.

## Compute profile (measured, 10-core laptop, 16 GB RAM)

| Step | Cost |
|---|---|
| Feature extraction (581 exposures processed + 259 raw) | 35 s (7 workers) |
| CorrCA sufficient statistics per set/route | 6–10 s, then memory-mapped |
| SYN for one split (all 4 blocks, 259 cells) | ≈1.5 s; batches of 10 splits share one EEG pass |
| Ridge fit with inner CV (one model, one split) | ≈0.9 ms |
| H1 permutation test (999 × 100 paired refits) | ≈90 s |
| Regime A point estimate (R = 50, 11 models) + 5 permutation tests (B = 999) | ≈ 2 min with cached SYN (5 workers; measured) |
| Nested CV, 200 repetitions × 100 splits (SYN recomputed per split) | Measured 50–75 synchrony plans/min with 5 workers → ≈ 4.5–6.5 h wall per cold interval; minutes when cached |

Memory: synchrony workers use ≈1.2 GB each, so at most 5 run in parallel on 16 GB. Simulation workers (fixed features) are light, so 9 run in parallel.
