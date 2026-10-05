"""The only module that may touch quiz outcomes.

* :func:`load_real_outcomes` refuses unless an analysis-freeze authorization record exists
  and the freeze manifest verifies against the current code, configuration, population and
  feature tables, re-checked at every access (protocol §16; readiness verdict condition 1). Creating that record is a
  user action taken after the preregistration deposit.
* :func:`synthetic_outcomes` draws outcomes from the design-phase outcome-only psychometric
  parameters on the real incidence. It never reads item- or cell-level outcomes.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .config import AUDIT_EVIDENCE, DESIGN_EVIDENCE
from .population import AnalysisSet

OUTCOME_COLUMNS = {"exact": "normalized_exact_score", "partial": "normalized_partial_score"}


class OutcomeAccessDenied(PermissionError):
    pass


def load_real_outcomes(aset: AnalysisSet, kind: str, authorization) -> np.ndarray:
    """Real video-level quiz scores for the cells of ``aset`` (requires a verified authorization)."""
    from .config import load_config
    from .freeze import Authorization, load_authorization

    if not isinstance(authorization, Authorization) or not authorization.verified:
        raise OutcomeAccessDenied("Real outcomes are locked until the analysis-freeze authorization verifies "
                                  "(see analysis_freeze/README.md)")
    # Never trust the caller's object alone: re-read the record and re-verify the freeze at every access.
    if load_authorization(load_config()).record_sha256 != authorization.record_sha256:
        raise OutcomeAccessDenied("Authorization record changed since the run started")
    column = OUTCOME_COLUMNS[kind]
    keys = ["experiment", "participant_id", "canonical_video_id"]
    table = pd.read_parquet(AUDIT_EVIDENCE / "gate_closure_behavioral_eligibility.parquet",
                            columns=keys + ["question_type", "gate_behavior_eligible", column])
    table = table[(table.question_type == "memory") & table.gate_behavior_eligible]
    joined = aset.cells[keys].merge(table[keys + [column]], on=keys, how="left", validate="one_to_one")
    y = joined[column].to_numpy(float)
    if not np.isfinite(y).all():
        raise ValueError("Analysis-set cell without an eligible outcome")
    authorization.log_access(aset.name, kind, len(y))
    return y


def outcome_params() -> dict:
    """Per-experiment outcome-only parameters (the design simulation's generator, precision_simulation.py)."""
    s = json.loads((DESIGN_EVIDENCE / "outcome_psychometrics.json").read_text())
    rel = pd.read_csv(DESIGN_EVIDENCE / "outcome_reliability_by_video.csv")
    out = {}
    for exp, lab in [(1, "E1_ocular"), (3, "E3"), (4, "E4"), (5, "E5_repeat")]:
        rv = rel[rel.set == lab]
        within = float((rv.sd_exact ** 2).mean())
        err = float(((1 - rv.alpha_exact) * rv.sd_exact ** 2).mean())
        vc = s["sets"][lab]["variance_components_normalized_exact_score"]
        out[exp] = dict(mean=s["sets"][lab]["normalized_exact_score"]["mean"], video=vc["video"],
                        person=vc["person"], pv=max(within - err - vc["person"], 1e-4), meas=err)
    return out


def synthetic_outcomes(aset: AnalysisSet, rng: np.random.Generator, nuisance: np.ndarray | None = None,
                       nuisance_share: float = 0.0, signal: np.ndarray | None = None, signal_amp: float = 0.0,
                       items: int = 12) -> np.ndarray:
    """Synthetic exact scores on the analysis set's incidence.

    ``nuisance`` (cells x q) enters linearly with a total share ``nuisance_share`` of the person
    variance (a nonsignal null: outcomes depend on C/Q columns that the baseline contains);
    ``signal`` (cells,) enters with amplitude ``signal_amp`` (planted physiological information).
    """
    par = outcome_params()
    exp, ev, person = aset.experiment, aset.ev, aset.person
    ev_exp = aset.ev_experiment
    content = np.array([rng.normal(0, np.sqrt(par[e]["video"])) for e in ev_exp])
    pe = aset.exp_of_person
    z_person = rng.normal(size=aset.n_person)
    sd_p = np.sqrt([par[e]["person"] for e in pe])
    ystar = (np.array([par[e]["mean"] for e in exp]) + content[ev]
             + np.sqrt(1 - nuisance_share) * sd_p[person] * z_person[person]
             + np.sqrt([par[e]["pv"] for e in exp]) * rng.normal(size=aset.n))
    if nuisance is not None and nuisance_share > 0:
        Z = (nuisance - nuisance.mean(0)) / np.where(nuisance.std(0) > 0, nuisance.std(0), 1)
        comb = Z @ rng.normal(size=Z.shape[1])
        comb = (comb - comb.mean()) / comb.std()
        ystar = ystar + np.sqrt(nuisance_share) * sd_p[person] * comb
    if signal is not None and signal_amp:
        s = (signal - signal.mean()) / signal.std()
        ystar = ystar + signal_amp * s
    y = ystar + np.sqrt([par[e]["meas"] for e in exp]) * rng.normal(size=aset.n)
    return np.clip(np.round(y * items) / items, 0, 1)
