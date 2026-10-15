# Stage 0c — outcome-free signal feasibility and modality decisions

2026-10-13. Nothing here reads a quiz outcome.

## Scope

**Data.** Decisions use **development and label-free data only**: all released exposures except the tested exposures of the locked cohorts (E4 session 2, E5 session 2).

- 1,152 exposures, 177 learners, 311,428 learner-seconds.
- Anchored analyses use the 9 development videos and the provisional (machine) anchors.
- The anchors of the locked-content videos (Stars, Immune) were not used.

**Code.**

| Kind | Location |
|---|---|
| Library | `src/cairn/extract.py`, `channels.py`, `pooling.py`, `encoder.py`, `stats.py` |
| Scripts | [scripts/](scripts/): `channels_build.py`, `signal_feasibility.py`, `eeg_hr_feasibility.py`, `encoder_stage0.py` |
| Outputs | [evidence/signal/](evidence/signal/) |

**Representation.**

- Per-second channels are computed from the released 128 Hz gaze, pupil, saccade, blink and head streams. They use the frozen G01-R validity rule and are summarized at 10 Hz, then 1 Hz.
- Reference-relative channels use the **attentive viewings of the same video by other learners**. Self-inclusion is impossible by construction: `reference_stats` raises, and this is tested.

| Family | Channels |
|---|---|
| Reference-free | valid, on-screen, blink, saccades, speed, 5 s dispersion, pupil (z), head distance (z), head motion |
| Reference-relative | `dist` (distance to the peer median ÷ peer spread), `logdens` (peer-KDE log-density), `rho5` (5 s correlation with the peer mean course), `pupil_rel`, `valid_rel` |

## 1. Variance structure (A)

Attentive viewings; shares weighted over experiment × video units. "person × moment" is the residual: time-local, idiosyncratic variance, which whole-video features discard.

| Channel | Person 1 s / 10 s | Stimulus-locked 1 s / 10 s | **Person × moment** 1 s / 10 s | Residual lag-1 (1 s / 10 s) |
|---|---|---|---|---|
| dist | .08 / .27 | .15 / .14 | **.77 / .59** | .30 / .13 |
| logdens | .11 / .30 | .14 / .13 | .75 / .57 | .34 / .20 |
| rho5 | .07 / .15 | .38 / .37 | .55 / .49 | .79 / .11 |
| sacc | .15 / .39 | .16 / .17 | .69 / .44 | .23 / .24 |
| valid | .36 / .63 | .03 / .02 | .61 / .35 | .37 / .39 |
| blink | .40 / .60 | .03 / .02 | .57 / .38 | .59 / .43 |
| pupil (z) | .00 / .03 | .26 / .25 | .74 / .73 | .81 / .35 |
| pupil_rel | .01 / .04 | .05 / .05 | .95 / .91 | .81 / .35 |
| head_motion | .12 / .33 | .03 / .03 | .85 / .65 | .51 / .05 |

[I] Reading:

- Gaze alignment and saccade channels keep a large person × moment component.
- Validity is mostly a person trait at 10 s, but has persistent within-person episodes (lag-1 ≈ .4), consistent with the planning audit (INF-094).
- Pupil is luminance-locked (26%). Its relative version is almost all residual.

## 2. Anchored moment terms (B) — development anchors

The moment term is the anchor-window mean minus the learner's whole-video mean (plan §10). The figures below are shares of its variance:

- **item:** constant across learners, absorbed by item easiness β;
- **person × item:** what λ can use.

| Channel | Item share | **Person × item share** | Within-viewing odd/even reliability (Spearman–Brown; upper bound) | Test–retest attentive ↔ distracted viewing (r) |
|---|---|---|---|---|
| valid | .05 | .82 | .80 | .01 |
| onscreen | .02 | .89 | .94 | .01 |
| blink | .04 | .83 | .91 | .01 |
| sacc | .25 | .67 | .68 | .04 |
| speed | .22 | .68 | **.38** | .11 |
| disp5 | .52 | .40 | .98* | .03 |
| pupil | .25 | .63 | .97* | .11 |
| dist | .06 | .70 | .68 | .08 |
| logdens | .14 | .75 | .70 | .06 |
| rho5 | .49 | .46 | .97* | .02 |
| pupil_rel / valid_rel | .00 (by construction) | .84 / .86 | as pupil / valid | .13 / .02 |

\* Inflated by 5 s smoothing or slow dynamics.

**[I] Reliability is bounded on both sides but not pinned down:**

- Within a viewing, the person × item part of unsmoothed channels has split-half reliability ≤ .68–.80. This is an upper bound: 1 s autocorrelation inflates it.
- Across two viewings of the same video by the same learner, it is about 0. The second viewing is distracted, so this is a lower bound that also includes a real state change.
- So the moment-level deviations are state-like, or noise. They are not stable person × content traits.
- Outcome-free data cannot say how much of the within-viewing reliability is attention. Only the item link (NH1) can.
- **The Stage-1 simulation must span anchored-feature reliability from about 0.2 to 0.7.**

