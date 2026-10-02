# Open questions and evidence required next

**Dated audit disposition — 2026-10-02:** this original queue is retained unchanged. Consult [empirical P0 dispositions](../dataset_exploration/open_questions_resolved.md) and [remaining gates](../dataset_exploration/open_questions_remaining.md) for current status. OQ-01/03/04 are substantially resolved; OQ-02/05/07 have explicit bounded resolutions/quarantines; OQ-06 remains blocking. Actual-file evidence must supersede documentary expectations explicitly, not by silently editing this historical queue.

No issue below is resolved merely by choosing a more complex model. `P0` means it can invalidate basic cohort/target construction; `P1` constrains a specific scientific claim; `P2` improves contextual completeness. Source keys resolve in the [registry](evidence/source_registry.md).

| ID / priority | Question | Why it matters / present evidence | Concrete resolution artifact |
|---|---|---|---|
| OQ-01 / P0 | Do the downloaded ZIPs match selected1.1 hashes and corrections? | S03 metadata only; mutable website/mirrors may lag | Download manifest, archive checksums, version sidecars and file tree |
| OQ-02 / P0 | Do all quiz IDs map to actual participants and correct stimuli? | S04 corrections; S06 surplus IDs in 1–3 (INF-005/016) | Join cardinalities, unmatched IDs/reasons, response-key audit; no joins by row position |
| OQ-03 / P0 | How are partial scores and binary correctness related? | Different schemas, multiple selections/penalties | Recomputed item and video totals, denominator/range dictionary, randomized-option mapping |
| OQ-04 / P0 | What is the actual valid all-modality/outcome intersection? | Experiment-level availability does not imply complete cases | Person×session×video×modality availability and QC table; phenotype coverage |
| OQ-05 / P0 | Which session/task maps to which actual video/exposure? | Exp. 4 README contradictions and reused IDs | Canonical stimulus checksum/URL, local-ID mapping, block/order/event ledger |
| OQ-06 / P0 | Which exact preprocessing produced each derivative? | EEG .05/.3/.5 Hz and ECG filter discrepancies | Per-release provenance, options, software versions, native→aligned→derived trace |
| OQ-07 / P0 | Are R-peak files actual timestamps and does HRV code reproduce Figure 6? | INF-019 formula discrepancy | Column/unit/header check; RMS-RR vs true RMSSD comparison; reproduce published aggregate |
| OQ-08 / P1 | What does the pupil technical-validation result measure? | Notebook IQR versus mean-size prose | Executed code/data version and reproduced statistic (INF-020) |
| OQ-09 / P1 | Where/how severe is16 Hz contamination? | S01 author warning; no measured spectrum audit here | Per-channel/subject/session spectra and contamination mask; raw/clean sensitivity |
| OQ-10 / P1 | How accurate is cross-device alignment? | S01 common triggers/linear transform without error distribution | Trigger residuals, drift, dropped-event analysis and valid temporal precision |
| OQ-11 / P1 | Are interpolation masks complete and reliable? | S06 exports intervals; high eye correction fractions | Mask/sample coverage and longest-gap distributions, by task/person/outcome |
| OQ-12 / P1 | Are BDF padding, zeros, NaNs and channel scalings correctly distinguished? | Export code zero-pads and skips empty records | Valid-sample counts, sidecar/unit tests and cross-format comparison |
| OQ-13 / P1 | What EEG reference and participant-specific EOG montage were used? | Inconsistent mapping reported | Channel/reference provenance and empirical montage sanity checks |
| OQ-14 / P1 | What were randomization and quiz timings for4/5? | Shared source partition; descriptor allocation wording incomplete | Allocation log/protocol, block order and test/preview timestamps |
| OQ-15 / P1 | Did prior papers use the now-corrected label mappings? | All published before Sept. 2026 correction | Original OSF input hashes/subject maps and reanalysis change log; author clarification if needed |
| OQ-16 / P1 | Are there duplicate people across experiments? | Local IDs cannot answer; cohorts described separately | Recruitment/session provenance or privacy-preserving identity mapping from authors |
| OQ-17 / P1 | What is P05's dataset, validation and result? | Publisher metadata verified, methods inaccessible | Original six-page paper plus code; fill each unresolved dossier field |
| OQ-18 / P1 | What do inaccessible supplements add? | P01/P03/P04 PDFs failed retrieval | Genuine PDFs/author copies; inspect supplementary tables, filters, uncertainty and analyses |
| OQ-19 / P1 | Can questionnaire scales be pooled? | ASRS 0–4 vs1–5 prose; weighted digit span unspecified | Item recoding, recomputed subscores, instrument version; distinguish maximum span from weighted score |
| OQ-20 / P1 | Which target best isolates immediate learning performance? | E5 final score follows re-exposure; E2 baseline domain knowledge | Exposure-aware target table; pretest availability; recognize absence of delayed retention |
| OQ-21 / P2 | What are current age/sex/GPA/occupation distributions and missingness? | Table parentheses unclear; published phenotype counts historical | Deidentified aggregate metadata report, scale eligibility and missingness analysis |
| OQ-22 / P2 | Why do reported modality-hours differ across website/mirror? | EEG91.2 vs65 h; others round differently | File-derived observed/valid hours with denominator and version |
| OQ-23 / P2 | Does Exp.1 truly contain head position? | S02 vsS05/S06 conflict | Nonempty channels/units and native acquisition evidence |
| OQ-24 / P2 | Are engagement ratings and recognition/comprehension tags released? | Documented collection but absent/unclear static assets | Actual files, schema, timing and question taxonomy; otherwise explicitly unavailable |
| OQ-25 / P2 | Are native2048/500 Hz files and manual annotations obtainable? | Release raw is128 Hz; pipeline expects upstream arrays | Official native-file manifest/access terms and acquisition dates |
| OQ-26 / P2 | What are the code and video reuse licenses? | Data CC BY4 established; repository LICENSE absent; external video rights separate | Author/repository license statement and stimulus rights inventory |
| OQ-27 / P1 for foundation models | Did any candidate pretrained model already ingest BBBD/mirrors? | Public mirrored EEG can appear in training collections; occurrence not established | Exact pretraining manifest and release timestamps |

## How to close an issue

Record the inspected release/file/commit, exact evidence, result, and any changed interpretation in the inference register; preserve the earlier state. If documentation cannot settle a point, prepare a precise author query after the file audit. **No messages have been sent to dataset authors.** Author contact requires a user instruction. Waveform inspection and provenance checks can proceed in a separately authorized acquisition/audit stage; this review does not silently designate a final paper problem.
