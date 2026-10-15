# Reassessment of CAIRN after Stage 0

2026-10-13. Written from the position of a sceptical reviewer. Each answer is labelled:

| Label | Meaning |
|---|---|
| [F] | Stage-0 fact |
| [I] | Interpretation |
| [D] | Decision |
| [U] | Unresolved |

## 1. Is the research gap still defensible?

**Yes, but narrower.**

- [F] Lallé et al. 2025 predict per-item retention from gaze in content-tied windows of one educational video, for held-out learners.
- [F] They do not model item difficulty or a learner level, run no anchor-randomization null, publish no reliability or blinding for their spans, use no peer-relative signal, and evaluate on one video with seen items.
- [F] EyeBench shows that an item-only text model reaches 61 AUROC on reading comprehension, and gaze adds 1–3 points.
- [I] An item-level F1 or AUC from a pooled classifier cannot tell whether the moment signal predicts anything beyond item difficulty.
- [I] The defensible gap is therefore: *does engagement at the moment an item's content is presented predict that item's correctness beyond item easiness and the learner level, and does the content timing — not item-level modelling, data loss or fatigue trends — carry that information?* No published work answers this.

## 2. Is the novelty real after the full-paper checks?

**Real but narrowed** ([literature_closeout.md](literature_closeout.md) §4).

- "First content-anchored item-level prediction from gaze in video" is **withdrawn**: Lallé 2025.
- What remains:
  - a psychometrically identified predictive formulation (N-a′);
  - falsification as part of the method (N-d, now the central claim);
  - outcome-blind, reliability-gated anchoring with a public protocol;
  - peer-relative moment representation (N-b′, without the peer-free variant);
  - inductive evaluation across new content and a new protocol (N-e).
- [U] Lallé's paper text (reported retention performance) and Chen 2026's methods were not readable. The verdict rests on Lallé's public code and its companion paper.

## 3. Are the stimulus timelines reliable enough?

**Yes, with flags** ([timeline_audit.md](timeline_audit.md)).

- [F] 10/11 videos PASS and all 9 development videos PASS. Immune is PARTIAL (0–215 s solid).
- [F] The Enzymes mismatch is explained: two eHow videos were concatenated and the redundant review removed.
- [F] Three single-experiment videos rely on a declared substitute criterion.
- [F] Two videos (Planets, Enzymes) rest on replicated but unvalidated (tier-B) evidence.
- [D] Anchor-shift sensitivity (±5/±10 s) is mandatory in Stage 2 and in the lock.

## 4. Are enough items genuinely localizable?

**Yes for development; tighter for the lock** ([anchor_audit.md](anchor_audit.md)).

- [F] 87/107 development items (81%) and 105/131 overall are anchorable on the provisional machine anchors.
- [F] They occupy only 59 distinct development moments, and 19 in the locked primary cohort (26 items).
- [F] Localized items are mostly recognition items, so the localized/diffuse contrast is confounded with category.
- [U] **No human annotation exists yet**. Every count is provisional until G-AN.

## 5. Is there enough reliable moment-level signal?

**Present, but its attention-relevant reliability is not identifiable outcome-free.**

- [F] Gaze alignment and saccade channels keep 44–77% person × moment variance.
- [F] Within-viewing split-half reliability of the anchored person × item part is ≤ .68–.80, an upper bound.
- [F] Cross-viewing stability is about 0 (a lower bound).
- [F] Construct separation of attentive vs distracted viewing in held-out learners is strong (AUC .89), but confounded with repetition.
- [I] The signal is state-like. Whether those states track learning of specific content is exactly NH1.
- [I] The plausible effect is **small**. EyeBench's 1–3 AUROC-point gaze increment in reading, where gaze lands on the tested words, is a sobering external anchor.

## 6. Does the representation suppress content identity adequately?

**Yes for the moment term; no for the person path.**

| Features | Identity accuracy | Chance |
|---|---|---|
| Item-centred moment terms | .11 | .11 |
| Person-centred moment terms | .16–.18 | .11 |
| Whole-video reference-relative means | .58 | .11 |

- [D] Whole-video means may enter only next to video and experiment offsets. Flexible person-path models must include the offsets or be probed.

