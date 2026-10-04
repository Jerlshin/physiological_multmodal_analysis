# M07 — External validation feasibility

2026-10-04. A repository/API audit was delegated and then spot-verified by the lead investigator.

- **Re-checked against the OSF API:** John 2025's licence (CC-BY 4.0), the 516-file / 6.03 GB inventory and folder counts, and the workbook sheets `LeVi`, `POIs`, `Quest` with 7 pretest and 13 posttest item columns.
- **Evidence files:** the [John OSF manifest](evidence/external/john2025_osf_4rn5q_file_manifest.json), the [Bühler OSF manifest](evidence/external/buhler2024_osf_4qkvx_file_manifest.json) and the [audit notes](evidence/external/delegated_audit_notes.md).
- **Not downloaded:** no external participant-level data were placed in the repository.

**Process deviation (recorded).** The delegated check exceeded its self-imposed 50 MB download limit. The Lallé GitLab server ignored HTTP range requests, so two zips (82 MB and 86 MB) arrived in full. They were listed and then deleted. Nothing was retained or analysed.

## Verdict

- **An ocular-only external replication of regime A is credible now (John et al. 2025).**
- **No accessible dataset supports a tri-modal replication or an external new-content (B) test.** Those claims require a new prospective cohort.
- M07 is therefore **partially satisfied**. It does not block baseline implementation, but it bounds which claims a Q1 paper can make.

## Candidates

V = verified at the repository level; R = reported in the paper only; U = unresolved.

| Candidate | Access / licence | People | Content units | Sensors | Outcome | Independence from BBBD | Usable for |
|---|---|---|---|---|---|---|---|
| **John et al. 2025**, Sci Rep 15:20291, [OSF 4rn5q](https://osf.io/4rn5q/) | V: public, **CC-BY 4.0**; 516 files / 6.03 GB | V: 121 questionnaire rows; 118 instructional-video EDF files (117 join the questionnaire). R: 105 pass the paper's eye QC | **1** instructional video ("Programming in Minecraft", ≈ 16 min). The Hitchcock clip is non-educational | V: raw **EyeLink 1000 EDF**, 500 Hz, right eye. V: ear-EEG (cEEGrid, 18 channels, 250 Hz; 4 files < 5 MB). R: no ECG | V: **item-level pretest (7) and posttest (13)**; posttest immediate (R). Plus a 0/1 utility-value condition, age, sex, mental effort | Yes: Frankfurt (DIPF/Goethe); different lab, cohort and tracker unit | **Ocular regime-A replication**, with *pretest adjustment unavailable in BBBD* |
| **Lallé et al.**, AIED 2025, [GitLab](https://gitlab.lip6.fr/mocah-public/eye_tracking_green_chem_video) | Public; licence file is BSD-3 (a software licence; data-reuse terms ambiguous) | 53 with quiz labels (per the delegated listing) | 1 video (7.5 min), **self-paced** with pause/seek | Tobii ≈ 60 Hz gaze and pupil | 15-item immediate quiz, items mapped to segments; per-item "already knew" | Yes: Sorbonne | Second ocular replication, **reference-free features only**: self-paced viewing breaks the shared timeline that ISC needs. Clarify terms first |
| Bodonhelyi et al. 2026 (TUM), Zenodo 14097753 | Draft, unpublished, restricted (V: API 404) | 56 (R) | 3 videos, one topic | EyeLink 1000 Plus 1000 Hz | Pre / post / 1-week (R) | Yes | Future, if released |
| Bühler et al. 2024 | V: OSF 4qkvx holds only the test PDFs; sensor data "planned" | 84 (R) | 1 lecture (60 min) | SMI 250 Hz; wristband (not ECG) | Pre / post, thought probes | Yes | Only on author release |
| IMPROVE | Signed licence (R) | 120 | Mostly reading | Tobii; NeuroSky band power about 1 Hz | Pre / post | Yes | Not a video-learning criterion |
| Madsen 2021 webcam; Adler 2025 | Public (no licence) / on request | 82–1,012; 354 | 4–5 | Webcam | Per-video answers; pre / post | **No**: Parra-lab lineage, same videos | Internal consistency only, not external |
| Liu 2023, Sauter 2022, Kok 2023, Davidesco 2023, AttentivU, Kaggle "confused", MEMA, Chen 2026 | Not public / no statement / wrong outcome / unresolved | — | — | — | — | — | Not usable now. Chen 2026 is worth an author request (needs user authorization) |

## External-validation plan (frozen principles)

1. **Primary external test: John 2025, ocular regime A.** It mirrors the BBBD gaze block exactly:
   - **Features:** the same frozen gaze features, recomputed from raw EDF with the same correction-exclusion rule:
     - gaze ISC against a *training-person* reference on the same video;
     - gaze dispersion;
     - saccade rate.
   - **Baseline:** age, sex, study condition, gaze-correction fraction.
   - **Pretest-adjusted baseline:** the same plus the **pretest** sum. This contrast is the one BBBD cannot supply.
   - **Outcome:** posttest proportion correct.
   - **Evaluation:** person-grouped 10-fold CV, repeated 20 times, with nested-CV intervals.

   The external analysis plan is time-stamped in the repository **before** the instructional-video EDF and outcome files are downloaded: [external_analysis_plan_john2025.md](external_analysis_plan_john2025.md). The confirmatory external contrast is *Skill(gaze) > 0 beyond the pretest-adjusted baseline*.

   The paper's 105-person QC set is post hoc. We apply our own frozen QC rule and report both counts.
2. **Secondary external test: Lallé 2025**, reference-free gaze features only, after reuse terms are clarified.
3. **Cross-cohort transfer** (BBBD → John): models trained on BBBD scale-free gaze features, with outcome standardized within cohort. It is labelled **transport**, not new-content validation, because device, language, content length and test all change at once.
4. **No pooling** of external cohorts with BBBD to inflate N. External results are reported per cohort.

## What only a prospective cohort can provide

The following are out of reach of any verified resource:

- tri-modal (EEG + ECG + eye) external confirmation;
- content-population inference;
- separation of prior knowledge from learning.

Design requirements, derived from the [precision analysis](precision_and_independence.md):

- **many more independent content units:** B's per-video spread and few-cluster coverage failure at 8 videos imply a minimum in the low tens, to be set by a dedicated simulation before collection;
- an item-level pretest and posttest, with a delayed test if retention is claimed;
- a criterion with higher per-video reliability: more items per video, or validated items;
- documented native triggers and calibration;
- a preregistered sensor-QC policy;
- an incomplete crossed learner × content allocation.

This is a recommendation (I). Ethics, recruitment and acquisition have not been started and require the user's decision.

## Actions requiring the user's authorization (not performed)

- Downloading John 2025 `/Mine` (about 4.1 GB) after time-stamping the external plan.
- Downloading the Lallé zips (about 168 MB).
- Contacting the Lallé, Kasneci/TUM, Bühler or Chen authors.
- Sending the BBBD [author query](../dataset_exploration/evidence/author_query_draft.md).
