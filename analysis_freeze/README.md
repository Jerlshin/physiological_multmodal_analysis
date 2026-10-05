# Analysis freeze and outcome-access authorization

This folder implements the protocol's analysis-freeze condition ([protocol §16](../docs/research/experimental_design/protocol.md)) as a machine-checked gate. Real quiz outcomes are readable **only** through `g01r.outcomes.load_real_outcomes`. That function refuses access unless both of the following hold:

1. `AUTHORIZATION.json` exists in this folder and references the SHA-256 of `freeze_manifest.json`.
2. `freeze_manifest.json` still verifies against the working tree:
   - frozen documents and configuration;
   - every production source file, including the analysis registry;
   - population ledger, feature QC and validation evidence;
   - both feature tables and the signal caches;
   - every synchrony and CorrCA cache entry present at the freeze (append-only: later additions are allowed);
   - the dependency lock and the verified data archives.

The loader re-runs this check at every access, not only when the run starts.

| File | Written by | Purpose |
|---|---|---|
| `freeze_manifest.json` | `python -m g01r freeze` | SHA-256 binding of everything the confirmatory run depends on |
| `derived_cache_index.json` | `python -m g01r freeze` | SHA-256 of every synchrony/CorrCA cache entry at the freeze; bound by the manifest (IS-029) |
| `AUTHORIZATION.template.json` | this phase | Shape of the record. **It is not an authorization** |
| `AUTHORIZATION.json` | **the user only**, via `python -m g01r authorize …` after depositing the preregistration | Unlocks real outcomes; records the git commit that contains the freeze; append-only (a second record is refused) |
| `outcome_access_log.jsonl` | the outcome loader | One line per real-outcome access (set, outcome, cells, authorization hash) |

## Procedure (in order)

1. **Commit the freeze (local git).** Commit the repository state that contains this manifest. The commit hash time-stamps the analysis freeze.
2. **Deposit the preregistration.** Use [preregistration.md](../docs/research/baseline_implementation/preregistration.md), completing only its deposit-time fields (authors, the freeze commit from step 1, the date). It cites the protocol commit `ef1df1b` and the manifest SHA-256, and discloses the exploratory history. This is an external action and needs your authorization.
3. **Verify the freeze.** `PYTHONPATH=src .venv/bin/python -m g01r verify-freeze` must print `VERIFIED` and no note about uncommitted bound files.
4. **Authorize.** `PYTHONPATH=src .venv/bin/python -m g01r authorize --preregistration <DOI-or-URL> --by <name>`. It refuses unless the manifest verifies and every bound file is committed unmodified, and records the commit. Commit `AUTHORIZATION.json` afterwards.
5. **Run the first confirmatory analysis.** `PYTHONPATH=src .venv/bin/python -m g01r run --analysis H1_H2 --workers 5`.

Any change to a bound file after step 4 makes the outcome loader refuse access. A justified change must be logged as a dated deviation (protocol §16), the freeze rebuilt and a new authorization written. Because a second authorization record is refused, the old record is first moved to a dated history file as part of that logged deviation.
