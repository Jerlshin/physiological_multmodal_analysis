# Evidence scope, reproducibility and retained artifacts

Phase: 2026-10-03. The current BBBD audit is the ground truth. This pass reviewed the repository research trajectory and performed new literature discovery/comparison; it did not repeat native-signal forensics or fit a predictive model.

## Repository review scope

The reviewed trajectory includes:

1. Dataset landscape: search/selection/exclusion reports, the 30 dataset/family notes, comparison and evidence records.
2. Selected dataset: protocol, cohort/modalities/outcomes, preprocessing/quality, P01–P05 and related-paper dossiers, prior-work matrix, source registry, originality limits and open questions.
3. Empirical audit: acquisition/inventory, joins/scoring, signal QC, timing, provenance, quality masks, trait/outcome characterization, independence/leakage, feasibility, retention and validation reports.
4. The later gate-closure amendment: exact ECG scope, E2 response-provenance quarantine, corrected behavioral eligibility and current scientific denominators.
5. Global decisions, inferences and bibliography, preserving chronology and supersession.

The source manifest fingerprints **90 existing Markdown research records plus 13 decisive aggregate evidence files** at the start of the phase's global-index amendments. A fingerprint is provenance, **not** a claim that every byte in every raw archive or code snapshot was newly read. The review inherited documented primary-paper assessments and their limits rather than pretending to re-replicate all originals. Source archives, native data and historical numerical outputs remain unchanged.

## Aggregate recheck

[review_snapshot.py](review_snapshot.py) reads only existing audit Parquet/CSV/JSON inputs. It reproduces eligible memory denominators, direct provisional-QC sensor intersections and first-view/protocol subsets. It verifies the 94/324/8 tri-modal, 57/216/8 first-view and 94/327/8 reduced-sensor ceilings, and independently counts the 98 released item rows with full partial credit despite wrong choices.

Outputs: [repository_snapshot.json](repository_snapshot.json), [repository_source_manifest.json](repository_source_manifest.json). The script records 147 qualified people / 581 outcomes across all non-E2 experiments and 120 / 446 in E3–5. It does not establish participant uniqueness, native signal validity, statistical power, missingness mechanism or a predictor's usefulness.

To regenerate from the repository root:

```sh
.venv/bin/python docs/research/research_gap/evidence/review_snapshot.py
```

Regeneration will refresh the source fingerprint manifest against the then-current documents; the originally saved hashes for global indexes reflect their state before this phase's appended amendments. This is expected and does not imply an audit input changed.

## Literature evidence

[search_records.json](search_records.json) preserves all 71 literal queries and the requests/results identities from 38 saved web-tool batches. Requests may contain temporary search handles; returned primary URLs and titles support source recovery. Batches are grouped by search/read families, so this is not a reconstructed exact wall-clock trace. Returned incidental/secondary hits are discovery metadata, not scientific evidence used by default.

[literature_records.json](literature_records.json) contains the 43 curated external records and access tiers. Fourteen are FT (relevant original methods/results sections inspected), not 43 fully read papers. Primary abstracts/indexed extracts have bounded use; failed access never establishes absence. Journal/conference/workshop/preprint status is kept distinct. P01–P05/S01 and related R records retain their original repository identifiers.

No whole copyrighted articles were copied into this phase's artifacts. The register stores citations, URLs, access facts and original research analysis. No restricted paper access was bypassed, no external dataset was acquired, and no author was contacted.

## Validation and boundaries

Phase validation checks JSON parsing, local Markdown targets, unique register IDs, correspondence between curated IDs and dossiers, aggregate-count assertions, and that all eight serious dossiers contain the required appraisal fields. It is documentation/evidence verification, not a model test suite. See [validation.json](validation.json) for the actual run result.

Global research indexes receive dated amendments linking this phase. Earlier audit/source records remain historical. The phase never changes E2 exclusion, the duplicate-item quarantine, provisional QC rules, OQ-06 status or the source archives.

