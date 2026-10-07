# Completion of the preregistered G01-R analysis plan (run-book steps 2–5)

Phase run 2026-10-06 to 2026-10-07. Input: the frozen, authorized state of the [H1/H2 phase](../confirmatory_h1h2/README.md):

- freeze `g01r-freeze-v1`, manifest `a2594996…`;
- authorization `0bd14a35…`;
- OSF preregistration https://osf.io/uh397/overview.

**Scope, as instructed.** Execute the remaining registry analyses exactly as frozen, in run-book order:

| Run-book step | Analyses |
|---|---|
| 2 | H3.1, H3.6 |
| 3 | H3.2–H3.5 |
| 4 | D_BC, D_CAS, D_E5, D_transport, D_E1, X_explanatory, S_identity_probe |
| 5 | Collated report |

Then document them and write one integrated report for the preregistered phase.

**What was not done.** H1/H2 were not modified, re-run or re-interpreted. No model, feature, set, threshold, exclusion, target, resampling scheme, metric or inference rule was added or changed. No learner was removed, and no post hoc or new-method analysis was run.

**Documents:**

- [results_steps2_5.md](results_steps2_5.md): per-analysis records, each with case flow, model, estimate, interval, decision, δ/2δ, multiplicity, reference access, quality/missingness, numerical warnings, and relation to H1/H2.
- [final_report.md](final_report.md): the integrated final report for the preregistered phase, including the empirical bottleneck and the ranked recommendation.

**Headline.**

- **All 17 registry analyses are complete.**
- H1 remains a **bounded negative**. All eight H3 robustness estimates keep its sign and stay below δ (0.009–0.021).
- **Synchrony's increment over reference-free features reappears on new content** with an unlabelled half-cohort reference (regime C beats B in 8 of 8 videos). It does not carry across protocols, and the synchrony model's skill over the baseline stays below δ (C 0.020 [−0.014, 0.045]).
- **Reference-free features hurt on new content** (B −0.025 [−0.049, −0.006]).
- **Gaze robustness to eye-quality policy is not testable** with the prespecified analyses. The full-model increment halves under the strictest eye QC.
- **No support for EEG or ECG.**
- **About 82% of the held-out signal beyond content is nonsignal (covariates and quality).**

## Sequence and gate evidence

| UTC | Step | Result | Evidence |
|---|---|---|---|
| 2026-10-06 12:31:44 | `verify-freeze` | `VERIFIED`; manifest, authorization, config and cache-index hashes as frozen; access log 1 line | [01](evidence/logs/01_verify_freeze_pre_step2.log) |
| 12:31:50 | Unit tests | 100 run, all pass. The one skip is by design: `test_no_authorization_record_exists_in_repository` applies only before authorization | [02](evidence/logs/02_tests_pre_step2.log) |
| — | Commit `d737ac1` (pre-run gate logs) | Clean tree apart from `.DS_Store` | git |
| 12:32:15–12:33:35 | **Step 2** `run --analysis H3_1_partial,H3_6_gpa` | Exit 0; 2 outcome accesses | [03](evidence/logs/03_step2_H3_1_H3_6_stdout.log) |
| 12:34:20 | `verify-freeze` | `VERIFIED` | [04](evidence/logs/04_verify_freeze_post_step2.log) |
| 12:34:32 → 2026-10-07 16:56:19 | **Step 3** `run --analysis H3_2_eye30,H3_2_eye70,H3_3_four,H3_4_raw,H3_5_alpha` | Exit 0; 5 outcome accesses; 28.4 h (host sleep about 5 h, see notes) | [05](evidence/logs/05_step3_H3_2_to_H3_5_stdout.log), [10](evidence/logs/10_operational_sleep_events.log) |
| 2026-10-07 16:56:37 | `verify-freeze` (automatic gate before step 4) | `VERIFIED` | [06](evidence/logs/06_verify_freeze_post_step3.log) |
| 16:56:44 → 18:38:25 | **Step 4** `run --analysis D_BC,D_CAS,D_E5,D_transport,D_E1,X_explanatory,S_identity_probe` | Exit 0; 7 outcome accesses (transport reads E4 and E5; the identity probe reads none) | [07](evidence/logs/07_step4_descriptive_stdout.log) |
| 18:38:25 | `verify-freeze` | `VERIFIED` (frozen cache entries intact; new entries appended, IS-029) | [08](evidence/logs/08_verify_freeze_post_step4.log) |
| 18:39:04 | **Step 5** `report --experiment g01r-confirmatory --out results/report` | Exit 0; 15 analyses collated | [09](evidence/logs/09_step5_report.log), [copy](evidence/g01r_report/report.md) |

**Outcome-access log.** [outcome_access_log.jsonl](../../../analysis_freeze/outcome_access_log.jsonl) now has 15 entries:

- 1 from H1/H2;
- 14 in this phase, every one under authorization `0bd14a35…` and after the loader re-verified the manifest.

