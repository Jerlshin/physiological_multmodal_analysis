# Stage 0a — stimulus timeline recovery and gate G-TL

2026-10-13. Outcome-free. Machine-readable outputs are in [evidence/](evidence/):

| File | Content |
|---|---|
| `timeline_table.csv` | Segments, offsets, edit-point CIs, status shares |
| `timeline_seconds.csv` | Per recording second: source, video time, G-TL status |
| `timeline_map_1hz.csv` | All candidate mappings and their replication flags |
| `timeline_gate_summary.json` | Verdicts and per-block validators |
| `timeline_audit_summary.json` | Per-configuration agreement |
| `timeline_cut_locked_validation.csv`, `timeline_pupil_luminance_validation.csv` | Independent validators |

Scripts are in [scripts/](scripts/): `timeline_audit.py`, `cut_locked_validation.py`, `pupil_luminance_validation.py`, `timeline_gate.py`. The library code is in `src/cairn/timeline.py`.

## 1. Question

For each of the 11 stimuli, which second of the public YouTube video was on screen at each second of the BBBD recording? Item anchors are built from the public video and transcript, then projected onto the recording clock. A wrong mapping silently destroys the anchoring.

## 2. Facts that motivated the audit

**[F] Recorded and public durations differ** (BBBD event files; YouTube metadata 2026-10-13; *Scientific Data* 2026 Table 2):

| Video | Recorded (s) | YouTube now (s) | Paper listing |
|---|---|---|---|
| Stars | 184.8 | 208.7 | 3:29 |
| Light bulbs | 142.9 | 143.0 | 2:23 |
| Immune | 388.8 | 468.8 | 7:49 |
| Internet | 369.0 | 392.1 | 6:33 |
| Birth rate | 150.2 | 153.3 | 2:34 |
| Mosquitoes | 261.0–261.1 | 300.4 | 4:47 |
| Related | 362.8–362.9 | 385.1 | 6:26 |
| Work-energy | 342.6 | 347.4 | 5:48 |
| Capacitors | 385.5 | 386.8 | 6:27 |
| Planets | 262.4 | 279.0 | 4:39 |
| Enzymes | 268.5 | 191.6 | 3:12 |

**[F] Enzymes has two public sources.** The item bank (`Education_questions`) lists two URLs for it: `lkRZKqDdwzU` ("Three Factors That May Alter the Action of an Enzyme", 191.6 s) and `AAZ03aScPr8` ("What Function Does an Enzyme Serve in a Chemical Reaction", 157.1 s). The official experiment page and the *Scientific Data* paper list only the first.

**[F] Other facts:**

- Within an experiment, every recording of a video has the same duration to the millisecond. Across experiments they differ by ≤ 0.08 s. So one stimulus file per video was used.
- Neither the *Scientific Data* paper, the official experiment page nor the P01 OSF materials (m7gj4, d4k3q) document trims.

## 3. Method

### 3.1 Alignment signals

Both alignment signals are at 10 Hz and use only released peer gaze.

| Signal | Video side | Gaze side |
|---|---|---|
| **Spatial** | Intensity-weighted centroid of the frame difference: *where* new ink or motion appears | Peer-median gaze position |
| **Temporal** | Hard cuts, smoothed over a 0.6 s re-orienting window | Peer-mean saccade-onset rate, z-scored per recording |

- Score: windowed Pearson correlation of the two series at every candidate offset. Windows are 30 s with a 5 s step. Offsets span [−recording length, source length], so an excerpt of any source can be placed anywhere.
- Inputs: all 1,415 released viewings with processed gaze (all sessions, E1–E5). These are a stimulus property and are not used for method selection (§7).

### 3.2 Path model

The stimulus was made by cutting sources, which can only **remove** material. So the alignment path is fitted as **monotone**:

- Within a source the offset never decreases.
- Sources occur in one order, and every order is tried.
- Each removal or source switch costs 0.5 correlation units.
- The fit is Viterbi over windows × (source, offset) states (`cairn.timeline.monotone_viterbi`).

