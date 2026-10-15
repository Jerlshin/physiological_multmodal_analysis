# Stage 0 — CAIRN feasibility, novelty close-out and Stage-1 preparation

2026-10-13. Executed on the user's instruction to run Stage 0 of the [research plan v1.1](../research_plan.md#23-staged-implementation-roadmap) and prepare Stage 1.

**Status: STAGE 0 COMPLETE (computational parts). Gate G-AN awaits human annotators. GO to Stage 1 under the conditions in [reassessment.md](reassessment.md#12-verdict). No outcome accessed. No supervised CAIRN fit. Stage 2 not started.**

## Documents

Each document separates **fact → interpretation → decision → unresolved question**.

| Document | Content |
|---|---|
| [entry_state.md](entry_state.md) | Repository, freeze and access-log state at entry; frozen material; disclosures |
| [literature_closeout.md](literature_closeout.md) | Closest-paper comparison (Lallé 2025, Chen 2026, Davidesco 2023, Lan 2017, EyeBench); corrections; novelty verdict |
| [timeline_audit.md](timeline_audit.md) | Stage 0a: stimulus timeline recovery, gate G-TL, the Enzymes explanation |
| [anchor_audit.md](anchor_audit.md) | Stage 0b: provisional (machine / LLM-assisted) anchors, counts, handoff for human annotation |
| [annotation/ANNOTATION_PROTOCOL.md](annotation/ANNOTATION_PROTOCOL.md) | Human annotation protocol, template and package manifest |
| [signal_feasibility.md](signal_feasibility.md) | Stage 0c: outcome-free signal checks, encoder, EEG/ECG, modality decisions |
| [reassessment.md](reassessment.md) | Critical reassessment of CAIRN; go / no-go |
| [stage1_spec.md](stage1_spec.md) | Exact Stage-1 simulation, `src/cairn` plan, leakage tests, gate, baselines, manifests, reproducibility |
| [decisions.md](decisions.md) | Stage-0 decision and inference log (S0-D…, S0-I…) |
| [scripts/](scripts/), [evidence/](evidence/) | Code and outputs (`evidence/SHA256SUMS`) |

## Final Stage-0 report

**1. Did the closest-paper review preserve CAIRN's novelty?**
Partly.

- Lallé et al. (AIED 2025) already predict **per-item retention from gaze in content-tied windows of an educational video, for held-out learners**. "First content-anchored item-level prediction in video learning" (part of N-a) is **withdrawn**.
- Lallé models no item difficulty or learner level, uses no peer-relative signal, runs no anchor-randomization null, reports no anchoring reliability or blinding, and uses one video with seen items.
- Chen 2026 (abstract only) is explanatory.
- EyeBench's own results show a text-only model nearly matching gaze + text, which shows why item-level scores need an item-only baseline.

**2. What exactly remains novel?**

| Claim | Content |
|---|---|
| N-a′ | A psychometrically identified predictive formulation: item easiness + learner level + within-learner moment effect, for physiology during learning |
| **N-d (now central)** | Falsification built in: anchor permutation, circular shift, in- vs out-of-window long data-loss episodes |
| — | Outcome-blind, reliability-gated, hash-frozen anchors with a public protocol |
| N-b′ | A peer-relative per-second representation as the item predictor. The peer-free variant is dropped |
| N-e | Evaluation on new learners, new content and a locked new-protocol cohort, plus external replication. Lallé's method becomes baseline B9 |

**3. Were all 11 stimulus timelines recoverable?**

- **10 of 11 PASS; Immune is PARTIAL** (0–215 s solid).
- All 9 development videos pass.
- **Enzymes is explained:** the stimulus is two eHow videos concatenated (`AAZ03aScPr8` 5–145 s, then `lkRZKqDdwzU` 50–178 s), with the redundant review cut.
- Flags:
  - Work-energy, Capacitors and Planets use a substitute replication criterion (shown in one experiment only).
  - Planets and Enzymes rest on replicated but unvalidated (tier B) evidence.
  - Mosquitoes 0–180 s is tier B.
- The validator rule was revised once (v1 → v2), for documented reasons; under v1, Internet and Mosquitoes would be PARTIAL.

**4. How many items could be reliably anchored?**

- Provisionally **105 of 131** (development **87 of 107**), on machine (R1 lexical + R2 LLM-assisted) anchors.
- They occupy only **59 distinct development moments**, and 19 in the locked primary cohort (26 items).
- **None is human-annotated yet. G-AN is not satisfied.**

**5. Which videos/items failed the timeline or annotation gates?**

- Timeline:
  - Immune items 2, 7, 8, 9 and 10 fail (evidence after 215 s, or in removed material).
  - Capacitors item 8 is key-inconsistent.
- Not localized (20 items):
  - multi-span: Stars 7, Internet 9, Mosquitoes 12, Related 2, 6, 12;
  - diffuse: Mosquitoes 8, 9; Work-energy 5, 8; Planets 4, 12; Enzymes 1, 2;
  - absent from narration: Light bulbs 4, Birth rate 1, Related 3;
  - longer than 45 s: Planets 9, 10; Enzymes 10.
- Annotation gate G-AN: **not evaluated**. It needs two human annotators; the handoff is ready.

**6. What did the outcome-free temporal analyses show?**

- Gaze alignment and saccade channels keep 44–77% person × moment variance.
- Anchored moment terms are reliable within a viewing (split-half ≤ .68–.80, an upper bound) but not stable across viewings (about 0), i.e. state-like.
- Attentive vs distracted viewing is separated in held-out learners (AUC .89; within-learner rho5 dz −1.28). This is confounded with repetition.
- Long invalid episodes are behavioural: 7× more frequent under distraction.
- The label-free linear encoder keeps construct information (AUC .80 vs .62 for matched noise) but does not beat handcrafted channels.
- Peer-free distillation fails (R² < 0).

**7. Which modalities survive into Stage 1?**

| Decision | Modalities |
|---|---|
| Primary | Gaze alignment (`logdens`, `rho5`), gaze dynamics (saccades, dispersion), validity / on-screen (episode-aware) |
| Ablation only | Pupil |
| Diagnostic only | Head, EEG, ECG/HR |
| Rejected | `speed`, respiration |

**8. Does EEG earn a branch?**

- **No.** Time-resolved CorrCA EEG-ISC is not ocular (R² .02), but its person × moment part fails the plan's pre-declared reliability check (component split, Spearman–Brown .06).
- It stays a diagnostic.

**9. Is content-identity leakage under control?**

- **For the moment term, yes:** item-centred moment terms classify video identity at chance (.11).
- **The person path is not leakage-free:** whole-video reference-relative means identify the video (.58). They are allowed only next to video and experiment offsets.
- Protocol leakage is small (.23 vs .20).

**10. Does CAIRN still appear to be the strongest method direction?**

Yes, but in a simplified form and with an honest risk:

- **CAIRN-linear** (handcrafted channels + anchored pooling + Rasch head) is the pre-specified primary candidate. The learned encoder becomes ablation A4.
- **Main risk:** the effect may be too small to detect in the lock (EyeBench-scale increments; about 19 locked moments).

**11. Did any new literature suggest a better alternative?**

- No. Training-free vision-language models fail on Lallé's dataset (Becquet 2026). The other 2025–2026 work is descriptive or explanatory.
- Lallé's method is adopted as a baseline (B9), and its dataset remains the preferred external test, terms permitting.

**12. What changed in the research plan?** (amendment v1.2, labelled [S0-x] in the plan)

- Novelty narrowed: N-a′ replaces N-a; N-d becomes the central claim; regime B is dropped.
- Modality decisions updated.
- G-TL operationalization and substitute criterion; G-AN status.
- CAIRN-linear is primary; new baseline B9.
- NH4 uses long episodes.
- Randomization nulls permute distinct anchor moments.
- §20.3 power inputs corrected: 26 anchorable E4 items, about 19 moments. The Stage-1 simulation must re-derive δ_item and locked power, with a declared redesign path if power is low.
- The literature review is corrected: EyeBench numbers; the Lallé "already knew" claim withdrawn; N44–N51 added.

**13. What files/code were added or modified?**

- **Added:**
  - `src/cairn/`: `__init__`, `paths`, `exposures`, `extract`, `timeline`, `transcripts`, `anchors`, `channels`, `pooling`, `encoder`, `stats`, `gate`;
  - `tests/test_cairn.py` (21 tests);
  - `docs/research/novel_method/stage0/`: this folder, its scripts and evidence.
- **Amended** (dated, labelled): `novel_method/research_plan.md`, `novel_method/literature_review.md`, `novel_method/README.md`, `docs/research/README.md`, `docs/research/decision_log.md` (D076–D083), `docs/research/inference_register.md` (INF-101–INF-111), and `.gitignore` (+ `data/stimuli/`).
- **Git-ignored data:**
  - `data/stimuli/`: 12 public videos, captions, transcripts, the annotation package, literature copies;
  - `data/derived/cairn/`: 10 Hz series, 1 Hz channels, video features, moment terms.
- **No frozen or historical file was modified.**

**14. Did any outcome access occur?**

- **No.**
  - The BBBD access log still has 15 entries and the John log 1 (hashes unchanged).
  - No CAIRN authorization or freeze exists.
  - No supervised fit was run.
- Disclosed:
  - one incidental view of a pre-existing **experiment-wide aggregate** (E1 domain-question mean 0.535; no item-, video- or learner-level value);
  - a schema-only (column-name) read of the forensic item table to specify the gated loader.

**15. Is the project ready for Stage 1?**

- **Yes, for Stage 1 (outcome-free simulation and implementation).**
- Not yet for Stage 2, which additionally needs:
  - (a) two human annotators and a frozen anchor set passing G-AN;
  - (b) a passing Stage-1 simulation;
  - (c) a CAIRN freeze and an explicit development-scope authorization.

**16. Exact next step (not started).**

1. Commit the planning phase, then the Stage-0 phase (user action).
2. Recruit two annotators for [ANNOTATION_PROTOCOL.md](annotation/ANNOTATION_PROTOCOL.md). This runs in parallel with step 3.
3. Run Stage 1: implement `cairn.design`, `item_keys`, `features`, `model`, `inference`, `simulate`, `manifest` and `cli` per [stage1_spec.md](stage1_spec.md). Create `.venv-cairn` from a new `requirements-cairn.lock`. Then run `python -m cairn simulate --set development,locked_primary --replicates 500`.
4. Stage 2 only after the user writes `analysis_freeze_cairn/AUTHORIZATION.json` with scope `development`, bound to a verified CAIRN freeze that contains the human anchor set. **Not authorized here.**

## Exit checks

These are re-run at the end of Stage 0; results are in `evidence/exit_checks.log`:

- `g01r verify-freeze`: VERIFIED.
- Full unit-test suite: G01-R, John and CAIRN.
- Access-log hashes equal to the entry hashes.
- Frozen-path diff empty.