| UTC | Set | Outcome | Cells | Analysis |
|---|---|---|---|---|
| 2026-10-06 12:32:27 | PAS_E34_core | partial | 259 | H3.1 |
| 12:33:03 | PAS_E34_core | exact | 259 | H3.6 |
| 12:34:46 | PAS_E34_core_eye30 | exact | 223 | H3.2 (0.30) |
| 18:08:30 | PAS_E34_core_eye70 | exact | 265 | H3.2 (0.70) |
| 2026-10-07 03:16:51 | PAS_E34_four | exact | 216 | H3.3 |
| 08:44:09 | PAS_E34_core | exact | 259 | H3.4 |
| 13:06:54 | PAS_E34_core_alpha30 | exact | 234 | H3.5 |
| 16:56:56 | PAS_E34_core | exact | 259 | D_BC |
| 17:03:06 | CAS_E34 | exact | 302 | D_CAS |
| 17:12:32 | E5_core | exact | 128 | D_E5 |
| 18:25:26 | E4_core | exact | 111 | D_transport (source/target) |
| 18:25:32 | E5_core | exact | 128 | D_transport (source/target) |
| 18:25:37 | E1_gaze | exact | 121 | D_E1 |
| 18:38:23 | PAS_E34_core | exact | 259 | X_explanatory |

## Run provenance

| Analysis | Run ID | Start → end (UTC) | Elapsed | `result.json` SHA-256 | MLflow run |
|---|---|---|---|---|---|
| H3_1_partial | `20261006T123221Z_a27a0b62` | 10-06 12:32:21 → 12:32:57 | 36 s | `18acb19d90a6…` | `f9d4ff4129aa…` |
| H3_6_gpa | `20261006T123257Z_d1e38f11` | 10-06 12:32:57 → 12:33:35 | 38 s | `a079cb369d1a…` | `f1f8ab1bf121…` |
| H3_2_eye30 | `20261006T123439Z_5a0263c2` | 10-06 12:34:39 → 18:08:24 | 5.6 h | `341c03dc9eda…` | `433a6cad666a…` |
| H3_2_eye70 | `20261006T180824Z_85517ad2` | 10-06 18:08:24 → 10-07 03:16:45 | 9.1 h | `18de04d3f9ef…` | `84361aedfc57…` |
| H3_3_four | `20261007T031645Z_20f139c0` | 10-07 03:16:45 → 08:44:04 | 5.5 h | `5824f906ff1c…` | `d53d81ffed85…` |
| H3_4_raw | `20261007T084404Z_9117498b` | 10-07 08:44:04 → 13:06:48 | 4.4 h | `fe98bebd1b46…` | `e626b84e88de…` |
| H3_5_alpha | `20261007T130648Z_ea387334` | 10-07 13:06:48 → 16:56:18 | 3.8 h | `7b9a61dd00bb…` | `487791262c73…` |
| D_BC | `20261007T165649Z_c945a3df` | 10-07 16:56:49 → 17:03:01 | 370 s | `aa0c205f7e69…` | `b44cfbbeaaf0…` |
| D_CAS | `20261007T170301Z_6dbbf219` | 10-07 17:03:01 → 17:12:26 | 565 s | `c82e11b1fb55…` | `50950f177c5e…` |
| D_E5 | `20261007T171226Z_99ee1196` | 10-07 17:12:26 → 18:25:20 | 1.2 h | `e55200f1da18…` | `305f781a2049…` |
| D_transport | `20261007T182520Z_c9759030` | 10-07 18:25:20 → 18:25:32 | 11 s | `9d59ca4ca640…` | `244d34980384…` |
| D_E1 | `20261007T182532Z_8e41b75d` | 10-07 18:25:32 → 18:38:17 | 766 s | `e7e63c1131e6…` | `0364bb251d91…` |
| X_explanatory | `20261007T183817Z_904fe9c0` | 10-07 18:38:17 → 18:38:23 | 6 s | `4373119cdf18…` | `558608a67b73…` |
| S_identity_probe | `20261007T183823Z_12d883ba` | 10-07 18:38:23 → 18:38:24 | 1 s | `f77c56ca6d46…` | `c545220fee26…` |

Full SHA-256 of every artifact of every run (predictions, folds, penalties, cells, B/C predictions) is in [run_digest_steps2_4.json](evidence/tables/run_digest_steps2_4.json). The phase's own files are hashed in [SHA256SUMS](evidence/SHA256SUMS).

