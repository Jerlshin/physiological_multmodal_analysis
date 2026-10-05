# Freeze finalization and preregistration package — G01-R

2026-10-05. This pass makes the [analysis freeze](analysis_freeze.md) and the [preregistration](preregistration.md) publication-grade, without changing the frozen scientific design. Decisions are logged as BID-018…BID-025 and the facts as BII-012…BII-014 ([decision log](../research_gap/decision_log.md), [inference register](../research_gap/inference_register.md)).

**No real quiz outcome was read, inspected or modelled. No physiology–outcome association was computed.** Nothing was committed, deposited, sent or downloaded.

## Verdict: **READY TO COMMIT AND PREREGISTER**

- The working tree verifies against the rebuilt freeze manifest (SHA-256 `a2594996ac122348ffacff8a0a100f7dc035aa6848c7df23b0ca939e310f2149`).
- The preregistration agrees with the protocol, the implementation specification, the configuration and the registry on every element reviewed in §2.
- The outcome lock holds and is now stricter (§3).
- The one clarification (IS-028, how H3 is read) was confirmed by the user on 2026-10-05 and recorded as final (BID-026). It changes no computation.

## 1. What was reviewed

The preregistration draft was checked line by line against:

- the frozen [protocol](../experimental_design/protocol.md) v1.0 (commit `ef1df1b`), the [estimand](../experimental_design/estimand_and_hypotheses.md), the [evaluation contract](../experimental_design/evaluation_contract.md) and the [population ledger](../experimental_design/analysis_population.md);
- the [implementation specification](implementation_spec.md), `configs/g01r_protocol_v1.toml` and `src/g01r/registry.py`;
- the code paths that produce each confirmatory number: `analysis.run_A`, `inference.h1_decision`, `metrics.regime_A_report`, `models.FAMILY`, the outcome loader and the freeze gate.

The freeze manifest was checked against everything the first confirmatory run reads.

## 2. Consistency review

| Element | Frozen source | Implementation | Draft preregistration | Final status |
|---|---|---|---|---|
| H1 | Protocol §1, §11; estimand §5–6 | Registry `H1`: M5 vs M2, PAS-core, exact, regime A; block RF + SYN residualized on content, C, Q | Correct | Consistent; Ŝ (R = 50) and repetitions 1–10 for the test now stated |
| H2 family | Protocol §1, §11; contract §6 | `H2a–d`; `holm_family` in the configuration | (b–d) given only as "blocks over M2"; tested blocks not stated | Fixed: models, blocks and nuisance sets stated; H1 and H2 declared separate families |
| Populations | Protocol §3; M03 | `expected_counts`; reproduced cell for cell | No per-experiment split; H3.5 and transport sets missing | Fixed: full table, including H3.5 (68 / 234 / 7) and E4-core |
| Eligibility, QC, exclusions | M03; audit `basic_qc` | `population.py` (whitelisted columns) | Absent | Fixed: tested-cell definition, eligibility, the QC thresholds, the quarantined E3 cell, exclusions not made |
| Outcome | Protocol §4 | `OUTCOME_COLUMNS` | Correct | Consistent |
| Access regimes | Contract §2 | IS-010, IS-012; registry regimes | Correct but thin | Consistent; joint hold-out of the shared video and the C half split stated |
| Features, Q, C, missing data | Protocol §6 | IS-002…IS-011; configuration | Correct | Consistent; the 60-s rule and the Q indicators stated |
| Models | Contract §5 | `models.FAMILY` | **No model table** | Fixed: all 11 model specifications, with roles |
| Pipeline and resampling | Protocol §8; contract §3 | `pipeline.py`; IS-009, IS-013 | Correct | Consistent |
| Metrics | Protocol §10 | `metrics.regime_A_report` | Secondary metrics missing | Fixed |
| Inference and decision table | Protocol §11; estimand §6 | `inference.py`; IS-014, IS-025, IS-026 | Correct | Consistent; p-value formula, U₃ definition and B/C bootstrap size stated |
| Detection fallback | EDD-009; IS-027 | `validation_verdict.json` → permutation | Correct | Consistent |
| H3 robustness | Protocol §13 (7 analyses, estimate and interval, "no new tests"); estimand §5 (6 analyses; "keeps its sign **and its decision category**") | Registry H3_1…H3_7: interval only, no test, no futility bound | Restated the protocol | **Inconsistency between two frozen documents.** Resolved by IS-028 in favour of the protocol and the code. Confirmed by the user; the estimand carries a dated clarification (BID-026) |
| Stopping and futility | No interim analysis in any frozen document | Order H1 → H2 → H3 → descriptive | Silent. The readiness verdict said the order "allows stopping after any stage", which could be read as permission to leave stages unreported | Fixed: no interim analyses, no stopping for efficacy or futility, every stage completed and reported; "futility" defined as the U₃ bound |
| Descriptive and exploratory | Protocol §14; contract §5 | Registry D_*, X_explanatory, S_identity_probe | Explanatory model and identity probe missing | Fixed |
| Reporting commitments | Protocol §15; contract §7 | Report builder | Correct | Consistent; failed analyses reported, not replaced |
| Deviations | Protocol §16 | Gate refuses any changed bound file | Correct | Consistent |

