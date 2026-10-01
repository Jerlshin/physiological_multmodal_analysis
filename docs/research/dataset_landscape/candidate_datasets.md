# Candidate dataset catalogue

Evidence cutoff: **2026-10-01**. Thirty individually documented candidates/families: 26 in the main matrix plus four screening/longitudinal notes. This is a curated landscape, not an exhaustive catalogue of every physiological dataset.

Read [the decision](selection_decision.md) first, then [the matrix](comparison_matrix.md). Exact source links, rates, labels, missingness, access and scientific limits live in each note. **NV** means not verified; it is not a negative finding.

| Dataset / note | Disposition |
|---|---|
| [BBBD — Brain, Body, and Behavior Dataset](dataset_notes/bbbd.md) | primary recommendation, using corrected release 1.1; file-level audit required before modelling. |
| [Digit span / OpenNeuro ds003838](dataset_notes/digit_span_ds003838.md) | strongest general alternative; preferred if experimental control becomes the main priority. |
| [DREAMT](dataset_notes/dreamt.md) | strongest clinical/sleep alternative; could become primary if clinical wearable validation is prioritized. |
| [LLaMAC](dataset_notes/llamac.md) | strongest recent broad affect candidate with over 100 released participants. |
| [SENSE-42](dataset_notes/sense42.md) | strong recent HCI alternative; smaller cohort and restricted/consent-dependent coverage. |
| [BALLADEER](dataset_notes/balladeer.md) | strong pediatric clinical candidate; not primary because coverage and diagnostic confounding need substantial audit. |
| [IMPROVE](dataset_notes/improve.md) | strongest direct educational-behavior alternative; weaker neural/cardiac measurement than BBBD. |
| [MMV — MultiModal Vigilance](dataset_notes/mmv.md) | strong repeated-session vigilance resource; too few people and too much label circularity for default primary selection. |
| [A Multimodal Dataset for Mixed Emotion Recognition](dataset_notes/mixed_emotion.md) | valuable affect-specific alternative; access and short trials reduce its default priority. |
| [I DARE — multimodal affective response dataset](dataset_notes/idare.md) | controlled affect candidate; short events and processed-signal uncertainty constrain cardiac research. |
| [MPD-DF — Multimodal Phenotyping Dataset of Driving Fatigue](dataset_notes/mpd_df.md) | recent driving-specific candidate; label construction is the main methodological limitation. |
| [DEJA-VU — emotional transitions in virtual reality](dataset_notes/dejavu.md) | transition/VR alternative; synchronization and sample size prevent primary selection. |
| [Enhanced Valence-Arousal Multimodal Emotion Dataset](dataset_notes/enhanced_va.md) | recent emotion/stress candidate; strong protocol and evaluation confounds. |
| [Public-exhibit emotion physiology dataset](dataset_notes/public_exhibit.md) | strongest scale/diversity challenge to laboratory affect datasets; not primary for precise multimodal neuroscience. |
| [EmpathicSchool](dataset_notes/empathicschool.md) | useful stress/video–wearable candidate; small and already benchmarked. |
| [WEMAC](dataset_notes/wemac.md) | valuable women-focused affect resource; does not provide simultaneous brain/eye/body breadth. |
| [MultiPhysio-HRC](dataset_notes/multiphysio_hrc.md) | promising 2025/26 industrial task-transfer resource; not selected due to confounds and incomplete release audit. |
| [EMBRACE](dataset_notes/embrace.md) | promising social/motor hyperscanning resource; hold pending access/format audit. |
| [SEED-VII](dataset_notes/seed_vii.md) | strong recent EEG–eye affect benchmark; narrower physiology and small N. |
| [COG-BCI](dataset_notes/cog_bci.md) | strong older repeated-session control/transfer comparator. |
| [CASE](dataset_notes/case.md) | older reference for continuous affect annotation; not selected as primary. |
| [StressID](dataset_notes/stressid.md) | credible stress/audio–video–physiology alternative; lower verification depth than finalists. |
| [K-EmoCon](dataset_notes/k_emocon.md) | naturalistic social-affect comparator, with dyadic dependence and access limits. |
| [AMIGOS](dataset_notes/amigos.md) | established affect/social-context comparator. |
| [DEAP](dataset_notes/deap.md) | essential historical comparator, not a primary novelty foundation. |
| [WESAD](dataset_notes/wesad.md) | essential wearable stress reference; unsuitable as the sole foundation for a new generic classifier paper. |
| [MAD — Multimodal Affective Database (2026 preprint)](dataset_notes/mad.md) | screened, not selected; public acquisition not verified. |
| [Multimodal n-back with music](dataset_notes/nback_music.md) | rejected as primary because released sample is much smaller than recruitment. |
| [CognitiveLab](dataset_notes/cognitivelab.md) | promising but not acquisition-ready on evidence obtained. |
| [TILES family and 2025 sleep benchmark](dataset_notes/tiles.md) | important longitudinal alternative; secondary domain resource for this selection. |

## Interpretation boundaries

- Physiological modalities, derived outputs and behavioral labels are distinguished. Proprietary attention scores, heart rate and raw EEG/ECG are not interchangeable.
- Subject IDs alone do not guarantee independence: common videos, repeated sessions and dyads can link train and test data.
- New data release does not erase prior scientific use of the same recordings.
- All potential ML opportunities in notes are provisional; no model architecture, final target or paper claim has been selected.
