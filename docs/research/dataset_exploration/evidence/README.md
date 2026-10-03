# Machine-readable evidence

**Gate follow-up — 2026-10-02:** New gate_closure_* artifacts retain paired/all-ECG transfer tests, OSF hash-verified inputs, content maps, historical aggregate comparisons and an explicit behavioral eligibility view. The original quiz tables are unchanged. The generating module is bbbd_audit.gate_closure; report generation automatically reapplies this status. [Evidence and verdict](../gate_closure.md).

Evidence is generated from checksum-verified BBBD 1.1 ZIPs by `src/bbbd_audit/`, using `audit_config.json`. Raw source snapshots and author-code ZIP are attributed to the official dataset/code sources. No model or evaluation split exists.

| Artifact | Scientific role |
| --- | --- |
| download_manifest.json / zenodo_record_22968459.json | Official identity/sizes/MD5; local SHA-256 and download timestamps |
| archive_members.parquet | Complete canonical ZIP directory, file sizes/CRC/offsets |
| canonical_manifest.parquet / missing_files.parquet | Physical files plus explicit design/unexpected absent records, modality/outcome joins and validity masks |
| exposure_tensor.parquet / modality_intersections.csv | Grouping units, coverage, provisional QC and exact common-grid valid durations |
| quiz_items.parquet / quiz_video_outcomes.parquet / quiz_aggregate_comparison.parquet | Independent score reconstruction, duplicate quarantine, partial/exact denominators and rounding |
| participant_quiz_join_ledger.csv / participant_traits.parquet / phenotype_coverage.json | Cardinalities, unmatched IDs, observed traits and raw/item-derived coding |
| channel_qc.parquet / eeg_contamination_map.parquet / peak_qc.parquet | Channel statistics, PSD/band/line summaries, RR/RMSSD and peak anomalies |
| files/channels/peaks/masks/events/metadata_expN.parquet | Resumable experiment QC shards; masks keep original seconds intervals; metadata preserves contradictions |
| physiology_flat_runs.parquet | Dataset-wide finite exact-constant regions in raw ECG/EOG/respiration/head |
| timing_boundaries.parquet | Sample-count agreement; does not estimate native clock residuals |
| missingness_map.parquet / *_diagnostics.csv | Design versus loss versus QC, descriptive selection checks |
| exploratory_*.csv/parquet | EXPLORATORY modality/person/video summaries; no significance or performance optimization |
| leakage_risk_register.json / independence_graph.json / research_feasibility.csv / p0_gate_status.csv | Formal future-design constraints and bounded scientific judgments |
| disk_usage.jsonl / retention_manifest.json / validation.json | Allocated versus logical disk accounting, retention and verification |
| audit_execution_code.zip / audit_pipeline_source.zip / generating_source_fingerprints.json | Exact full-signal execution source, final deterministic pipeline source snapshot and per-file SHA-256 fingerprints |

Parquet uses Zstandard compression. Exact values are retained in tables; report decimals are rounded for readability. Binary validity masks use `numpy.packbits(..., bitorder='little')`; truncate unpacked masks to `qc_sample_count`. True means invalid/corrected, false means eligible under the audit definition. Exact intersection durations OR all selected modality masks over the shortest common released-grid length. This does not recover unreleased artifact masks or alignment residuals.

The full archive is immutable, while derived evidence is reproducible. Metadata descriptions and upstream code are evidence of declarations/possible operations, not proof that all options were executed. Scientific classifications are explicit in the reports. Date/timestamp values use 2026-10-02 audit date and UTC machine timestamps; user-facing local timezone is Europe/Berlin.