## 3. Findings outside the documents, and what changed

| # | Finding | Risk | Change |
|---|---|---|---|
| F1 | `test_run_refuses_without_authorization` calls `g01r run --analysis H1_H2` against the real authorization path | **After authorization, running the test suite would have started an unintended real-outcome confirmatory run**, hours long, under a test process | Both authorization-dependent tests now use an empty temporary record path (BID-019) |
| F2 | The synchrony and CorrCA disk caches (≈ 7,900 synchrony entries, 71 CorrCA units, 2.1 GB) feed the confirmatory run but were not bound. `features/synchrony.py` was last edited 18 s before the first manifest, after most entries were written | Stale or altered cache entries would enter the confirmatory run unverified | Recomputed with the frozen code: all bit-identical (71/71 CorrCA units and 740/740 synchrony plans bit-identical: all 500 PAS-core regime-A splits, 100 random cached nested-CV plans (M2 vs M5) and 20 cached outer splits for each of 7 other regime-A set/route combinations ([cache_consistency.json](evidence/validation/cache_consistency.json))). Entries present at the freeze are bound append-only (IS-029). The "delete the cache for a cold run" advice was corrected: deleting now blocks access (BID-020) |
| F3 | `authorize` did not require the freeze to be committed and did not record a commit | The preregistration could cite a commit that does not contain the authorized state | `authorize` refuses unless every bound file is tracked and unmodified, and records `git_commit` (BID-021) |
| F4 | The outcome loader trusted the `Authorization` object it was given | Any code path could construct a "verified" object | The loader re-reads the record and re-verifies the manifest at every access |
| F5 | The dependency lock was not bound | The exact environment was recorded but not frozen | `requirements-baseline.lock` is bound; `verify-freeze` prints any drift of installed versions (not enforced) |
| F6 | `git_state` dropped the first two characters of the first dirty path (`.gitignore` → `gitignore`) | Cosmetic provenance error | Fixed |
| F7 | The global decision log said BID-001–016 while BID-017 existed | Broken trail | Fixed |

The manifest was rebuilt (schema 2) because bound code and documents changed. It was rebuilt once more after the user confirmed IS-028 (BID-026), because the estimand and the implementation specification are bound. The superseded manifests (`38fd950b…`, `cd6429ce…`) were never cited or used for an authorization.

## 4. Verification in this pass

| Check | Result |
|---|---|
| `g01r verify-freeze` on the rebuilt manifest | `VERIFIED` |
| Unit tests | 101 tests, all pass |
| Outcome firewall | Only `outcomes.py` names outcome sources (static test); every other read of the eligibility table is column-whitelisted; no `AUTHORIZATION.json` exists; `g01r run` refuses (tested) |
| Derived caches | 71/71 CorrCA units and 740/740 synchrony plans bit-identical: all 500 PAS-core regime-A splits, 100 random cached nested-CV plans (M2 vs M5) and 20 cached outer splits for each of 7 other regime-A set/route combinations ([cache_consistency.json](evidence/validation/cache_consistency.json)) |
| Committability | 51 repository files are bound: 7 are already committed unchanged (the protocol documents and the reused audit modules); the other 44 are new or modified and none is git-ignored, so the commit will contain them. `authorize` checks this. Nothing under `data/` or `results/` is committed (git-ignored, hash-bound instead) |
| Evidence content | Population files hold keys and set flags only; no outcome or participant-level physiological values in any committed file |

