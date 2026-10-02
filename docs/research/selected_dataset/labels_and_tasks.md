# Labels, outcomes and defensible tasks

Sources: [S01–S06 and P01–P04](evidence/source_registry.md). **There is no verified continuous ground-truth attention trace.** The data contain instructions, stimulus identifiers, behavioral responses and physiological measurements with different semantics. Keep those distinctions in the data dictionary and in claims.

| Variable | Evidence class / role | Defensible use | Boundary |
|---|---|---|---|
| Attend vs distract, experiments 1–3 | VERIFIED FACT: assigned experimental condition | Discrimination of the recorded compound viewing protocols | Not naturally occurring mind wandering; condition is confounded with fixed order, arithmetic and repeat viewing |
| Exp. 4 session | VERIFIED FACT: two attentive blocks with different content | Block/content comparison with explicit design limitations | Session 2 is not “distracted”; no attention-class pair here |
| Exp. 5 intervention | VERIFIED FACT: second exposure with reward and question preview | Association with the bundled intervention/exposure | No isolated causal reward/attention effect without further design evidence |
| Quiz answer key / correctness | Scoring reference / observed response accuracy | Immediate item/video recall or comprehension performance, after mapping audit | Not a continuous attention label or longitudinal learning gain |
| Quiz partial score | Behavioral outcome | Item-level or aggregated score retaining denominator and scoring rule | Do not force multi-select/penalty scores into Bernoulli counts |
| Domain pretest | Prior-knowledge outcome/covariate | Control for baseline knowledge where matched | Availability and definition differ; not a universal pre/post parallel test |
| Digit span | Behavioral performance / working-memory proxy | Trait-related covariate or carefully specified outcome | Not IQ; weighted score formula and valid length need verification |
| ASRS items/subscores | Self-report traits | Association and subgroup/sensitivity analyses | Screening values do not establish ADHD diagnosis; avoid clinical labels |
| GPA | Self-reported historical academic outcome | Restricted exploratory association with eligibility/missingness controls | Not a standardized cross-institution examination; missing-not-at-random plausible |
| Video engagement rating | Subjective report | Explore perceived engagement if row-level data exist | Collection/availability/scoring and timing not fully established |
| Stimulus ID / local task ID | Experimental metadata | Content grouping and identity controls | Same local ID can mean different videos across experiments; use canonical video identity |
| ISC / alpha / HRV | Derived physiological measures | Predictors or explicitly operationalized response variables | Cannot be relabeled independent attention ground truth and “validated” against themselves |

## Quiz construction and scoring

**VERIFIED FACT.** P01 uses four-option questions and describes multiple-correct-option scoring: points for correct selections and subtraction for incorrect selections. Question types include recognition and comprehension, categorized by independent raters/majority decision. Some experiments provide prior-domain questions. Question/answer order was randomized in the original lab studies. Website summaries such as “10–11 questions” do not describe every released table; Exp. 4/5 reference files have 36 question rows per participant (12 for each of three videos). [P01 Methods; S06]

The inspected reference schemas differ:

| Experiment | Fields as written in source TSV |
|---|---|
| 1 | `participant_id, stimulus_id, question_type, question_no, answer, correct_answer, is_correct` |
| 2 | `participant_id, stim_no, question_type, question_number, answer, correctanswer, is_correct` |
| 3 | `participant_id, stim_no, question_no, numberofanswers, answers, correct_answers, score` |
| 4, 5 | Same fields as 3 plus `is_correct` |

[Machine-readable field/count audit](evidence/repository_metadata_audit.json). The static source files are copied by the reformatter; this script does not reconstruct scores from original response logs. Exp. 1's reference file includes domain/memory types even though its described protocol emphasizes intentional post-video testing, and it has 31 IDs against 27 released participants. This discrepancy is not resolved by renaming its columns. [S06; INF-005]

**OPEN QUESTION — corrected joins (INF-016).** S04 explicitly corrects Exp. 4/5 participant-to-quiz mappings and `is_correct`. Confirm the archive-level answer key, actual selected options, partial credit, score range/denominator and original randomized answer-order encoding. Reconstruct aggregate scores both ways and explain discrepancies before selecting any target. Current publications predate that correction; whether their internally used labels shared the error is unknown. Do not assume either that their findings are invalid or that they already used corrected labels.

**OUR INFERENCE (INF-017).** Exp. 4's post-test for its latter videos provides a relatively direct, single-exposure outcome pairing; Exp. 5's final test follows repeated, previewed, rewarded viewing. If first-viewing physiology is paired with that final test, later exposure is an intervening learning opportunity. Preserve this distinction; pooling scores without it can change the scientific question.

## Trait and subjective-score definitions

The website codes ASRS answers 0–4; earlier prose uses a 1–5 response scale. The supplied files include 18 items, dichotomous and Likert screener/full scores, and inattentive/hyperactive subscores. Verify item offsets and subscale construction before pooling; record source instrument version. The website digit-span range is described as 3–7 digits and supplies `score` plus `weighted_score`; P04 specifies two reverse-recall trials at each length (10 trials total) and maximum span with at least one correct trial at that length. The separate `weighted_score` formula and correspondence to current release values remain unresolved. Video engagement is described on a seven-point scale with unclear verbal ordering in the website text, and it is absent from the inspected static phenotype export assets; file-level availability is OPEN. [S05 questionnaires; S06 config; INF-018]

## Candidate task feasibility without selecting a problem

**OUR INFERENCE.** The strongest target family is carefully aligned immediate quiz performance, with prior knowledge/traits and video difficulty as controls. Protocol discrimination can be a diagnostic benchmark but requires narrow naming. Cross-modal prediction is feasible in principle where channels overlap, and has precedent in P03. Missing-modality analysis depends on establishing actual missingness and interpolation masks. Long-term retention, diagnosis, causal intervention efficacy and real-world classroom performance are not established outcome capabilities of this release. No modeling is authorized by this assessment; see [candidate directions](research_readiness.md).
