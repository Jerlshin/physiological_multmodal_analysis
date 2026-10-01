# Evidence artifacts and reuse rights

All artifacts were prepared on 2026-10-01. They are small metadata extracts and research tables; no participant biosignals, face videos, full copyrighted articles or modelling outputs are stored here.

| Artifact | Source / rights / interpretation |
|---|---|
| [search_log.md](search_log.md) | Executed query strings and returned titles/links; includes rejected/noisy discovery results. A lead is not an accepted source. |
| [bbbd_cohort_table.md](bbbd_cohort_table.md) | Adapted BBBD paper Table 1, article CC BY 4.0 with attribution; additional duration facts from official mirror. Useful replacement for copying a promotional “all modalities” figure. |
| [bbbd_release_manifest.md](bbbd_release_manifest.md) | Corrected archive file names/bytes/declared MD5, sourced from public repository metadata. Local content checksums not verified because full archives were not downloaded. |
| [bbbd_metadata_snapshot.json](bbbd_metadata_snapshot.json) | Selected Zenodo metadata, release 1.1, CC BY 4.0 data license. |
| [digit_span_metadata_audit.json](digit_span_metadata_audit.json) | Aggregate availability/demographics from public CC0 participant metadata; source hash and mutable-ref limitation retained. No subject rows copied into the report. |
| [balladeer_metadata_snapshot.json](balladeer_metadata_snapshot.json) | Figshare v2 metadata; data CC BY 4.0. Article has different rights (CC BY-NC-ND), so its figure/table artwork is not copied or adapted here. |
| [llamac_metadata_snapshot.json](llamac_metadata_snapshot.json) | Figshare v6 data/code record, CC BY 4.0; file bytes summarized. |
| [mixed_metadata_snapshot.json](mixed_metadata_snapshot.json) | Restricted Zenodo; no public license/files in the inspected API response. Empty file list does not mean empty data. |
| [dejavu_metadata_snapshot.json](dejavu_metadata_snapshot.json) | Open CC BY 4.0 archive; compressed data/code bytes differ legitimately from unpacked size. |
| [sense42_metadata_snapshot.json](sense42_metadata_snapshot.json) | Restricted record, CC BY 4.0 metadata; file size hidden. Code CC0 is a separate license. |
| [embrace_metadata_snapshot.json](embrace_metadata_snapshot.json) | Open CC BY 4.0 record; small visible repository ZIP does not prove full raw-signal delivery. |

Useful figures not copied:

- [BBBD paper](https://doi.org/10.1038/s41597-026-07215-1): protocol and coverage illustrations establish which experiments have which sensors; local factual table preserves the decision-relevant content.
- [BALLADEER Table 1](https://www.nature.com/articles/s41597-026-06758-7/tables/1): task-by-device counts expose incomplete intersections; article CC BY-NC-ND, so source/citation and discussion are retained instead of adapted artwork.
- [IMPROVE](https://doi.org/10.1038/s41597-025-05681-7): acquisition layout/protocol illustrates the 16-source setup and phone groups; article CC BY-NC-ND, linked rather than adapted.
- [DEJA-VU](https://doi.org/10.1038/s41597-026-07456-0): transition/protocol figures explain sequence and coarse temporal alignment; article CC BY-NC-ND, linked rather than adapted.
- [Public-exhibit study](https://doi.org/10.1038/s41598-026-48250-7): classifier/quality-filter figures show how stimulus selection alters apparent discrimination; article CC BY-NC-ND, linked/described only.

JSON snapshots preserve selected facts and the hash of the full retrieved metadata response. They are not byte-for-byte archives of the server response, and cannot substitute for its original JSON in a hash comparison. Bibliography links allow a later investigator to re-retrieve and compare the cited records. No dataset's data license is inferred from its article or code license.
