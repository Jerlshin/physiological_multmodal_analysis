# Readiness verdict — Baseline Implementation & Analysis Freeze

2026-10-05.

> **Update — freeze finalization (2026-10-05).** The freeze and preregistration package were reviewed and finalized after this verdict; the freeze manifest was rebuilt (no scientific change). The current verdict, the changes and the exact next steps are in [freeze_finalization.md](freeze_finalization.md). Values below are updated where they changed.

## Verdict: **READY FOR PREREGISTRATION / ANALYSIS FREEZE**

The G01-R pipeline is implemented exactly as the [frozen protocol](../experimental_design/protocol.md) specifies:

- operational gaps are closed by [IS-001…IS-029](implementation_spec.md);
- it was validated before any outcome access;
- it is bound by a hash manifest that the outcome loader re-verifies.

**No real quiz outcome has been read, inspected or modelled. No physiology–outcome association has been computed.**

## 1. What has been implemented and validated

| Requirement | Implementation | Validation |
|---|---|---|
| Eligibility and case flow | `population.py`, an independent re-implementation with outcome-free column whitelists | Reproduces all 10 frozen sets cell for cell and the case-flow table (asserted at every run) |
| Participant/content grouping and splits | `splits.py`: person-grouped, experiment-stratified folds; LOVO × person folds; regime-C half splits; label-addressed seeds | No person or video overlap; every cell tested once per repetition; deterministic |
| Feature interfaces and sensor pipelines | `signals.py` (verified ZIPs, video trimming, digital zero codes); `features/` (RF1–RF6, RF-P, Q, C, raw route) | 23 synthetic-signal tests: valid-sample rules, 16 Hz exclusion, Welch equal to scipy, RR rules, saccade intervals, missing rule. Q equals the audit tables exactly |
| Reference-access rules | `references.py`: regime A leave-self-out, regime C cross-fitted halves, transport, explanatory | Plan assertions at construction and tests: no self in the reference, training-only references, CorrCA fit scope, held-out video never in the filters |
| Synchrony | `features/synchrony.py`: exact pairwise CorrCA statistics, reference-mean ISC on samples valid in both | Hand-computed reference correlations; planted-component recovery; fit-scope invariance; bit-identical under batching |
| Prespecified baseline families | `models.py` (M0–M5, M-EEG/ECG/gaze, M5+pupil, M5_B, E1, shortcut controls); ridge only, frozen grid, person-grouped inner CV | Closed-form ridge test; training-only imputation; test-label invariance |
| Metrics | `metrics.py`: person-balanced and cell-weighted skill, ΔRMSE/ΔMAE in items, calibration, state, within-content, per-video and per-experiment, ÷ reliable share | Known-value tests |
| Inference | `inference.py`: person-block Freedman–Lane, nested CV, corrected-t futility, Holm, two-way bootstrap, declared fallback, H1 decision table | **V1** production re-simulation, **V2** real-feature calibration (below); unit tests |
| Deterministic configuration | `configs/g01r_protocol_v1.toml` with invariant checks; label-addressed RNG | Edited frozen values are refused; overrides are flagged `frozen=false` |
| Logging and provenance | `provenance.py`, `tracking.py`: git, code hash, config hash, data archives, environment, set and split identity, outcome source | Tracking tests (file store and MLflow mirror) |
| Experiment tracking | MLflow 3.16 (SQLite) mirroring the append-only file run store | Every pipeline, validation and smoke run is tracked |
| Result artifacts | Per run: predictions for every model and repetition, folds, permutation nulls, penalties, `result.json`; `report.py` builds the prespecified tables | End-to-end smoke dry run of all 15 executable registry entries on synthetic outcomes, plus a full-scale frozen-configuration dry run of H1_H2 (see below) |
| Tests | 101 tests in total (29 inherited + 72 new) | All pass |

**Inference validation before outcomes (protocol §17.3):**

| Check | Result | Target |
|---|---|---|
| V1 false detection (null, 300 datasets) | 0.060 (MC SE 0.014) | ≤ 0.07 ✓ |
| V1 power at 2δ (true skill 0.108) | 0.973 | ≥ 0.80 ✓ |
| V1 futility error at 0.108 | 0.050 (boundary) | ≤ 0.05 ✓ |
| V1 reproduction of the design phase | 0.060 / 0.050 / 0.937 / coverage 0.88–0.91 vs 0.063 / 0.043 / 0.91 / 0.86–0.90 | Within MC error ✓ |
| V1 on the final code | Bit-identical (4 datasets) | ✓ |
| V2 real features, pure null | 0.030 (200 datasets) | ≤ 0.07 |
| V2 real features, nuisance null | 0.065 (200 datasets; MC SE 0.017) | ≤ 0.07 |
| V2 planted signal (sanity) | detection 0.92 at skill ≈ 0.10 | — |
| Feature QC trigger (PAS-core learners lost) | 0% | ≤ 15% ✓ |

