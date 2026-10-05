# Baseline Implementation & Analysis Freeze — G01-R

Phase run 2026-10-04/05. Input: the [experimental-design package](../experimental_design/README.md), verdict GO for G01-R, with [protocol.md](../experimental_design/protocol.md) v1.0 (commit `ef1df1b`) as the analysis contract.

Output: a production-quality, reproducible pipeline that executes the frozen protocol, validated before any outcome access, together with an analysis-freeze gate that keeps real quiz outcomes locked until the preregistration is deposited.

**No real quiz outcome was read, inspected or modelled in this phase.**

- Every model fit used synthetic outcomes, drawn from the design phase's outcome-only psychometric parameters.
- Every physiological feature was generated outcome-blind.
- No preregistration was submitted, no author contacted, no external dataset downloaded and no bespoke architecture developed.

**Next phase:** [first confirmatory run (H1/H2)](../confirmatory_h1h2/README.md), 2026-10-05.

**Verdict:** see [freeze_finalization.md](freeze_finalization.md) (current for this phase), which finalizes the freeze and preregistration package after the [readiness verdict](readiness_verdict.md).

## Reading order

| Document | Content |
|---|---|
| [pipeline_architecture.md](pipeline_architecture.md) | Modules, data flow, outcome firewall, leakage rule → code → test map, compute profile |
| [implementation_spec.md](implementation_spec.md) | IS-001…IS-029: every operational clarification of the protocol, fixed before outcome access |
| [feature_qc.md](feature_qc.md) | Outcome-blind feature QC and missingness; REVISE trigger evaluation; pre-outcome observations |
| [validation_report.md](validation_report.md) | Production re-validation of the operating characteristics (V1) and real-feature null calibration (V2) |
| [analysis_freeze.md](analysis_freeze.md) | What is frozen, the hash manifest, the authorization gate, the run book |
| [preregistration.md](preregistration.md) | Final preregistration text as frozen. Deposited by the user at OSF (https://osf.io/uh397/overview) before the 2026-10-05 authorization; the repository copy is left unchanged, with deposit-time fields recorded in [FREEZE_RECORD.md](../../../analysis_freeze/FREEZE_RECORD.md) |
| [readiness_verdict.md](readiness_verdict.md) | Phase verdict and what remained |
| [freeze_finalization.md](freeze_finalization.md) | Consistency review, finalization changes, current verdict and the exact next steps |

**Evidence** ([folder](evidence/)), all regenerable with `python -m g01r …`:

| Folder | Produced by | Content |
|---|---|---|
| `population/` | `g01r population` | Analysis sets (keys and flags only), case flow, summary verified against the frozen manifest |
| `feature_qc/` | `g01r feature-qc` | Aggregate feature distributions, missingness, correlations, route agreement, trigger |
| `validation/` | `g01r validate-v1`, `validate-v2`, `validation-verdict`; `cache_consistency.py` | Replicate-level CSVs, summaries, verdict; bit-identity of the reused synchrony caches |

Code: [`src/g01r`](../../../src/g01r). Config: [`configs/g01r_protocol_v1.toml`](../../../configs/g01r_protocol_v1.toml). Freeze: [`analysis_freeze/`](../../../analysis_freeze/README.md). Tests: `tests/test_g01r_*.py`.

The decision trail is appended, never overwritten:

- [decision log](../research_gap/decision_log.md), BID-001 onward;
- [inference register](../research_gap/inference_register.md), BII-001 onward;
- global pointers in [decision_log.md](../decision_log.md) and [inference_register.md](../inference_register.md).

## Commands

```sh
export PYTHONPATH=src
.venv/bin/python -m g01r population          # verify sets against the frozen manifest; case flow
.venv/bin/python -m g01r extract             # outcome-blind features (processed + raw routes)
.venv/bin/python -m g01r warm-syn            # optional: precompute synchrony for the frozen PAS-core splits
.venv/bin/python -m g01r feature-qc          # feature QC report and the 15 % trigger
.venv/bin/python -m g01r validate-v1         # production re-simulation (≈2 h, 9 workers)
.venv/bin/python -m g01r validate-v2         # real-feature null calibration
.venv/bin/python -m g01r validation-verdict  # targets of protocol §17.3; detection procedure
.venv/bin/python -m g01r freeze              # write analysis_freeze/freeze_manifest.json
.venv/bin/python -m g01r verify-freeze
.venv/bin/python -m g01r dry-run --analysis all --experiment g01r-dryrun   # synthetic outcomes only
.venv/bin/python -m unittest discover -s tests
# USER ACTIONS ONLY, after commit + preregistration deposit:
.venv/bin/python -m g01r authorize --preregistration <DOI> --by <name>
.venv/bin/python -m g01r run --analysis H1_H2 --workers 5
```

**Tracking.** Every command writes `results/runs/<experiment>/<run>/` (`run.json`, `params.json`, `metrics.json`, `artifacts/`). It mirrors the run to MLflow (`results/mlflow/mlflow.db`, SQLite backend), which can be browsed with:

```sh
mlflow ui --backend-store-uri sqlite:///results/mlflow/mlflow.db
```

Both folders are git-ignored, as are the derived feature tables and caches under `data/derived/`. Their hashes are bound by the freeze manifest.
