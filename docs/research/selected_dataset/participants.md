# Participants and cohort identity

**VERIFIED FACT — release-level counts.** Values below transcribe the descriptor's Table 1; they are not counts from the ZIPs. [S02](evidence/source_registry.md)

| BBBD experiment | Recruited | Excluded | Released | Age range | Mean ± SD |
|---|---:|---:|---:|---|---|
| 1 | 27 | 0 | 27 | 18–53 | 26.74 ± 8.98 |
| 2 | 31 | 0 | 31 | 18–50 | 25.79 ± 8.13 |
| 3 | 32 | 3 | 29 | 18–57 | 25.93 ± 8.94 |
| 4 | 46 | 3 | 43 | 18–45 | 25.09 ± 6.49 |
| 5 | 50 | 2 | 48 | 18–49 | 25.71 ± 7.98 |
| Total | 186 | 8 | 178 | 18–57 | 25.79 ± 7.93 |

Table 1 appends (17), (21), (21), (24), (26), total (109), to final counts without defining the parentheses in the inspected caption. P01 explicitly reports 17 females in its first cohort, but this alone does not verify all current-release sex counts. Retain these as uninterpreted table values until `participants.tsv` is audited. Website Exp. 2 says 32 in places; do not silently replace Table 1's 31. [S02; S05; legacy U02/U03]

**VERIFIED FACT — recruitment/ethics.** Recruitment used Craigslist in New York City and CCNY student mailing lists. Compensation was $20/hour; visits lasted approximately 1–2 hours. Participants consented under CCNY IRB 2017-1175-CCNY. This is a convenience adult sample, not a representative school-age, clinical or population sample. [S01 Methods]

**OPEN QUESTION — exclusions.** The descriptor gives eight final exclusions and examples of incomplete sessions or poor data quality, but a complete person-by-person reason ledger and thresholds across all modalities have not been established. Publication-specific exclusions differ: P02's video ECG analysis retained 27 of 31 after four poor recordings; P03 retained 92 from its new 96-person combined cohort and 29 each from earlier cohorts. These are historical analysis sets, not contradictory proofs that the corrected release must have those counts. The reason and consequences of Exp. 5 sub-09 removal need a provenance record. [S01; S04; P02 STAR Methods; P03 Methods]

## Earlier paper cohorts are not new independent samples

| Source and local numbering | BBBD mapping | Historical N / caveat |
|---|---|---|
| P01 lab Experiments 1, 2, 3 | BBBD 1, 2, 3 | 27, 31, 30 reported in lab cohorts; current BBBD 3 has 29 |
| P01 classroom / at-home studies | Outside current BBBD five experiments | 82 classroom; 1,012 at home; do not add to BBBD N or interpret as BBBD 4/5 |
| P02 Experiment 2 | BBBD 2 ECG subset | 31 recruited, 27 ECG analyses |
| P02 Experiments 1, 3, 4 | Outside BBBD | Auditory-story/clinical cohorts; cardiac–recall result cannot automatically be assigned to BBBD |
| P03 Experiment 1 | Combined source behind BBBD 4 and 5 | 96 recruited, 92 retained; historical 43 + 49, versus current 43 + 48 |
| P03 Experiment 2 | BBBD 3 | 32 recruited, 29 retained |
| P03 Experiment 3 | BBBD 2 | 31 recruited, 29 retained |
| P04 four experiments | BBBD 2–5 | 31 + 29 + 43 + 49 = 152, versus current 151 |

P03's written recruited total of 158 is inconsistent with 96 + 32 + 31 = 159; use its per-analysis Ns and retain the discrepancy. EEG, eye and outcome complete cases also differ within papers. Numeric subject IDs repeat by experiment; a join must use `(experiment, participant_id)` and an explicit historical-to-release mapping. Shared membership across papers means published “replications” are not all independent new evidence. [P01–P04; INF-003]

## Participant metadata and questionnaires

S06 `bbbd_generate_bids_descriptors.m` writes `participant_id`, `species`, `Sex`, `Age`, `Occupation`, `Tired`, `Study_time`, `GPA`, `Caffeine`, `Occupation_field`; Experiment 2 adds `Hearing`. Age is years, GPA self-reported, caffeine is time since last caffeine in hours. Tiredness has five ordered labels (very awake through very tired), but source coding differs: numerical codes in some experiments versus strings in others. `Study_time` is in hours, with reference period unresolved. `Hearing` is generated as “Yes” for all Exp. 2 rows in this code: it is not independent evidence of a clinical hearing examination. [S06 generator; INF-004]

ASRS and digit-span reference files exist for 2–5. The questionnaire page describes 18 ASRS items and alternative screener/full and symptom-subscale scores; these are self-reported traits, not diagnoses. GPA availability and missingness are selective. P04 reports 149 ASRS and 147 working-memory observations; 42/152 did not report GPA. Its methods retain 123 college-eligible records and impute 13 missing GPAs with a median, consistent with 110 observed GPA values. These historical counts must not be reused as current-release coverage. [P04 Methods/Limitations; S05]

## Direct repository metadata audit

**VERIFIED FACT — repository only (INF-005).** The pinned reference TSVs contain the following distinct IDs. Each ASRS file has nonmissing values in all 18 item columns; item validity and score consistency were not tested. No raw participant records are copied into this review. [Aggregate audit](evidence/repository_metadata_audit.json)

| Experiment | Released N in paper | Quiz IDs (rows) | ASRS IDs | Digit-span IDs |
|---|---:|---|---:|---:|
| 1 | 27 | 31 (3,286) | — | — |
| 2 | 31 | 34 (3,604) | 27 | 29 |
| 3 | 29 | 32 (2,304) | 32 | 29 |
| 4 | 43 | 43 (1,548) | 43 | 43 |
| 5 | 48 | 48 (1,728) | 48 | 48 |

Exp. 5 sub-09 is absent from all three inspected reference files. Counts alone do not establish that remaining IDs correspond correctly to signals. Surplus quiz/ASRS IDs in 1–3 may represent pre-exclusion or incorrectly associated records; the reason remains OPEN. Validate one-to-one/many-to-one joins against corrected release metadata before constructing outcomes. Missingness is modality-, phenotype- and version-specific, not a single global participant mask.
