# Dataset Exploration & Empirical Readiness Report

**Gate follow-up — 2026-10-02:** Current behavioral eligibility excludes Exp.2: 581 memory outcomes overall; multimodal QC ceiling 94 people / 324 observations / 8 videos. The full-release counts below remain forensic release-key/QC evidence. OQ-06 is empirically narrowed but still blocking; the full transition is not ready. [Evidence and verdict](gate_closure.md).

Audit date: **2026-10-02**. Selected source: **BBBD v1.1, Zenodo record 22968459, released 2026-09-25**. All five archives acquired and checksum-verified; all relevant continuous streams received dataset-wide lightweight QC. No predictive model, architecture search, performance optimization, final paper question or final split was developed.

The result is a queryable, reproducible release audit with a remaining **blocking preprocessing-provenance gate (OQ-06)**. The archive/scoring/intersection questions are substantially resolved; native timing, original execution logs and historical published-input lineage remain unavailable. Passing basic QC is a provisional numerical screen, not final scientific certification.

## Evidence and report index

- [Download/version](download_and_version_audit.md), [archive inventory](archive_manifest.md), [canonical manifest](dataset_manifest.md), [quiz integrity](quiz_integrity.md).
- [Modality intersections](modality_coverage.md), [all-signal QC](signal_quality.md), [EEG/16 Hz](eeg_quality.md), [ECG/HRV](ecg_quality.md), [eye/pupil](eye_quality.md), [respiration/auxiliary streams](respiration_quality.md).
- [Preprocessing trace](preprocessing_provenance.md), [timing](synchronization_audit.md), [missingness/selection](missingness.md), [outcomes/traits](outcome_characterization.md), [leakage/independence](leakage_and_independence.md), [EXPLORATORY multimodal structure](exploratory_multimodal_structure.md).
- [Candidate feasibility](research_feasibility.md), [P0 disposition](open_questions_resolved.md), [remaining gates](open_questions_remaining.md), [storage/retention](storage_and_retention.md), [machine-readable evidence](evidence/README.md).

## Answers to the readiness questions

1. **Correct release? Yes.** All five official file sizes/MD5s match; local SHA-256s and timestamps are retained. Embedded 1.0.0 naming is stale metadata, explicitly recorded. Canonical total **26,973,110,601 bytes**.
2. **What is on disk?** Five immutable ZIPs containing 41,251 members, small source-metadata snapshots, 16,038 physical continuous-file manifest rows, compact validity masks, channel/peak/QC tables, seven scientific figures and reproducible modules/tests. No second full signal tree or converted full-dataset copy exists.
3. **Usable independent units?** 178 experiment-qualified participants, 11 canonical videos, 1474 design-expected exposures and 736 unambiguous phenotype memory outcomes. Scientific usable counts depend on modality, chronology and QC; the exact table follows. Cross-experiment unique-human identity is not independently certified.

| experiment | people | design_exposures | videos | release_key_memory_pairs |
| --- | --- | --- | --- | --- |
| 1 | 27 | 270 | 5 | 135 |
| 2 | 31 | 310 | 5 | 155 |
| 3 | 29 | 348 | 6 | 173 |
| 4 | 43 | 258 | 6 | 129 |
| 5 | 48 | 288 | 3 | 144 |

4. **Exact modality intersections?** Full presence/QC/outcome counts and exact released-grid valid durations are in [modality_coverage.md](modality_coverage.md) and [CSV](evidence/modality_intersections.csv). Eye requires gaze+pupil, no raw fallback is disguised as processed data, and repeated outcomes are not counted as new tests.
5. **Correctly linkable outcomes?** Keyed video memory outcomes reconstruct; 1–2 also include domain scores. Exp.3 sub-01/stim03 is quarantined. Extra phenotype IDs in 1–3 remain unmatched. Partial credit in 3–5 omits wrong-choice penalties; 4–5 exact-set correctness is a different variable. Original answer-order logs remain unavailable.
6. **Strongest experiments?** **OUR INFERENCE:** Exp.3 is the strongest remaining first-view multimodal quiz cohort; Exp.4 supports the single-exposure tested subset and Exp.5 bundled repeat/preview/incentive transport. Exp.2 remains a signal/condition cohort while its behavioral targets are quarantined. Exp.1 offers eye-only context. No experiment is selected for a paper.
7. **Important QC problems?** Eye correction dominates attrition; some expected raw/processed streams are absent; integer EEG export loses original NaN semantics; EOG anatomical numbering and voltage scaling are not fully verified. Per-record reasons, absent-file placeholders and flat-run evidence remain queryable.
8. **16 Hz severity?** Quantified for every EEG channel/record and both representations, with 3/6/10/20 dB flags and relative power. Peaks are localized rather than universal; processed/raw differences exist. No automatic rejection or neural/artifact attribution is made from a frequency peak alone.
9. **Eye interpolation?** Exact masks are preserved. Means, maxima and longest gaps by experiment/modality appear below. Some corrected spans last minutes; complete processed files are not equivalent to wholly observed samples.