A first, unconstrained Viterbi produced short non-monotonic excursions onto repeated visuals. It is kept only in the audit history, not used.

### 3.3 Decision rule

The rule was fixed before any anchor was built; [`timeline_audit.py`](scripts/timeline_audit.py) has the docstring.

1. Three configurations are fitted: temporal, spatial and combined (the mean of the two).
2. A configuration is *admissible* if its pooled path is physically plausible:
   - video time ≥ −1 s at the recording start;
   - inside every source.
3. A second is *replicated* if the pooled mapping (same source, |Δoffset| ≤ 2 s) is reproduced by **≥ 2 independent experiments**. That is gate G-TL as written in plan §11.2. For the three videos shown in one experiment only (Work-energy, Capacitors, Planets), G-TL cannot be applied as written. They use a **substitute**: both random learner halves **and** both sessions must reproduce the mapping. This is a declared deviation (S0-D04).
4. The final mapping is the admissible configuration replicating the most seconds. A second fails if another admissible configuration replicates a different mapping there (> 2 s apart).

### 3.4 Independent validators

These were added after the first gate run, and are reported with that history (§5).

| Validator | Test |
|---|---|
| **Cut-locked saccade response** | Peer saccade rate in [0.1, 0.6] s after each hard cut, mapped by the candidate timeline, against cuts at random times (2,000 draws). Circular for the temporal configuration |
| **Pupillary light response** | High-passed peer pupil against minus the mapped frame luminance, lag 0.2–1.5 s, against circular shifts ≥ 20 s (1,000 draws). Independent of both alignment signals |

Both are computed per 60 s block.

### 3.5 Final per-second status

| Status | Conditions |
|---|---|
| **PASS-A** | Replicated, no conflict, and validated in its block (p < 0.05) |
| **PASS-B** | Replicated and conflict-free, but no validator informative for any candidate in that block: constant luminance (glass board, blackboard), no cuts |
| **FAIL** | Otherwise |

Edit points are re-localized at 1 s, with a 200-draw viewer bootstrap CI. Seconds inside an edit-point 95% CI fail.

**Video verdict** (by share of PASS-A + PASS-B seconds):

| Verdict | Share |
|---|---|
| PASS | ≥ 90% |
| PARTIAL | 50–90% (item-level gating) |
| FAIL | < 50% |

### 3.6 Gaze latency

Every PASS video starting at the source's first frame gives a raw offset of −0.2 to −0.4 s: the gaze response lags the screen. Light bulbs, whose recording is 0.05 s shorter than the source, fixes this at ≈ 0.25 s. Offsets in `timeline_table.csv` are latency-corrected by +0.25 s.

## 4. Results

**Columns:**

- **Experiments** — independent viewing groups.
- **Shown source span** — latency-corrected source seconds.
- **Removed** — source seconds not shown.
- **Cut-locked** — p under the final mapping; n = number of cuts.
- **Pupil–luminance** — whole recording, final mapping.