## 7. Does gaze still justify the primary role?

**Yes.** It is the only modality with both reliable moment structure and construct sensitivity.

## 8. Does EEG deserve inclusion?

**No branch.** Time-resolved CorrCA EEG-ISC is not ocular (R² .02 on ocular residuals), but its person × moment part fails the plan's own reliability check (component split SB .06). It stays a diagnostic.

## 9. Is the proposed architecture still the best candidate?

**Yes as a direction. Simplified in detail.**

[D] Changes, each a minor architectural decision with Stage-0 rationale:

| Change | Rationale |
|---|---|
| **Primary candidate = CAIRN-linear** (handcrafted channels, anchored pooling, Rasch head). The learned encoder (linear; TCN in Stage 2) becomes ablation A4 | The label-free encoder did not beat handcrafted channels on reconstruction or construct. This is the [R4] fallback, decided before outcomes |
| **Channels reduced** to five families: validity (episode-length aware), on-screen, alignment (`logdens`), `rho5`, saccade/dispersion. `speed` dropped; `blink` merged into validity. Pupil is an ablation | Redundancy and reliability (§2 of signal_feasibility.md) |
| **Regime B (peer-free, reference-distilled) removed** from the primary claims | Distillation R² < 0 for held-out learners |
| **NH4 uses long invalid episodes** (≥ 1 s), not raw validity | Long episodes are the behavioural part: 7× more frequent under distraction |
| **New external baseline B9:** Lallé-style pooled window classifier (reference-free gaze features in item windows, item identity dropped, learner-grouped CV) | The direct test of what psychometric anchoring adds over the closest prior method |
| **Shared anchors handled explicitly** | Items sharing a span share a moment regressor; the randomization nulls permute *distinct anchor moments*, not items |

## 10. Has any 2025–2026 method become a stronger direction?

**No** (literature_closeout.md §4.4). Training-free VLMs fail on this exact dataset (Becquet 2026). Lallé-type classifiers are the comparator, not an alternative.

## 11. Remaining risks, honestly ranked

| Rank | Risk | Mitigation |
|---|---|---|
| 1 | **The effect is too small to detect in the lock** (E4: 39 learners × 26 items, about 19 distinct moments; plausible gaze increments of 1–3 AUROC points) | Stage-1 simulation on the real anchor structure decides the minimum detectable effect. If power is insufficient, the confirmatory design changes **before** Stage 2: e.g. E4 + E5 as one pooled lock, or a one-sided intersection test |
| 2 | **No human anchors** | Gate G-AN must pass before Stage 2. Provisional anchors are for outcome-free Stage-1 work only |
| 3 | **Category confound** in localized vs diffuse items | Contrast conditioned on R/C and item easiness [R13] |
| 4 | **Tier-B timelines** (Planets, Enzymes, Mosquitoes 0–180 s) | Anchor-shift sensitivity; sensitivity analysis excluding tier B |
| 5 | **Lallé collision** may make reviewers see an incremental contribution | Frame the paper around identification and falsification; run Lallé's method as a baseline |

## 12. Verdict

**GO to Stage 1**, with the narrowed claims and simplified architecture above, under four conditions:

1. **G-AN:** two human annotators complete the protocol, and the anchor set is frozen, **before** any development outcome is linked (Stage 2).
2. **Stage-1 simulation passes** ([stage1_spec.md](stage1_spec.md) §1):
   - T1, T2 and the intersection test keep false detection ≤ .07 under the null scenarios, including fatigue/position and data-loss confounds;
   - the development stop rule has a low go-to-lock rate under the null;
   - the locked design has ≥ 80% power at a stated, plausible effect. Otherwise the lock design is revised first.
3. **Outcome access stays gated** (`cairn.gate`). Development access needs a CAIRN freeze and an explicit user authorization.
4. **No claim of "first item-level prediction"** appears in any document or manuscript.

No major assumption failed outright. The novelty narrowed, the encoder was demoted and regime B was dropped. These are revisions, not a change of direction. The decisive uncertainty, the size of the moment effect, can only be answered by development outcomes under the stop rule.