## 5. Decisions that are yours

1. **Confirm the H3 reading (IS-028) before the commit.** *Resolved 2026-10-05: confirmed by the user and recorded as final (BID-026).* The estimand asks that H3 keep H1's "decision category"; the protocol forbids new tests in H3, and the registry follows the protocol. IS-028 reads robustness as agreement in sign and in side of δ, and states that H3 never changes the H1 conclusion. The alternative, re-running permutation tests and futility bounds for each H3 analysis, would add tests the protocol excludes. Changing this after the deposit would be a deviation.
2. **Deposit details.** Authors and affiliations; the registry (OSF "Preregistration in secondary data analysis" fits); whether to embargo.
3. **Attach the frozen repository snapshot?** Recommended: `git archive` of the freeze commit (code, documents, manifest, evidence; no raw data and no outcomes) uploaded with the deposit, so reviewers can check the hashes.

Not needed, and therefore not asked: a cold confirmatory run. The cache is verified bit-identical; a cold run would cost about 1.5–2 h more and require rebuilding the freeze before the commit. The optional OQ-06 author query and the John 2025 download remain separate authorizations.

## 6. Exact next steps

> **Done 2026-10-05:** step 1 (commit `6ba87fe`, tag `g01r-freeze-v1`) and the snapshot. See [FREEZE_RECORD.md](../../../analysis_freeze/FREEZE_RECORD.md). Steps 2–4 remain user actions.

Run every command from the repository root. Each step is a user action.

**1. Commit the freeze.**

```sh
cd /Users/jerlshin/FieldOfInterest/ResearchWork/NTU_research
git add .gitignore pyproject.toml requirements-baseline.lock configs analysis_freeze src/g01r tests docs/research
git status --short            # expect no entries under data/ or results/
git commit -m "G01-R analysis freeze and preregistration package"
git tag -a g01r-freeze-v1 -m "G01-R analysis freeze (manifest a2594996ac12)"
git rev-parse HEAD            # the freeze commit: copy it into the preregistration
PYTHONPATH=src .venv/bin/python -m g01r verify-freeze
```

`verify-freeze` must print `VERIFIED` and no note about uncommitted bound files.

**2. Deposit the preregistration.** Use [preregistration.md](preregistration.md). Fill only its deposit-time fields: authors, the freeze commit from step 1, the date. Optionally attach `git archive --format=zip -o g01r-freeze-v1.zip g01r-freeze-v1`. Note the DOI or URL.

**3. Write the authorization record.**

```sh
PYTHONPATH=src .venv/bin/python -m g01r authorize --preregistration <DOI-or-URL> --by "<your name>"
git add analysis_freeze/AUTHORIZATION.json
git commit -m "Record G01-R outcome-access authorization"
```

`authorize` refuses unless the freeze verifies and is committed. It records the manifest SHA-256 and the commit.

**4. Run the first confirmatory analysis (H1/H2).**

```sh
PYTHONPATH=src .venv/bin/python -m g01r verify-freeze
PYTHONPATH=src .venv/bin/python -m g01r run --analysis H1_H2 --workers 5
```

- **Wall time:** about 3–4 h with 5 workers. Do not edit any bound file or run `g01r freeze` while it runs.
- **Output:** `results/runs/g01r-confirmatory/H1_H2__…/result.json` (mirrored to MLflow), containing the H1 p-value, Ŝ, U₃, the nested-CV interval, the H1 decision category, Holm-adjusted H2a–d, the cell-weighted and state intervals and the shortcut diagnostics (i, iii).
- **Afterwards:** commit `analysis_freeze/outcome_access_log.jsonl`, then continue with steps 2–5 of the [run book](analysis_freeze.md#run-book-after-authorization). Report every analysis, whatever the H1 result.