**Redundancy** (double-centred correlations):

| Pair | r |
|---|---|
| valid ~ −blink | −.93 |
| dist ~ −logdens | −.80 |
| pupil_rel = pupil | 1.0 once item-centred |
| valid_rel = valid | 1.0 once item-centred |
| rho5 vs dist / logdens | ∓.36 |
| sacc, speed, disp5 | inter-correlated .34–.46 |

There are about four independent moment families: validity, alignment, rho5, and saccade dynamics. Pupil is a fifth, ablation-only family (§7).

**Anchor coverage:** 8.2% of attentive anchor windows have < 50% valid gaze, and 2.5% have no gaze position at all.

## 3. Missingness behaviour (C)

Medians per exposure:

| | Attentive | Distracted |
|---|---|---|
| Invalid fraction | .14 | .26 |
| Invalid episodes per minute | 18.8 | 22.4 |
| **Long (≥ 1 s) episodes per minute** | **0.23** | **1.60** |
| Share of invalid time in long episodes | 5% | 30% |
| Off-screen share of invalid samples | 1.6% | 7.0% |
| Blink-coded share of invalid samples | 40% | 46% |

- Head motion is higher in invalid than in valid seconds in 69% of exposures (median ratio 1.15; E2–E5).
- **[I]** Long invalid episodes behave like **behaviour** (looking away, disengaging) rather than random tracker loss: they are seven times more frequent under distraction. Short (blink-scale) loss is common in both conditions.
- **[I]** This supports measuring NH4 (in-window data loss as behaviour) with an episode-length-aware validity channel, not raw validity.

## 4. Construct check (D): attentive vs distracted viewing, E1–E3

**Within learner and video** (paired dz, distracted − attentive; 422 pairs):

| Channel | dz | | Channel | dz |
|---|---|---|---|---|
| rho5 | **−1.28** | | dist | +.71 |
| sacc | −.99 | | disp5 | −.69 |
| logdens | −.75 | | valid | −.68 |
| speed | −.59 | | blink | +.52 |
| onscreen | −.50 | | pupil | +.11 |

**Held-out-learner discrimination** (5-fold learner-grouped, logistic on whole-viewing channel means; 883 exposures, 87 learners):

| Feature set | AUC |
|---|---|
| Reference-relative | **.89** |
| Reference-free | .87 |
| All | .90 |
| Validity only | .74 |

