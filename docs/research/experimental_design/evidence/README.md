# Evidence for the experimental-design phase (2026-10-04)

Everything here was produced **without computing any physiology–outcome association**. Inputs are:

- audited bookkeeping tables;
- outcome-only item data;
- physiology-only variance summaries;
- simulated data.

Run every script from the repository root with the project virtual environment (numpy, scipy, pandas only).

| Script | Reads | Writes | Approx. runtime |
|---|---|---|---|
| `outcome_psychometrics.py` | Audited quiz items and gate eligibility | `outcome_psychometrics.json`, `outcome_reliability_by_video.csv`, `one_item_equivalent_items.csv` | 5 s |
| `design_ledger.py` | Exposure tensor, eligibility, traits, exposure summaries (QC fractions only) | `case_flow.csv`, `design_ledger.json`, `analysis_set_manifest.csv` (keys and flags only), `core_exclusion_reasons.csv`, `analysis_set_incidence.csv`, `covariate_availability.csv`, `selection_diagnostic.csv` | 5 s |
| `precision_simulation.py` | Manifest, psychometrics | `precision_simulation_summary.csv`, `precision_simulation_meta.json`, `simulation_replicates/{A,B}_*.csv` | About 60 min on 10 cores (`--quick` for a smoke test) |
| `inference_calibration.py [--person]` | As above (imports `precision_simulation`) | `inference_calibration_summary_{cell,person}perm.csv`, metadata, `simulation_replicates/calibration_*` | About 15 / 10 min |

```sh
.venv/bin/python docs/research/experimental_design/evidence/outcome_psychometrics.py
.venv/bin/python docs/research/experimental_design/evidence/design_ledger.py
.venv/bin/python docs/research/experimental_design/evidence/precision_simulation.py
.venv/bin/python docs/research/experimental_design/evidence/inference_calibration.py
.venv/bin/python docs/research/experimental_design/evidence/inference_calibration.py --person
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
```

**Reproducibility.**

- Simulations are seeded deterministically per scenario and replicate.
- Inner penalty-selection folds draw from the replicate's generator, so results reproduce exactly on the same library versions (see `requirements-audit.lock`).
- The cell-wise permutation run was produced by the script version before the `--person` option was added. Its outputs were renamed to the `cellperm` scheme without other change.

**`external/` folder.**

- File manifests (John 2025, Bühler 2024).
- The P05 bibliographic record.
- Delegated audit notes.

It contains no external participant-level data.
