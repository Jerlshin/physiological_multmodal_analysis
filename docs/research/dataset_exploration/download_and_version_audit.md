# Download and version audit — 2026-10-02

**EMPIRICALLY VERIFIED IN THIS AUDIT.** All five archives from [Zenodo record 22968459](https://zenodo.org/records/22968459), DOI 10.5281/zenodo.22968459, version 1.1, publication date 2026-09-25, were downloaded, streamed through MD5 and SHA-256, and atomically promoted from resumable `.part` files. Total verified canonical bytes: **26,973,110,601**. Official license metadata says CC BY 4.0.

| archive | local_bytes | members | member_bytes | official_checksum | sha256 |
| --- | --- | --- | --- | --- | --- |
| experiment1.zip | 893268919 | 3690 | 892366871 | md5:419a7468c4e60f052ab7820f3c9ffd4b | 0698ad5018eb88793ae80aacd7bb22f271c0ec8805e14cc7c9a969c7519079f7 |
| experiment2.zip | 5601886507 | 8994 | 5599789317 | md5:e9671316f97e1c3ec1d86a03e0a1ab28 | e810e7b7a144da0a27171efb78823b07c07502348284a0ba67638b0708bdf5af |
| experiment3.zip | 7966970285 | 9872 | 7964570671 | md5:adbe5c4766253d6be7aba530ac820ac9 | e804caa1c14de8b5502a60f66f925aadbf4b914ed447863d7aa72a2e0c473fef |
| experiment4.zip | 5466148546 | 8788 | 5463994648 | md5:0842a88740769449ce92b5e5269f6b70 | fe0eecb9f3f03c676aec3b1a2894ec0ca5fcde4263738f3637cc7d3144ca07f7 |
| experiment5.zip | 7044836344 | 9907 | 7042465654 | md5:cc9bf98d80ad8399cff409e13fb448c0 | ec108ca955de9ee2d05a3a55b1de79173fbef7220411485414e324b019231dfb |


Sources and UTC start/completion timestamps: [download_manifest.json](evidence/download_manifest.json). [Exact API snapshot](evidence/zenodo_record_22968459.json); [official correction changelog snapshot](evidence/official_changelog.html). The API's five objects establish independent per-experiment acquisition. One MiB/64 KiB range probes inspected the ZIP directories and small metadata before full transfers. Sequential transfer was replaced by six bounded 16 MiB range workers, reusing the completed prefix. Each worker writes into a single archive, syncs it, and records a local chunk hash. Retried 429 responses did not invalidate final official checksum matches. There are no duplicate full-data transfers or extracted waveform trees.

Canonical ZIPs are read-only under `data/bbbd/canonical_source/` and excluded from Git. Source files were never edited. Inner `dataset_description.json` names retain “1.0.0”; that is an **empirically observed contradiction**, not grounds to relabel checksum-matched 1.1 bytes as an older download. [Release versus pinned code fingerprints](evidence/release_vs_code_quiz_fingerprints.json) show exact Exp.4/5 quiz byte identity; Exp.1–3 differ in serialization but match after parsing and key sorting. A code commit date alone does not prove correction absence.