| experiment | modality | files | mean_correction | median_correction | max_correction | max_gap_seconds | basic_QC_flags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | gaze | 263 | 0.217 | 0.148 | 0.904 | 189.219 | 35 |
| 1 | pupil | 263 | 0.307 | 0.224 | 0.995 | 144.039 | 39 |
| 2 | gaze | 297 | 0.241 | 0.189 | 0.910 | 122.742 | 33 |
| 2 | pupil | 297 | 0.344 | 0.260 | 0.987 | 100.633 | 60 |
| 3 | gaze | 323 | 0.235 | 0.198 | 0.872 | 173.688 | 42 |
| 3 | pupil | 323 | 0.368 | 0.281 | 0.987 | 174.477 | 75 |
| 4 | gaze | 247 | 0.193 | 0.143 | 0.882 | 229.836 | 17 |
| 4 | pupil | 247 | 0.337 | 0.213 | 0.980 | 230.469 | 56 |
| 5 | gaze | 285 | 0.205 | 0.138 | 0.932 | 108.508 | 28 |
| 5 | pupil | 285 | 0.354 | 0.192 | 0.988 | 108.695 | 72 |

10. **Synchronization?** Boundary/sample-count agreement and padding are empirically checked. Synthetic array-boundary events contain no native clock-fit residuals. Whole-video aggregation is safest; multi-second windows are conditional exploratory analyses; sub-second/directional/lag claims are insufficiently verified.
11. **Leakage channels?** Participant/content repetition, adjacent windows, global preprocessing, ISC/CorrCA/PCA references, scaling/imputation, outcome duplication, quality/protocol shortcuts and post-exposure information are formally registered. Future controls must precede windowing/reference fitting.
12. **True experimental units?** People and canonical videos, with nested viewing blocks and crossed person/video exposures; repeated quizzes/targets are not independent windows. Experiment-qualified identifiers do not prove different humans across experiments. Only 11 videos limits content-level uncertainty regardless of hours.
13. **Empirically feasible questions?** Whole-video incremental information, observed-failure reliability, reduced-sensor measurement and explicit protocol transport remain conditional MEDIUM candidates; release measurement/reproducibility auditing is HIGH for demonstrable definitions, conditional for original-paper replication. Exact counts/evidence are in the [feasibility matrix](research_feasibility.md).
14. **Abandon/reframe?** Abandon current-release millisecond/directional/item-timed C05 claims until timing/item alignment exists. Reframe generic fusion/quiz novelty around incremental independent information; reward around bundled transport; defer architecture-led C06. Long-term gain and diagnostic outcomes are unsupported.
15. **Unresolved before formulation?** OQ-06's actual derivative configuration/scaling is blocking. Surplus IDs/duplicate item are safely quarantined but not explained; original response/published-input lineage, unique-human overlap, allocation, native timing and weighted trait coding remain bounded open questions.
16. **Another dataset later?** **OUR INFERENCE:** likely useful for external validation of transport, robustness or content-independent physiological relationships. Antecedent BBBD subsets are not external validation. A second dataset needs compatible measurement semantics and separate outcome definitions; no indiscriminate pooling is proposed.
17. **Retained/deleted?** Canonical ZIPs, checksum ledgers, small/medium scientific evidence and generating code/config are retained. No full waveform derivative was generated or deleted. Verified temporary probes/font caches were deleted after evidence validation; superseded checkpoints were retained as history. Exact categories, bytes and recreation commands are in [retention report](storage_and_retention.md).

## Reproduction

The executed environment uses Python 3.14 on macOS; [locked dependencies](../../../requirements-audit.lock) record the exact library versions. Create an isolated environment and install the package to expose the `bbbd-audit` entry point, then run from repository root:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-audit.lock
.venv/bin/python -m pip install --no-deps -e .
```

```sh
PYTHONPATH=src .venv/bin/python -m bbbd_audit.cli inventory
PYTHONPATH=src .venv/bin/python -m bbbd_audit.cli download
PYTHONPATH=src .venv/bin/python -m bbbd_audit.quiz
PYTHONPATH=src .venv/bin/python -m bbbd_audit.cli audit
PYTHONPATH=src .venv/bin/python -m bbbd_audit.cli summarize
PYTHONPATH=src .venv/bin/python -m bbbd_audit.structure
PYTHONPATH=src .venv/bin/python -m bbbd_audit.regional
MPLCONFIGDIR=data/bbbd/temporary_cache/matplotlib PYTHONPATH=src .venv/bin/python -m bbbd_audit.figures
MPLCONFIGDIR=data/bbbd/temporary_cache/matplotlib PYTHONPATH=src .venv/bin/python -m bbbd_audit.deep
PYTHONPATH=src .venv/bin/python -m bbbd_audit.report
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
PYTHONPATH=src .venv/bin/python -m bbbd_audit.cli validate
```

`inventory` uses remote ranges only when a canonical ZIP is absent; verified downloads are skipped. `audit` checkpoints per experiment and automatically invalidates a cache when QC code, input tables or config changes. The exact source of the full signal pass is retained in [audit_execution_code.zip](evidence/audit_execution_code.zip); later metadata and breath-peak semantic corrections are deterministically applied by `summarize` without another full signal pass. The current source/config is fingerprinted by `validate`. Source archives remain untouched. [Evidence index](evidence/README.md) documents schema, validity semantics and limitations. All exploratory statistics use descriptive summaries, no p-value search or predictive fitting. No confirmatory test set was declared or evaluated; future hypotheses formed using this audit need a locked/untouched evaluation or external data.

## NEXT_STAGE_RECOMMENDATION

**Gate not fully closed:** resolve the remaining OQ-06 EEG/eye execution, native-lineage and physical-calibration provenance before the full multimodal transition. Exp.2 behavioral pooling is now disallowed, with its targets quarantined; original response mapping remains needed only to reinstate those targets. The revised multimodal behavioral ceiling is 94 people / 324 observations / 8 videos. [Follow-up findings and reproduction](gate_closure.md). No final question or model is selected.
