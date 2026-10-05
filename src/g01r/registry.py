"""The prespecified analysis plan as code (protocol §1, §11-§15).

Each entry fixes the analysis set, regime, outcome, feature route, model families, tests and
interval procedures. Nothing outside this registry is run by the confirmatory runner, and the
registry's hash is part of the analysis-freeze manifest.
"""
from __future__ import annotations

from dataclasses import dataclass, field

CORE_RF = ("RF_EEG", "RF_ECG", "RF_GAZE")
CORE_SYN = ("SYN_EEG", "SYN_ECG", "SYN_GAZE")
A_MODELS = ("M0", "M1", "M2", "M3", "M4", "M5", "M_EEG", "M_ECG", "M_GAZE", "M0_Q", "M2_NOISE")


@dataclass(frozen=True)
class PermTest:
    id: str
    base: str
    full: str
    tested_blocks: tuple
    nuisance_blocks: tuple       # in addition to experiment x video content dummies


@dataclass(frozen=True)
class Comparison:
    id: str
    base: str
    full: str
    interval: bool = True        # nested-CV 90 % interval
    futility: bool = False       # corrected-t (z = 3.0) upper bound versus 2 delta
    extra_losses: tuple = ()     # additional nested-CV losses from the same fits: "state", "cell"


@dataclass(frozen=True)
class AnalysisSpec:
    id: str
    role: str
    description: str
    regime: str                  # A | BC | transport | CAS | explanatory | identity_probe | derived
    set_name: str
    outcome: str = "exact"
    route: str = "processed"
    include_gpa: bool = False
    models: tuple = ()
    comparisons: tuple = ()
    tests: tuple = ()
    options: dict = field(default_factory=dict)


H1 = PermTest("H1", "M2", "M5", CORE_RF + CORE_SYN, ("C", "Q"))
H2 = (
    PermTest("H2a", "M3", "M5", CORE_SYN, ("C", "Q") + CORE_RF),
    PermTest("H2b", "M2", "M_EEG", ("RF_EEG", "SYN_EEG"), ("C", "Q")),
    PermTest("H2c", "M2", "M_ECG", ("RF_ECG", "SYN_ECG"), ("C", "Q")),
    PermTest("H2d", "M2", "M_GAZE", ("RF_GAZE", "SYN_GAZE"), ("C", "Q")),
)
PRIMARY = Comparison("M5_vs_M2", "M2", "M5", interval=True, futility=True, extra_losses=("state", "cell"))
H3_PRIMARY = Comparison("M5_vs_M2", "M2", "M5", interval=True)

