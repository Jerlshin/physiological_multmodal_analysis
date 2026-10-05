"""Outcome-blind feature-level QC and missingness report (protocol §17.4; readiness-verdict trigger).

Reports, per analysis set and route, aggregate distributions and missingness of every frozen
feature (RF, Q, C) and of the synchrony features exactly as the analysis computes them (test
cells of the first frozen regime-A repetition), plus physiology-only correlations and raw-versus-
processed route agreement. Evaluates the live REVISE trigger: PAS-core losing more than 15 % of
learners to feature-level QC. Only aggregates are written; no outcome is read.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from . import references as refs_mod
from .config import IMPL_EVIDENCE, ProtocolConfig
from .design import FeatureProvider
from .features import RF_BLOCKS, SYN_BLOCKS
from .population import Population
from .splits import outer_folds

CORE_RF = [c for b in ("RF_EEG", "RF_ECG", "RF_GAZE") for c in RF_BLOCKS[b]]
CORE_SYN = [c for b in ("SYN_EEG", "SYN_ECG", "SYN_GAZE") for c in SYN_BLOCKS[b]]
SETS = [("PAS_E34_core", "processed"), ("PAS_E34_core", "raw"), ("PAS_E34_four", "processed"),
        ("PAS_E34_core_eye30", "processed"), ("PAS_E34_core_eye70", "processed"), ("PAS_E34_core_alpha30", "processed"),
        ("E5_core", "processed"), ("E1_gaze", "processed")]


def _describe(values: pd.Series) -> dict:
    v = values.to_numpy(float)
    ok = np.isfinite(v)
    out = dict(n=int(ok.sum()), missing_fraction=float(1 - ok.mean()) if len(v) else None)
    if ok.sum():
        q = np.quantile(v[ok], [0.05, 0.25, 0.5, 0.75, 0.95])
        out.update(mean=float(v[ok].mean()), sd=float(v[ok].std(ddof=1)) if ok.sum() > 1 else None,
                   q05=float(q[0]), q25=float(q[1]), median=float(q[2]), q75=float(q[3]), q95=float(q[4]),
                   min=float(v[ok].min()), max=float(v[ok].max()))
    return out


def syn_first_repetition(cfg: ProtocolConfig, prov: FeatureProvider) -> pd.DataFrame:
    """SYN features of every cell as a test cell of repetition 0 of the frozen regime-A folds."""
    aset = prov.aset
    folds = outer_folds(aset, cfg.resampling["outer_folds_A"], cfg.resampling["reps_A"], cfg.resampling["base_seed"],
                        aset.name, "A")
    cols = CORE_SYN + ["SYNP_pupil_isc"]
    out = pd.DataFrame(np.nan, index=np.arange(aset.n), columns=cols)
    for k in range(cfg.resampling["outer_folds_A"]):
        test = folds[0][aset.person] == k
        syn = prov.syn(refs_mod.regime_A(aset, ~test, np.ones(aset.n, bool)))
        out.loc[test, cols] = syn.loc[test, cols].to_numpy()
    return out


def set_report(cfg: ProtocolConfig, pop: Population, set_name: str, route: str) -> tuple[dict, pd.DataFrame]:
    aset = pop.analysis_set(set_name)
    prov = FeatureProvider(cfg, aset, route)
    s = prov.static
    ocular = prov.ocular_only
    rf_cols = [c for b in (("RF_GAZE",) if ocular else ("RF_EEG", "RF_ECG", "RF_GAZE")) for c in RF_BLOCKS[b]]
    syn_cols = ["SYN3_gaze_isc"] if ocular else CORE_SYN
    syn = syn_first_repetition(cfg, prov)
    feats = pd.concat([s[rf_cols + ["RFP_pupil_variability"]], syn], axis=1)
    rep = dict(set=set_name, route=route, people=aset.n_person, cells=aset.n, videos=aset.n_video, features={}, quality={},
               covariates={})
    for c in feats.columns:
        rep["features"][c] = _describe(feats[c])
    for c in prov.block_columns("Q"):
        rep["quality"][c] = _describe(s[c])
    for c in prov.block_columns("C"):
        rep["covariates"][c] = _describe(s[c])
    core = rf_cols + syn_cols
    any_missing = feats[core].isna().any(axis=1).to_numpy()
    lost = pd.Series(any_missing).groupby(aset.person).all()
    rep["missingness"] = dict(
        cells_with_any_missing_core_feature=int(any_missing.sum()),
        cells_with_any_missing_core_feature_fraction=float(any_missing.mean()),
        learners_with_every_cell_missing_some_core_feature=int(lost.sum()),
        learners_lost_fraction_if_complete_case=float(lost.mean()),
        per_block_cells_missing={b: int(feats[[c for c in cols if c in feats]].isna().any(axis=1).sum())
                                 for b, cols in {**RF_BLOCKS, **SYN_BLOCKS}.items() if any(c in feats for c in cols)},
        handling="protocol §6: missing features are imputed with the training mean plus a block indicator; no cell is dropped",
    )
    phys = pd.concat([feats[core], s[prov.block_columns("Q")]], axis=1)
    rep["spearman_physiology_and_quality"] = phys.corr(method="spearman").round(3).where(lambda d: d.notna(), None).to_dict()
    return rep, feats.assign(person=aset.person, ev=aset.ev)


def run(cfg: ProtocolConfig, sets=SETS) -> dict:
    pop = Population(cfg)
    out_dir = IMPL_EVIDENCE / "feature_qc"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = dict(outcome_values_read=False, sets={}, label="OUTCOME-BLIND feature QC (aggregates only)")
    frames = {}
    for set_name, route in sets:
        rep, feats = set_report(cfg, pop, set_name, route)
        report["sets"][f"{set_name}|{route}"] = rep
        frames[(set_name, route)] = feats
        print(f"feature QC {set_name}|{route}: lost={rep['missingness']['learners_lost_fraction_if_complete_case']:.3f}", flush=True)
    a, b = frames[("PAS_E34_core", "processed")], frames[("PAS_E34_core", "raw")]
    report["route_agreement_PAS_core_spearman"] = {c: float(a[c].corr(b[c], method="spearman"))
                                                   for c in CORE_RF + ["SYN1_eeg_isc", "SYN3_gaze_isc"]}
    lost = report["sets"]["PAS_E34_core|processed"]["missingness"]["learners_lost_fraction_if_complete_case"]
    report["revise_trigger"] = dict(rule="PAS-core loses > 15 % of learners to feature-level QC", value=lost,
                                    fired=bool(lost > 0.15))
    path = out_dir / "feature_qc.json"
    path.write_text(json.dumps(report, indent=2, default=lambda o: None) + "\n")
    rows = []
    for key, rep in report["sets"].items():
        for group in ("features", "quality"):
            for c, d in rep[group].items():
                rows.append(dict(set_route=key, group=group, feature=c, **{k: d.get(k) for k in
                                                                            ("n", "missing_fraction", "mean", "sd", "q05", "median", "q95")}))
    pd.DataFrame(rows).to_csv(out_dir / "feature_summary.csv", index=False)
    return report
