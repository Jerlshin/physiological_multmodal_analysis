# Real-outcome authorization and first confirmatory run (H1/H2) — G01-R

Phase run 2026-10-05. Input: the committed freeze `g01r-freeze-v1` (`6ba87fe`; manifest `a2594996…`) and the user's OSF preregistration, deposited before authorization: **https://osf.io/uh397/overview**.

Scope, as instructed and as fixed by the [run book](../baseline_implementation/analysis_freeze.md#run-book-after-authorization):

1. verify the freeze;
2. authorize outcome access;
3. re-verify;
4. run step 1 (`--analysis H1_H2`) exactly as frozen;
5. interpret it under the pre-declared rules.

Run-book steps 2–5 (H3.1–H3.6, the descriptive/explanatory/diagnostic analyses and the full report) are **not** part of this phase and were not started. No model, feature, target, set or inference rule was added or changed.

**Results:** [h1h2_results.md](h1h2_results.md).

**Headline.** H1 not detected (Ŝ = 0.021, p = 0.082, 90% interval −0.033 to 0.072). Pre-declared category: bounded negative, with increments ≥ 0.10 ruled out (U₃ = 0.079) and 0.05–0.10 not ruled out. In the H2 Holm family, synchrony beyond reference-free features (H2a) and the gaze block (H2d) are detected, both below δ; EEG (H2b) and ECG (H2c) are not.

## Sequence and gate evidence

| UTC (2026-10-05) | Step | Result | Evidence |
|---|---|---|---|
| 10:47:01–10:47:09 | `verify-freeze` (full, with caches) | `VERIFIED`; no environment drift; no uncommitted bound files | [01](evidence/logs/01_verify_freeze_pre_authorization.log) |
| 10:47:25 | Unit tests on the committed tree | 101/101 OK | [02](evidence/logs/02_tests_pre_authorization.log) |
| 10:47:40 | `authorize --preregistration https://osf.io/uh397/overview --by Jerlshin` | `AUTHORIZATION.json` written (SHA-256 `0bd14a35…`); records `git_commit 5ba4f16` and manifest `a2594996…` | [03](evidence/logs/03_authorize.log), [record](../../../analysis_freeze/AUTHORIZATION.json) |
| 10:47:47 | Commit `33e61e6`, then `verify-freeze` and `load_authorization` | `VERIFIED`; authorization accepted | [04](evidence/logs/04_verify_freeze_post_authorization.log) |
| 10:48:47 | Pre-run snapshot | Environment identical to `requirements-baseline.lock`; caches 7,903 synchrony / 71 CorrCA entries; **no outcome-access log existed** | [05](evidence/logs/05_pre_run_snapshot.log), [pip freeze](evidence/pip_freeze_at_run.txt) |
| 10:49:01 | `run --analysis H1_H2 --workers 5` started (HEAD `d02e477`) | — | [stdout](evidence/logs/07_h1h2_run_stdout.log) |
| **10:49:16** | **First and only real-outcome access** | `PAS_E34_core`, exact, 259 cells, authorization `0bd14a35…` | [outcome_access_log.jsonl](../../../analysis_freeze/outcome_access_log.jsonl) |
| 17:30:48 | Run finished | `FINISHED`, exit 0, 24,098 s | [run.json](evidence/run.json) |
| 17:31:36 | `verify-freeze` after the run | `VERIFIED` (frozen cache entries intact; 12,900 new synchrony entries appended) | [06](evidence/logs/06_verify_freeze_post_run.log) |

The outcome loader re-verified the authorization and the full manifest at the moment of access. Authorization and outcome access therefore both happened only after successful verification.

## Run provenance

| Item | Value |
|---|---|
| Run ID | `20261005T104908Z_c57b28d6` (MLflow run `19e779362aeb49e7bc9ceaaa39fc017b`, experiment `g01r-confirmatory`, id 6) |
| Run store (git-ignored) | `results/runs/g01r-confirmatory/H1_H2__20261005T104908Z_c57b28d6/` |
| Copied evidence | [run.json](evidence/run.json), [params.json](evidence/params.json), [metrics.json](evidence/metrics.json), [result.json](evidence/result.json) |
| Configuration | `configs/g01r_protocol_v1.toml`, SHA-256 `f34f1b03…`, `frozen = true`, no overrides |
| Protocol | v1.0, commit `ef1df1b` |
| Code at run | Commit `d02e477`, code SHA-256 `ead83bb691b2…` (identical to the freeze aggregate). Working tree dirty **only** in `.DS_Store` (macOS Finder metadata; tracked by accident, not bound by the freeze) |
| Freeze | Tag `g01r-freeze-v1`, manifest `a2594996ac122348ffacff8a0a100f7dc035aa6848c7df23b0ca939e310f2149`, cache index `6c96e77a…` |
| Authorization | `analysis_freeze/AUTHORIZATION.json`, SHA-256 `0bd14a35f56734bb6c151f46c9fff9d23a532abac37348bccb6acd2bcacf3067` |
| Environment | Python 3.14.5; numpy 2.5.3, scipy 1.18.1, pandas 3.0.6, pyarrow 25.0.1, mlflow-skinny 3.16.1; `pip freeze` identical to the lock |
| Data | BBBD v1.1 (Zenodo 22968459); download manifest SHA-256 in `run.json` |
| Set / split identity | Set `8a682fc06fcb4d16…`; split `f62f7ae362c148c1…` (identical to the pre-outcome dry runs) |
| Seeds | Base seed 20261004; label-addressed streams |
| Detection procedure | Permutation (from `validation_verdict.json`; fallback not triggered) |
| Artifact SHA-256 | Listed in [run_digest.json](evidence/tables/run_digest.json) (`result.json` `7b08e12e…`, `predictions.parquet` `a8af78cb…`, permutation nulls, folds, penalties, cells) |
| Warnings / failures | None. MLflow mirror errors: none. Runtime 6.7 h versus the run book's 3–4 h estimate (see results §10) |

Participant-level predictions and outcomes stay in the git-ignored run store; only aggregates are committed.

## Evidence folder

| Path | Content |
|---|---|
| `evidence/logs/` | Gate logs 01–06 and the run's stdout (07) |
| `evidence/{run,params,metrics,result}.json` | Copies of the tracked run record |
| `evidence/tables/` | `h1.csv`, `h2_holm.csv`, `comparisons.csv`, `per_experiment.csv`, `per_video.csv`, `intervals_from_h1_fits.csv`, `run_diagnostics_models.csv`, `clipped_at_zero_by_cell.txt`, `run_digest.json` |
| `evidence/g01r_report/` | Output of the frozen `g01r report` collator for this run (H1, H2, models, per-video, per-experiment, derived) |
| `evidence/summarize_h1h2.py` | Outcome-free tabulation of a finished run (copies from `result.json`; derives only numerical diagnostics) |

## Commands executed (in order)

```sh
cd /Users/jerlshin/FieldOfInterest/ResearchWork/NTU_research
PYTHONPATH=src .venv/bin/python -m g01r verify-freeze
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests
PYTHONPATH=src .venv/bin/python -m g01r authorize --preregistration "https://osf.io/uh397/overview" --by "Jerlshin"
git add analysis_freeze/AUTHORIZATION.json && git commit -m "Record G01-R outcome-access authorization"
PYTHONPATH=src .venv/bin/python -m g01r verify-freeze
PYTHONPATH=src .venv/bin/python -c "from g01r.config import load_config; from g01r.freeze import load_authorization; load_authorization(load_config())"
git commit  # pre-run logs and environment snapshot, so the run records a clean tree apart from .DS_Store
PYTHONPATH=src .venv/bin/python -m g01r run --analysis H1_H2 --workers 5
PYTHONPATH=src .venv/bin/python docs/research/confirmatory_h1h2/evidence/summarize_h1h2.py \
    results/runs/g01r-confirmatory/H1_H2__20261005T104908Z_c57b28d6 docs/research/confirmatory_h1h2/evidence/tables
PYTHONPATH=src .venv/bin/python -m g01r verify-freeze
PYTHONPATH=src .venv/bin/python -m g01r report --experiment g01r-confirmatory --out results/report_h1h2 \
    --title "G01-R confirmatory H1/H2 baseline (first real-outcome run)"
git add analysis_freeze/outcome_access_log.jsonl docs/research/confirmatory_h1h2/evidence && git commit
```

Two read-only helpers were also run; neither reads outcomes:

- a progress probe during the run, which counted cached nested-CV synchrony plans;
- a lookup of `Q_eeg_16hz_excess` for the cells whose predictions were clipped at 0.

## Next step (not started)

> **Update 2026-10-07.** Run-book steps 2–5 were completed in the [next phase](../preregistered_completion/README.md). This H1/H2 record is unchanged.

Per [preregistration §13 and §15](../baseline_implementation/preregistration.md#13-reporting-commitments-regardless-of-result), every registered analysis is completed and reported whatever the H1 result. The next frozen steps are run-book steps 2–4, then step 5. See the recommendation in [h1h2_results.md](h1h2_results.md) and the decision log (CHR-009).