REGISTRY = [
    AnalysisSpec("H1_H2", "confirmatory", "Regime A on PAS-core: H1 (M5 vs M2) and the Holm family H2a-d; all prespecified "
                 "regime-A models on identical folds; state and cell-weighted intervals; shortcut diagnostics (i, iii)",
                 "A", "PAS_E34_core", models=A_MODELS,
                 comparisons=(PRIMARY, Comparison("M3_vs_M2", "M2", "M3", False), Comparison("M4_vs_M2", "M2", "M4", False),
                              Comparison("M5_vs_M3", "M3", "M5", False), Comparison("M_EEG_vs_M2", "M2", "M_EEG", False),
                              Comparison("M_ECG_vs_M2", "M2", "M_ECG", False), Comparison("M_GAZE_vs_M2", "M2", "M_GAZE", False),
                              Comparison("M1_vs_M0", "M0", "M1", False), Comparison("M2_vs_M1", "M1", "M2", False),
                              Comparison("SHORTCUT_i_M0Q_vs_M0", "M0", "M0_Q", False),
                              Comparison("SHORTCUT_iii_NOISE_vs_M2", "M2", "M2_NOISE", False)),
                 tests=(H1,) + H2),
    AnalysisSpec("H3_1_partial", "robustness", "Partial-credit outcome", "A", "PAS_E34_core", outcome="partial",
                 models=("M2", "M5"), comparisons=(H3_PRIMARY,)),
    AnalysisSpec("H3_2_eye30", "robustness", "Eye-correction QC threshold 0.30", "A", "PAS_E34_core_eye30",
                 models=("M2", "M5"), comparisons=(H3_PRIMARY,)),
    AnalysisSpec("H3_2_eye70", "robustness", "Eye-correction QC threshold 0.70", "A", "PAS_E34_core_eye70",
                 models=("M2", "M5"), comparisons=(H3_PRIMARY,)),
    AnalysisSpec("H3_3_four", "robustness/secondary", "PAS-four without (M5) and with (M5+pupil) the pupil block", "A",
                 "PAS_E34_four", models=("M2", "M5", "M5_PUPIL"),
                 comparisons=(H3_PRIMARY, Comparison("M5_PUPIL_vs_M2", "M2", "M5_PUPIL", True))),
    AnalysisSpec("H3_4_raw", "robustness", "Raw-export feature route", "A", "PAS_E34_core", route="raw",
                 models=("M2", "M5"), comparisons=(H3_PRIMARY,)),
    AnalysisSpec("H3_5_alpha", "robustness", "Exclude content with exact alpha < 0.30 (bYgV9nvgJ3E)", "A",
                 "PAS_E34_core_alpha30", models=("M2", "M5"), comparisons=(H3_PRIMARY,)),
    AnalysisSpec("H3_6_gpa", "robustness", "GPA (valid GPA + missing indicator) added to C", "A", "PAS_E34_core",
                 include_gpa=True, models=("M2", "M5"), comparisons=(H3_PRIMARY,)),
    AnalysisSpec("H3_7_cell", "robustness", "Cell-weighted skill (point estimate and nested-CV interval from H1_H2)",
                 "derived", "PAS_E34_core", options=dict(source="H1_H2", loss="cell")),
    AnalysisSpec("D_state", "descriptive/exploratory", "State skill: nested-CV interval of the double-centred loss "
                 "difference (from H1_H2)", "derived", "PAS_E34_core", options=dict(source="H1_H2", loss="state")),
    AnalysisSpec("D_BC", "descriptive", "Regimes B and C on identical cells; per video, pooled two-way bootstrap "
                 "(conditional on the 8 videos), B-C paired per video", "BC", "PAS_E34_core",
                 models=("M2", "M5_B", "M5")),
    AnalysisSpec("D_CAS", "descriptive", "Coverage-set policy: M5 where PAS-core features exist, M2 otherwise; risk "
                 "versus M2 on all 302 cells", "CAS", "CAS_E34", models=("M2", "M5"),
                 options=dict(core_set="PAS_E34_core")),
    AnalysisSpec("D_E5", "descriptive", "E5 repeat-exposure regime A", "A", "E5_core", models=("M2", "M5"),
                 comparisons=(H3_PRIMARY,)),
    AnalysisSpec("D_transport", "descriptive", "E4 <-> E5 transport on the 3 shared videos (source references and "
                 "offsets); target-mean-recalibrated variant labelled as using target labels", "transport",
                 "E4_core", models=("M2", "M5"), options=dict(pair=("E4_core", "E5_core"))),
    AnalysisSpec("D_E1", "descriptive", "E1 ocular-only regime A (gaze RF + SYN; age and sex as C)", "A", "E1_gaze",
                 models=("M2", "M5_E1"), comparisons=(Comparison("M5_E1_vs_M2", "M2", "M5_E1", True),)),
    AnalysisSpec("X_explanatory", "explanatory", "Crossed REML mixed model (person and content random intercepts, "
                 "M5 inputs as fixed effects) fit once on PAS-core; never presented as predictive evidence",
                 "explanatory", "PAS_E34_core"),
    AnalysisSpec("S_identity_probe", "diagnostic", "Shortcut diagnostic (ii): held-out accuracy of predicting the "
                 "experiment x video unit from the physiological features", "identity_probe", "PAS_E34_core"),
]


def get(analysis_id: str) -> AnalysisSpec:
    for spec in REGISTRY:
        if spec.id == analysis_id:
            return spec
    raise KeyError(analysis_id)