| Item | Value (identical for all 14 runs) |
|---|---|
| Status | `FINISHED`, exit 0; MLflow errors: none |
| Configuration | `configs/g01r_protocol_v1.toml`, SHA-256 `f34f1b03…`, `frozen = true`, overrides `{}` |
| Code | Commit `d737ac1`, code SHA-256 `ead83bb691b2…`: the freeze aggregate, identical to the H1/H2 run |
| Working tree at launch | Dirty only in files not bound by the freeze: `.DS_Store`, this phase's logs and summarizer, copied run records, and the append-only `outcome_access_log.jsonl`. Recorded in each `run.json` |
| Environment | Python 3.14.5; numpy 2.5.3, scipy 1.18.1, pandas 3.0.6, pyarrow 25.0.1, mlflow-skinny 3.16.1; `pip freeze` identical to `requirements-baseline.lock` ([snapshot](evidence/pip_freeze_at_completion.txt)) |
| Data | BBBD v1.1; download manifest SHA-256 `a867e07c…` |
| Seeds | Base seed 20261004; label-addressed streams. Split identities of H3.1, H3.4 and H3.6 equal H1's (`f62f7ae3…`) |
| Workers | 5, as in the run book. The worker count does not enter any random stream |
| Run store (git-ignored) | `results/runs/g01r-confirmatory/<analysis>__<run id>/` |

## Evidence folder

| Path | Content |
|---|---|
| `evidence/logs/` | Gate logs 01–02, 04, 06, 08; step stdout logs 03, 05, 07; step 5 log 09; host sleep events 10 |
| `evidence/runs/<analysis>/` | Copies of `run.json`, `params.json`, `metrics.json`, `result.json` for all 14 runs |
| `evidence/tables/` | Outcome-free tabulations: H3 summary, regime-A records, per-experiment, per-video, B/C, CAS, transport, explanatory, identity probe, case flow by set, quality/missingness by set, run diagnostics, clipped-cell lists, run digest |
| `evidence/g01r_report/` | Output of the frozen `g01r report` collator (step 5) |
| `evidence/summarize_steps2_4.py` | Outcome-free tabulation script (never calls the outcome loader) |
| `evidence/pip_freeze_at_completion.txt` | Environment snapshot |
| `evidence/SHA256SUMS` | SHA-256 of every file in this phase folder (except itself) |

Participant-level predictions and outcomes stay in the git-ignored run store; only aggregates are committed.

## Commands executed (in order)

```sh
cd /Users/jerlshin/FieldOfInterest/ResearchWork/NTU_research
PYTHONPATH=src .venv/bin/python -m g01r verify-freeze
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests
git commit   # pre-run gate logs (d737ac1)
PYTHONPATH=src .venv/bin/python -m g01r run --analysis H3_1_partial,H3_6_gpa                              # step 2
PYTHONPATH=src .venv/bin/python -m g01r verify-freeze
PYTHONPATH=src .venv/bin/python -m g01r run --analysis H3_2_eye30,H3_2_eye70,H3_3_four,H3_4_raw,H3_5_alpha  # step 3
caffeinate -i -s -m -w <pid of the step-3 shell>      # added 2026-10-07T02:51Z after the host slept
# gated chain, inside caffeinate: wait for step 3 -> require exit=0 -> verify-freeze must print VERIFIED -> step 4 -> verify-freeze
PYTHONPATH=src .venv/bin/python -m g01r verify-freeze
PYTHONPATH=src .venv/bin/python -m g01r run --analysis D_BC,D_CAS,D_E5,D_transport,D_E1,X_explanatory,S_identity_probe  # step 4
PYTHONPATH=src .venv/bin/python -m g01r verify-freeze
PYTHONPATH=src .venv/bin/python -m g01r report --experiment g01r-confirmatory --out results/report         # step 5
PYTHONPATH=src .venv/bin/python docs/research/preregistered_completion/evidence/summarize_steps2_4.py \
    results/runs/g01r-confirmatory docs/research/preregistered_completion/evidence/tables
```

Read-only helpers that never read outcomes:

- progress probes that counted synchrony-cache files;
- `pmset -g log` and `top`;
- the GPA-missingness count from the outcome-free covariate table;
- a lookup of the cells clipped at 1 in D_E1 (from the outcome-free `predictions.parquet` and `cells.parquet`).

## Deviations and operational notes

- **Scientific deviations: none.** Every analysis ran from the frozen registry with the frozen configuration. No step was skipped, and the run-book order (step 2 → 3 → 4 → 5) was kept: step 4 started only after step 3 exited cleanly and the freeze re-verified.
- **Host sleep:**
  - **What happened.** The Mac's system-sleep setting (1 min idle) suspended the H3.2-eye70 run from about 21:45Z to 02:49Z.
  - **Why results are unaffected.** Results are deterministic functions of the frozen inputs and label-addressed seeds; the run simply resumed.
  - **Mitigation.** `caffeinate` was attached for the rest of the phase.
  - This explains eye70's 9.1 h versus about 5 h for the other cold H3 runs.
- **Wall time.**
  - Step 3 took 28.4 h, within the run book's 20–30 h estimate despite the sleep.
  - Step 4 took 1.7 h, against an estimated 3–4 h.
  - Memory, not CPU, was the constraint on this 16 GB host, so the run-book worker count (5) was kept.
- **Launch state.** Steps 3–4 were launched with uncommitted, unbound phase files present (logs, summarizer). `verify-freeze` was unaffected, and each `run.json` records the exact dirty file list.
