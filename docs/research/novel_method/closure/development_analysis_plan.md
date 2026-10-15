# Development analysis plan (DAP-1) — what Stage 2 computes, fixed before any development outcome exists

Written 2026-10-14 in the closure phase. It operationalizes:

- plan §23 Stage 2;
- the development selection rule (§12.4);
- the baseline ladder (§16) and ablations (§17);
- the stop rule (§20.5).

It uses the confirmatory design frozen in [design_config.json](design_config.json). Stage 2 is **exploratory**: nothing here is a confirmatory test, and the lock (E4 + E5) is touched only after Stage 3.

The code is `cairn.stage2` (numpy side) and `cairn.stage2.run_ml` (ML baselines, `.venv-cairn-ml`). The same code ran end to end on synthetic outcomes in the closure phase (`python -m cairn dryrun`; [evidence/dryrun/](evidence/dryrun/)).

## 1. Preconditions (the gate enforces 1–3)

1. Human anchor set frozen (G-AN), with `ANCHOR_FREEZE.json` and its companion.
2. Rule R-J re-simulation passed on the frozen anchors with the frozen design (`rj_record.json`).
3. CAIRN freeze record (`analysis_freeze_cairn/FREEZE_RECORD.json`, stage `development`) written after your commit. Your `AUTHORIZATION.json` must name scope `development` and bind the record.
4. The tests and `python -m cairn verify` pass at the frozen commit.

## 2. Data

- **Development set:** E3 (6 videos) + E1 on Light bulbs, Internet and Birth rate. That is 55 learners / 229 cells / 9 videos.
- **Outcomes:** exact-set item correctness through `cairn.gate.load_item_outcomes("development")`. One logged access per runner invocation: the numpy run and the ML run are two logged accesses. Outcomes are mapped to incidence rows by `cairn.item_keys.verify_item_table`.
- **No other cohort is read.** E4/E5 item outcomes stay locked.

## 3. Steps

| Step | Specification |
|---|---|
| 1. Manifest | Written before any fit: code, environment lock, inputs (frozen anchor table), design configuration hash, seeds, outcome-access mode |
| 2. Kernel selection | Over `design.KERNEL_GRID` (12 configurations: lag ∈ {−5, 0, 5} s × padding ∈ {0, 5, 10, 20} s). Score: repetition-level CV S_item of the primary (R = 10 × 5-fold, learner-grouped, experiment-stratified). **Rule (plan §12.4):** the simplest kernel whose mean lies within one standard error of the best mean. Simplicity order: padding first, then \|lag\|; hard span (0, 0) is simplest. The selected kernel is frozen for the lock |
| 3. Development tests (exploratory) | Primary at the selected kernel:<br>• confirmatory statistic: LR T1/T2/T2c, B = 999;<br>• fallback statistic: CV T1/T2, B = 999 |
| 4. Usefulness | CV S_item and ΔAUC_wp against IRT-M2 (R = 10), with the nested-CV 90% interval |
| 5. Stop rule (plan §20.5, unchanged) | Go **iff** all three hold:<br>• CV T2 p < .10;<br>• CV ΔAUC_wp ≥ .01;<br>• the Stage-0 construct check (AUC .89, met).<br>Otherwise stop: report the development results as exploratory negatives and keep E4/E5 untouched |
| 6. Numpy ladder | B0 video mean; IRT-0; IRT-M2; IRT-whole; B9 Lallé; CAIRN parametrizations P6 / PT / P0 at d\*; the raw (no-detrend) form |
| 7. ML ladder (`run_ml`, R = 3) | B3 (elastic net, random forest, LightGBM, CatBoost, GPBoost, TabPFN v2, each stacked into IRT-M2), item-level LightGBM residual, item-level GPBoost with crossed random effects, B4a MantisV2 video-level, B4b gated-attention MIL, B4b text-conditioned item attention (MLP and linear); ablation A4: MantisV2 / Mantis-8M anchored front end, B7 TCN encoder |
| 8. Ablations (descriptive) | A1 anchor source (true; relocated and circular-shift nulls; learned text-conditioned attention); A2 kernel (step 2 table); A4 representation (handcrafted vs FM vs TCN); A5 person path (IRT-whole vs anchored); A6 modality (validity only, gaze only, **gaze given validity** = the R-I NH4 attribution test); A9 item category (λ by R/C for the 1-df forms) |
| 9. Strongest competing baseline | For NH3: `stage2.select_strongest`, the non-CAIRN model with the highest development S_item among IRT-whole, B9 and the ML baselines. The anchored FM/TCN front ends are excluded: they are CAIRN with another representation. Fixed for the lock |
| 10. Outputs | `development_report.json`, `development_ml_report.json`, `selections.json` (kernel, go/stop, strongest baseline), all hashed into the lock freeze |

## 4. What development may and may not change

**May (pre-declared selections):**

- the kernel (step 2);
- the strongest competing baseline (step 9);
- the go / stop decision.

**May not:**

- the confirmatory statistic, parametrization or detrend degree d\*;
- the cohorts or the closed-testing structure;
- B, α or the useful thresholds (S_item ≥ .01 and ΔAUC_wp ≥ .02);
- the stop rule.

Any of those changes would need a new decision, a new simulation (rule R-J) and a new freeze before the lock. They would be reported as deviations.

**Optimism disclosure.** Kernel selection and the stop rule use the same development outcomes, so the development estimates are optimistic. This is why development is exploratory and the lock is the only confirmatory test.