## 2. What is now frozen

See [analysis_freeze.md](analysis_freeze.md) and `analysis_freeze/freeze_manifest.json` (SHA-256 `a2594996ac122348ffacff8a0a100f7dc035aa6848c7df23b0ca939e310f2149`, rebuilt in the freeze finalization). The following are bound by hash:

- the protocol and its companion documents;
- the implementation specification and the configuration (SHA-256 `f34f1b03…`);
- every production source file, including the analysis registry (17 entries: 15 executable, 2 derived from H1_H2);
- the population ledger;
- both outcome-blind feature tables and the ≈7 GB signal caches;
- the synchrony and CorrCA cache entries present at the freeze (append-only), verified bit-identical under the frozen code;
- the dependency lock `requirements-baseline.lock`;
- the feature QC report;
- the V1/V2 summaries and the validation verdict, which fixes the detection procedure to `person-block permutation (fallback not triggered)`;
- the data archives;
- the base seed 20261004.

## 3. What still requires your explicit authorization

1. **Commit the freeze to git.** This is local; I have not committed. The commit hash time-stamps the analysis freeze.
2. **Deposit the preregistration.** For example on OSF, from [preregistration.md](preregistration.md), completing only its deposit-time fields (authors, the freeze commit, the date). This is an external action.
3. **Write the authorization record.** `python -m g01r authorize --preregistration <DOI> --by <name>`. Only this unlocks real outcomes. It refuses unless the freeze is committed.
4. **Optional actions, each needing separate authorization:**
   - send the OQ-06 author query;
   - download John 2025 for the external ocular replication.

## 4. The exact first baseline execution step after authorization

```sh
cd /Users/jerlshin/FieldOfInterest/ResearchWork/NTU_research
PYTHONPATH=src .venv/bin/python -m g01r verify-freeze      # must print VERIFIED
PYTHONPATH=src .venv/bin/python -m g01r run --analysis H1_H2 --workers 5
```

This runs only the prespecified simple baselines (M0–M5, the single-modality models and the shortcut controls) on PAS-core in regime A, with the frozen configuration. It produces, in one tracked run (`results/runs/g01r-confirmatory/`, mirrored to MLflow):

- the H1 permutation p-value (B = 999, 10 paired repetitions);
- the person-balanced skill (R = 50);
- the futility bound U₃;
- the nested-CV 90% interval (200 repetitions);
- the H1 decision category;
- the Holm-adjusted H2a–d;
- the cell-weighted (H3.7) and state intervals;
- the shortcut diagnostics (i) and (iii).

**Expected wall time: ≈ 3–4 h with 5 workers.** The nested CV dominates.

- **Already validated end to end.** This command ran end to end at production settings on synthetic outcomes, apart from 20 nested repetitions instead of 200 (see the [validation report](validation_report.md#end-to-end-run-of-the-first-confirmatory-step-synthetic-outcomes)).
- **Cache reuse.** About 35% of the outcome-free synchrony plans it needs are already cached.
- **Remaining analyses.** The H3 and descriptive analyses follow the run book in [analysis_freeze.md](analysis_freeze.md).

## Live triggers carried forward (unchanged from the design phase)

- **REVISE the inference** if a production false detection exceeds 0.07 for both the permutation and the bootstrap. Not fired.
- **REVISE the population** if feature-level QC loses more than 15% of PAS-core learners. Not fired: 0%.
- **REVISE the framing** if a newly found paper estimates the same crossed incremental quantity. Open (M05 residual risk).
- **STOP the processed route** if an author or provenance statement reveals a pooled or label-using upstream step. Open (OQ-06 bounded).

## Residual risks stated before outcome access

- **Futility error.** The production rate (0.050) sits at its target, so a "≥ 0.10 ruled out" conclusion carries about 5% error, as declared.
- **EEG ISC and ocular activity.** EEG ISC is coupled to gaze behaviour. H2b is read as "EEG-recorded synchrony", not as non-ocular neural information.
- **Inflated point estimates.** An extreme quality value can inflate point estimates through baseline under-regularization. The matched-noise control is reported next to H1, and the decision requires p ≤ 0.05.
- **Compute.** The full confirmatory registry needs ≈ 25–35 h wall on this laptop, measured at 50–75 synchrony plans/min with 5 workers. It is dominated by nested CV with per-split synchrony on the five H3 sets that have their own features. The order H1 → H2 → H3 → descriptive allows pausing between stages; every stage is still completed and reported, whatever the H1 result.