| Video | Rec. (s) | Experiments | Config | Shown source span(s) | Removed (s) | Seconds passing | Cut-locked | Pupil–luminance | **Verdict** |
|---|---|---|---|---|---|---|---|---|---|
| Stars | 184.7 | E1, E2, E4, E5 | combined | 0.1–184.1 | 24.5 (end) | 100% (A 98%) | n = 122, p = .013 | r .76, p .001 | **PASS** |
| Light bulbs | 142.1 | E1, E2, E4 | combined | 0–141.9 | 0.9 | 100% (A 100%) | n = 167, p = .006 | r .64, p .001 | **PASS** |
| Immune | 388.7 | E1, E2, E4, E5 | spatial | 0–214.9; 236.4–265.4; 302.4–328.4; 343.2–420.2; 424.1–465.1 | 80.7 (mid-video) | 77% (A 45%) | n = 11, p = .65 | r .43, p .001 (0–240 s only) | **PARTIAL** |
| Internet | 369.0 | E1, E2 | combined | 0–368.9 | 23.0 (end) | 100% (A 65%) | n = 9, p = .001 | r .39, p .001 | **PASS** (v1: PARTIAL) |
| Birth rate | 150.1 | E1, E2 | combined | 0–149.9 | 3.2 | 100% (A 100%) | n = 17, p = .001 | r .62, p .001 | **PASS** |
| Mosquitoes | 261.0 | E3, E4 | temporal | 10.6–271.6 | 39.2 (start and end) | 100% (A 23%) | circular | r .34, p .001 (180–240 s r .69) | **PASS** (v1: PARTIAL) — flagged |
| Related | 362.8 | E3, E4, E5 | combined | 2.9–364.9 | 23.0 | 100% (A 99%) | n = 30, p = .001 | r .65, p .001 | **PASS** |
| Work-energy | 342.6 | E3 only | combined | 1.4–343.4 | 5.2 | 100% (A 82%) | n = 56, p = .033 | r .58, p .001 | **PASS** (substitute criterion) |
| Capacitors | 385.5 | E3 only | combined | 1.2–386.2 | 1.7 | 100% (A 31%) | n = 42, p = .001 | r .18, p .001 | **PASS** (substitute criterion) |
| Planets | 262.4 | E3 only | combined | 7.5–269.6 | 16.8 | 100% (B 100%) | no cuts | uninformative | **PASS-B only** (substitute; single signal) |
| Enzymes | 268.4 | E3, E4 | combined | `AAZ03aScPr8` 5.0–144.9, then `lkRZKqDdwzU` 50.0–177.9 | 80.5 | 99.6% (B) | no cuts | uninformative | **PASS-B only** |

**Overall:** 10 PASS, of which 2 rest on tier-B evidence only; 1 PARTIAL (Immune); 0 FAIL. Every development video passes, with the qualifications in §6.

### 4.1 Enzymes: the mismatch is explained

The recording is not the 192 s video it is listed as. It is an **edited concatenation of two eHow videos by the same presenter**:

- `AAZ03aScPr8` from 5.0 s to 144.9 s: the source minus its eHow intro and outro.
- Then `lkRZKqDdwzU` from 50.0 s to 177.9 s.
- The source switch is at recording 140 s (bootstrap 95% CI 140–140).
- Durations close: 139.9 + 127.9 = 267.8 s against 268.4 recorded.

Face validity [F]:

- The `AAZ03aScPr8` part ends at the presenter's sign-off ("…it lowers the activation energy, I'm Robin Higgins…").
- The `lkRZKqDdwzU` part begins exactly at "…the first we're going to review is pH…". The editor removed that video's redundant 50 s review of activation energy, which the first video had just taught.
- The item bank fits the split: items 7, 9, 10 and 11 (activation energy, alcohol → aldehyde, graph items) fall in the first part; items 2–6, 8 and 12 (pH, temperature, concentration, saturation) in the second.

The plan's G-TL clause ("the Enzyme duration mismatch must be explained … or that video is excluded") is satisfied. The supporting evidence is tier B: replicated in E3, E4 and both learner halves with 100% agreement, but the validators are uninformative for a presenter at a glass board.

### 4.2 Mosquitoes

The cut-based mapping (+10.5 s) is the only physically plausible one. The spatial signal's "staircase" path starts before the video, so it is inadmissible; it is the signature of slow gaze drift correlating with a talking-head video.

Supporting evidence:

- The mapping places the recording start on the first narrated sentence ("Mosquitoes suck…") and the end right after "Thanks for watching this episode of SciShow News". The Patreon outro was removed.
- It gives a strong cut-locked response in E3 (r = .21) and E4 (r = .32) separately, in both 0–180 s and 180–261 s, all p ≤ .007. This is partly out of sample, since a single global offset was fitted.
- Pupil–luminance confirms 180–240 s (r = .69). In 0–180 s it is uninformative for the final mapping (p ≈ .9), with weak (p .05–.10) support for the inadmissible spatial path.

Under the first validator rule (v1), Mosquitoes was PARTIAL (54%).

