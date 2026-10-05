"""Admissible person covariates C (protocol §6; M02 §3)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import AUDIT_EVIDENCE

TRAIT_COLUMNS = ["qualified_participant_id", "experiment", "Age", "Sex", "asrs_recomputed_inattention_0_4",
                 "asrs_recomputed_hyperactivity_0_4", "digit_span", "GPA_numeric"]


def covariate_table() -> pd.DataFrame:
    """One row per experiment-qualified person; missing values left as NaN with explicit indicators."""
    t = pd.read_parquet(AUDIT_EVIDENCE / "participant_traits.parquet", columns=TRAIT_COLUMNS)
    out = pd.DataFrame({"qualified_participant_id": t.qualified_participant_id})
    out["C_age"] = pd.to_numeric(t.Age, errors="coerce").astype(float)
    sex = t.Sex.astype("string")
    out["C_sex_male"] = np.where(sex == "Male", 1.0, np.where(sex == "Female", 0.0, np.nan))
    out["C_sex_unknown"] = np.isnan(out.C_sex_male).astype(float)
    out["C_asrs_inattention"] = pd.to_numeric(t.asrs_recomputed_inattention_0_4, errors="coerce").astype(float)
    out["C_asrs_hyperactivity"] = pd.to_numeric(t.asrs_recomputed_hyperactivity_0_4, errors="coerce").astype(float)
    ds = pd.to_numeric(t.digit_span, errors="coerce").astype(float)
    out["C_digit_span"] = ds.where(ds.between(3, 7))
    out["C_digit_span_missing"] = out.C_digit_span.isna().astype(float)
    gpa = pd.to_numeric(t.GPA_numeric, errors="coerce").astype(float)
    out["C_gpa"] = gpa.where(gpa.between(0.01, 4.0))
    out["C_gpa_missing"] = out.C_gpa.isna().astype(float)
    return out.reset_index(drop=True)