[I] The representation indexes viewing engagement. **Caveat:** distraction is always the second viewing, so condition is confounded with repetition and with the arithmetic task (critique #11). This is a sanity check, not proof of attention.

The plan's go-to-lock rule (iii), "e(t) separates distracted from attentive viewing above chance in held-out learners", is **met** by the handcrafted channels (AUC .89) and by the linear encoder (.80; §6).

## 5. Content-identity leakage (E)

Balanced accuracy for video identity (9 development videos, chance .11), learner-grouped CV:

| Features | Reference-free | Reference-relative |
|---|---|---|
| Whole-video means (the person path, ē) | .30 | **.58** |
| Anchored moment terms z − ē (person-centred) | .18 | .16 |
| Item-centred moment terms | .11 (chance) | .11 (chance) |
| Protocol (experiment) identity from item-centred terms (5 classes, chance .20) | .23 (all channels) | |

**[I] Leakage is controlled where CAIRN needs it to be:**

- **Moment term:** λ is identified within learner × item after item easiness is absorbed, which is equivalent to item-centring. There it is at chance.
- **Person path:** the whole-video reference-relative means carry strong content identity (.58). They must enter θ only next to video and experiment offsets, never in a flexible model without them. This confirms E8 (G01-R probe .50).
- **Protocol:** the small protocol leakage (.23 vs .20) is absorbed by experiment intercepts in θ. It is a reason to keep the locked cohort a different protocol.

## 6. Label-free encoder (J)

Fold-safe, 5 learner-grouped folds; fitting on training learners is asserted, and refits are deterministic (identical parameter hashes).

The encoder is a linear masked-centre-reconstruction encoder: 8 channels, 9 s context, K = 3, 536 parameters. It is the linear special case of the plan's masked-span objective.

| Check | Held-out learners | Reference |
|---|---|---|
| Reconstruction R² of the masked second | .26 | Neighbour-mean interpolation .30 |
| Attentive/distracted AUC from encoder means | **.80** | Random-projection encoder (matched noise) .62; raw channel means .89 |
| Identity from encoder moment terms: person-centred / item-centred | .16 / .11 | Random encoder .12 / .11 |
| **Reference distillation:** predict dist, logdens, rho5 from reference-free channels | **R² −.13, −.10, −.08** | — |

[I] Reading:

1. A learned linear bottleneck keeps construct information above matched noise, but it does **not** beat handcrafted channels or a trivial interpolation baseline. Stage 0 gives no outcome-free reason to make a learned encoder the primary representation. Per [R4], **CAIRN-linear (handcrafted channels + anchored pooling + IRT head) becomes the pre-specified primary candidate**. A learned encoder (linear here; TCN with PyTorch in Stage 2) becomes ablation A4.
2. **Peer-free distillation fails.** Reference-free gaze cannot predict the reference-relative channels in new learners. The regime-B ("no peers") part of claim N-b is **not supported** without video frames (saliency, C4). Regime B is removed from the primary claims.

## 7. EEG and ECG (F, G)

EEG is the E3 attentive development cells in the G01-R processed-route cache: 156 cells, 29 learners.

- CorrCA uses the G01-R formulation (pooled within/between covariance, γ = 0.5).
- It is fitted on one random half of learners and applied to the other (2-fold).
- First generalized eigenvalue: .043 / .049.

| Check (held-out half) | 10 s windows | 5 s windows |
|---|---|---|
| Mean windowed ISC, component 1 | .080 | .078 |
| Variance: person / stimulus-locked / person × window | .05 / .25 / .69 | .03 / .24 / .73 |
| Residual lag-1 | −.03 | .01 |
| **Reliability of the person × window residual — component 1 vs component 2** (plan's criterion) | r .03 → SB **.06** | r .02 → SB .03 |
| Same component against two disjoint reference halves | r .15 → SB .26 | r .15 → SB .26 |
| Coupling with ocular residuals (valid, blink, sacc, rho5, dist) | \|r\| ≤ .07; R² **.022** | — |
| Component 1 vs 2 agreement after regressing out ocular residuals | .02 | — |

[I] Time-resolved EEG synchrony in BBBD is **not ocular**, but its idiosyncratic moment-level part is **not reliable** by the plan's pre-declared Stage-0 criterion:

- The components do not share a person-specific moment signal.
- The planning audit's simple proxies agreed: alpha is 64% person-level, and the filter-free ISC proxy is 77% residual noise.
- Whole-video EEG was null in G01-R (H2b −0.004).

**HR** (2 Hz instantaneous HR; deviation from the leave-one-out peer course):

- variance: stimulus-locked 10–13%, residual 86–90%;
- lag-1 .40 at 10 s;
- odd/even "reliability" .99 is an artefact of the 2 Hz interpolation and is uninformative;
- whole-video HR was null in G01-R (H2c −0.011), and HR ISC ≈ 0.

[I] There is no outcome-free evidence of usable moment-level HR information.

## 8. Modality decisions for Stage 1

Each decision is [D], made from Stage-0 evidence only.

| Modality / channel | Decision | Evidence | What would reopen it |
|---|---|---|---|
| **Gaze alignment** (`dist` or `logdens` — redundant, keep `logdens`; `rho5`) | **Retain for primary development** | Large person × moment share; zero or low item-centred identity; strongest construct effect (rho5 dz −1.28) | — |
| **Gaze dynamics** (`sacc`, `disp5`) | **Retain for primary development** | Construct dz −.99 / −.69; reliable within viewing | — |
| `speed` | **Reject before Stage 1** | Low within-viewing reliability (.38); redundant with `sacc` / `disp5` | — |
| **Validity / off-screen** (`valid` with an episode-length split; `onscreen`; `blink` merged into validity) | **Retain for primary development** (NH4 channel) | Long invalid episodes 7× under distraction; off-screen share 4×; behaviourally interpretable | — |
| Pupil (`pupil_rel`) | **Retain only as an ablation** (development-gated, plan §12.4) | 84% person × item variance and the highest cross-viewing stability (.13), but no construct sensitivity (dz .10) and 8% gaze-position artefact | Passes the development selection rule |
| Head (distance, motion) | **Retain only as a diagnostic** | Higher motion in invalid seconds (69% of exposures); absent in E1 (development) → protocol-dependent input | A prospective cohort with head data throughout |
| **EEG** (CorrCA windowed ISC, alpha) | **Retain only as a diagnostic** (no development branch) | Fails the plan's own Stage-0 reliability criterion (SB .06); not ocular (R² .02). A branch would add forking paths without outcome-free support | A new dataset with denser item anchors, or a reliability check that passes |
| **ECG / HR** | **Retain only as a diagnostic** (no development ablation) | No outcome-free evidence of reliable moment information; null whole-video results; seconds-scale lags | — |
| Respiration | Reject (unchanged) | Uncalibrated; provenance open | — |
| Covariates C, recording quality Q | Person path (unchanged) | G01-R continuity | — |

**Answers to the plan's modality questions:**

- **Does gaze still justify the primary role?** Yes. It is the only modality with both reliable moment-level structure and construct sensitivity.
- **Does EEG deserve inclusion?** Not as a model input. It is not discarded "because the old ridge failed": the outcome-free, time-resolved check was done and failed on reliability.