**Flag:** item anchors in 0–180 s carry timeline tier B.

### 4.3 Related

The constant +2.6 s mapping:

- is replicated by E3, E4 and E5;
- is best or tied in every 60 s pupil–luminance block (r .34–.84);
- gives a cut-locked p = .0005.

An alternative temporal path (−2.0 s for 0–58 s, +5.5 s after 268 s) is inadmissible and fits the pupil response worse (r .39 vs .65).

The recording ends on "Next time.", and the channel outro was removed.

### 4.4 Immune — PARTIAL

| Recording span | Status | Evidence |
|---|---|---|
| 0–215 s | PASS | Shown source 0–214.9 s. Replicated in all four experiments; pupil–luminance r .59–.80 in 60–240 s |
| 215–388 s | Uncertain | About 77 s of mid-video source material removed in several pieces, with wide edit-point CIs ([237, 244], [270, 294], [335, 347]) |

The configurations disagree after 215 s by up to 3.3 s, and the validators are weak or inconsistent there.

**[F] Content cross-check.** Item 8 asks about antibodies. Its supporting narration (source 272–295 s) lies in material the mapping marks as *not shown*. So either the item writers worked from the full video, or the post-215 s mapping is wrong; the evidence cannot decide which.

**[D]** Immune items whose evidence lies after source 215 s are not anchorable: items 2, 7, 8, 9, 10. Items 1, 3, 4, 5, 6, 11 and 12 are.

## 5. Audit history (what changed after looking)

Every change below was made before any anchor was built. All are outcome-free.

| Step | Change | Reason | Effect |
|---|---|---|---|
| 1 | Unconstrained Viterbi → monotone path | Non-monotonic excursions are physically impossible for an edited stimulus | Stars, Internet, Work-energy, Capacitors and Planets go from 3–9 spurious segments to 1 |
| 2 | Edit penalty 0.25 → 0.5; drift 2 → 1 bin per window | Fewer spurious edits; drift tolerance absorbs frame-rate jitter only | Sensitivity runs at 0.25 and 1.0 are recorded in `timeline_audit_summary.json` |
| 3 | Validators added (cut-locked, pupil–luminance) | The rule had no signal independent of the alignment scores | Mosquitoes temporal mapping supported; Related constant mapping confirmed; Immune's second half shown to be weak |
| 4 | Validator rule v1 → v2 | v1 let **inadmissible** paths veto (Internet 180–240 s: the impossible temporal path reached p = .021 there), ignored the circularity of cut-locked tests for cut-based paths, had no multiplicity control (4 mappings × ~6 blocks at α = .05) and ignored edit-point uncertainty | v2: only admissible alternatives can contradict, at p < .01 and with stronger support; seconds inside an edit-point CI fail. v1 verdicts are kept in the outputs: Internet and Mosquitoes PARTIAL under v1 |

## 6. Gate verdict and residual risks

**G-TL (as operationalized): passed for 10/11 videos and for all 9 development videos. Immune is PARTIAL.**

| Residual risk | Affected | Mitigation |
|---|---|---|
| Single experiment (G-TL substitute criterion) | Work-energy, Capacitors, Planets | Halves + sessions replication; validators for Work-energy and Capacitors |
| Tier-B-only evidence (no independent validator) | Planets, Enzymes, most of Mosquitoes 0–180 s | Anchor-level timeline tier recorded; anchor-shift sensitivity (±5/±10 s, plan §18) is mandatory in Stage 2 |
| Immune second half | Immune items 2, 7–10 (locked/reserved content only) | Excluded from anchoring |
| Gaze latency (≈ 0.25 s) and ±2 s tolerance | All | Irrelevant at second-scale anchors (median span 10–32 s) |

**Use of locked-cohort viewings.** The alignment pooled peer gaze from all experiments, including E4 session 2 and E5 session 2. It used **no outcomes** and estimates a property of the stimulus file, not of learners. It informs no method choice. For every video shown in a locked cohort (Stars, Immune, Related), the mapping is independently reproduced by non-locked groups (E1, E2, E3).
