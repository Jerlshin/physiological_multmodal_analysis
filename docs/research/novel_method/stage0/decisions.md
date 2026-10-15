# Stage-0 decision and inference log

2026-10-13. Local IDs: **S0-D** for decisions and **S0-I** for facts and inferences. The global entries are D076–D083 in the [decision log](../../decision_log.md) and INF-101–INF-111 in the [inference register](../../inference_register.md).

## Decisions

| ID | Decision | Evidence / reason | Revisit trigger |
|---|---|---|---|
| S0-D01 | Execute Stage 0 on the user's instruction. No outcome access, no supervised CAIRN fit, no Stage 2. Commits are user actions | User instruction; JRP-010 precedent | — |
| S0-D02 | Fetch the 12 public stimulus sources (11 videos; Enzymes has two) and their captions, for annotation and alignment only. Keep them git-ignored (`data/stimuli/`), never redistributed. A current `yt-dlp` runs in a scratch virtualenv; the frozen `.venv` is untouched | Plan §11.2 step 1; user authorization in the Stage-0 instruction | Rights questions |
| S0-D03 | Stage-0 **design** analyses use development and label-free exposures only. They exclude E4 session 2 and E5 session 2 and do not use Stars/Immune anchors. Timeline alignment may pool all viewings: it estimates a stimulus property, uses no outcome and makes no method choice | Protects the locked cohorts from non-outcome information leakage into design | — |
| S0-D04 | G-TL ("agreement within ±2 s across ≥ 2 independent experiments") cannot be applied to Work-energy, Capacitors and Planets, which were shown only in E3. **Substitute:** both random learner halves *and* both sessions must reproduce the mapping. This is a declared deviation | Plan §11.2 | A second cohort for these videos |
| S0-D05 | Timeline path model: monotone (removal-only) Viterbi with an edit penalty of 0.5. Decision rule fixed before anchoring. Independent validators added (cut-locked saccades; pupillary light response). Validator rule **v2** adopted after v1's defects were identified: inadmissible vetoes, circularity, multiplicity, edit-point uncertainty. v1 is kept in the outputs | [timeline_audit.md §5](timeline_audit.md#5-audit-history-what-changed-after-looking) | — |
| S0-D06 | Immune is G-TL PARTIAL. Items whose evidence lies after source 215 s (items 2, 7, 8, 9, 10) are not anchorable. Enzymes is PASS, with the mismatch explained (two concatenated sources) | Timeline audit §4 | New evidence on the Immune edit |
| S0-D07 | Anchors from R1 (lexical) and R2 (LLM-assisted) are **provisional and never frozen**. G-AN needs two humans. The protocol, package and gate/freeze code are ready. Provisional anchors may be used only for outcome-free Stage-1 work | Plan §11.2 [R13]; user instruction | Human annotations delivered |
| S0-D08 | *Anchorable* = localized (one span ≤ 45 s) ∧ fully shown ∧ every span second passes G-TL ∧ key not inconsistent with the narration | Anchor audit §2 | G-AN adjudication |
| S0-D09 | Modality roles: gaze alignment, gaze dynamics and validity → **primary**; pupil → **ablation**; head, EEG, ECG/HR → **diagnostic only**; `speed` and respiration → **rejected** | [signal_feasibility.md §8](signal_feasibility.md#8-modality-decisions-for-stage-1) | Development selection rule (pupil); a new EEG reliability result |
| S0-D10 | **CAIRN-linear is the pre-specified primary candidate.** A learned encoder (linear; TCN in Stage 2) is ablation A4 | Encoder did not beat handcrafted channels outcome-free (construct .80 vs .89; reconstruction .26 vs .30) [R4] | — |
| S0-D11 | Drop regime B (peer-free, reference-distilled) from the primary claims | Distillation R² < 0 for held-out learners | Video-frame (saliency) reference, C4 |
| S0-D12 | NH4 uses **long** (≥ 1 s) invalid episodes in the anchor window | 7× more frequent under distraction; short loss is blink-scale | — |
| S0-D13 | Novelty: N-a is withdrawn as "first content-anchored item-level prediction" (Lallé 2025). N-a′ (psychometric identification) and **N-d (falsification, now central)** are kept; N-b′ and N-e are narrowed. New baseline **B9** (Lallé-style pooled window classifier) | [literature_closeout.md §4](literature_closeout.md#4-novelty-verdict) | Lallé paper text; new prior art |
| S0-D14 | T2 permutes **distinct anchor moments** within a video, not items. Items sharing a span keep their sharing | 87 development items occupy 59 distinct moments | — |
| S0-D15 | Stage-1 pass criteria are fixed. If locked power at δ_item is < .80, the lock design is revised **before** Stage 2, by a declared option | [stage1_spec.md §1.7](stage1_spec.md#17-pass-criteria) | Simulation results |
| S0-D16 | **Verdict: GO to Stage 1.** Stage 2 additionally needs G-AN, a passing simulation, a CAIRN freeze and explicit user authorization | [reassessment.md §12](reassessment.md#12-verdict) | — |

## Facts and inferences

| ID | Class | Statement | Evidence |
|---|---|---|---|
| S0-I01 | VERIFIED FACT (outcome-free) | The Enzymes stimulus is `AAZ03aScPr8` [5.0–144.9 s] followed by `lkRZKqDdwzU` [50.0–177.9 s], switching at recording 140 s (CI 140–140). Four other videos are trimmed at the end only, Mosquitoes at both ends, Immune mid-video | `evidence/timeline_table.csv` |
| S0-I02 | VERIFIED FACT (code-level) | Lallé 2025 predicts per-item retention ("QCM" Answer) from gaze features in 10–30 s windows ending at, or spanning, author-specified item content times. CV: StratifiedGroupKFold by participant (8 folds). Item identity (`Sc_id`) is dropped; there is no item-difficulty term and no randomization null. `PriorKnowledge` is a person-level fairness attribute | Lallé repository code (hashes in `evidence/literature_sources.json`) |
| S0-I03 | EXTERNAL FINDING (FT) | EyeBench OneStop comprehension, test AUROC: text-only RoBERTa 61.1 vs RoBERTEye 61.9, MAG-Eye 62.9 | EyeBench `auroc.csv` |
| S0-I04 | PROVISIONAL FACT (machine anchors) | 105/131 items anchorable (development 87/107); 59 distinct development moments; locked primary 26 items, about 19 moments | `evidence/anchors_provisional_summary.json` |
| S0-I05 | VERIFIED FACT (outcome-free) | Anchored moment terms: item share 0–52% by channel; person × item share 40–89%; within-viewing split-half reliability ≤ .68–.80 (unsmoothed channels); attentive ↔ distracted test–retest ≈ 0 | `evidence/signal/B_anchored_reliability.csv` |
| S0-I06 | VERIFIED FACT (outcome-free) | Attentive vs distracted viewing: held-out-learner AUC .89 (reference-relative); rho5 dz −1.28. Long invalid episodes 0.23 vs 1.60 per minute | `evidence/signal/signal_feasibility_summary.json` |
| S0-I07 | VERIFIED FACT (outcome-free) | Video identity: item-centred moment terms .11 (chance .11); person-centred .16–.18; whole-video reference-relative means .58 | idem |
| S0-I08 | VERIFIED FACT (outcome-free) | CorrCA windowed EEG-ISC (held-out half): component split reliability SB .06; reference-split SB .26; R² on ocular residuals .02 | `evidence/signal/F_G_eeg_hr_summary.json` |
| S0-I09 | VERIFIED FACT (outcome-free) | Linear label-free encoder: reconstruction .26 (neighbour baseline .30); construct AUC .80 (random .62, handcrafted .89); reference distillation R² −.08 to −.13 | `evidence/signal/J_encoder_summary.json` |
| S0-I10 | INFERENCE | CAIRN's gap survives in narrowed form. The decisive unknown is the size of the anchored moment effect beyond item easiness, likely small (EyeBench: 1–3 AUROC points). The locked primary cohort has fewer moments than planned, so the Stage-1 simulation decides whether the lock is adequately powered | Reassessment |
| S0-I11 | OPEN QUESTION | Human anchors (G-AN); Lallé paper text and data terms; Chen 2026 methods; outcome-free mapping of forensic `question_no` to item-bank items; Immune's post-215 s edit structure | — |
