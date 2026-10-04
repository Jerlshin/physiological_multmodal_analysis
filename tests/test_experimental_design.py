"""Checks for the experimental-design phase: frozen ledger, outcome-only inputs,
estimator mechanics and documentation integrity. No physiology-outcome model is fit."""
import importlib.util
import json
import re
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "docs/research/experimental_design"
EV = DESIGN / "evidence"


def load_sim():
    spec = importlib.util.spec_from_file_location("precision_simulation", EV / "precision_simulation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FrozenLedger(unittest.TestCase):
    def test_analysis_set_counts(self):
        summary = json.loads((EV / "design_ledger.json").read_text())
        self.assertEqual(summary["PAS_E34_core"], {"people": 68, "cells": 259, "videos": 8})
        self.assertEqual(summary["PAS_E34_four"], {"people": 57, "cells": 216, "videos": 8})
        self.assertEqual(summary["CAS_E34"], {"people": 72, "cells": 302, "videos": 8})
        self.assertEqual(summary["E5_core"], {"people": 46, "cells": 128, "videos": 3})

    def test_manifest_has_no_outcome_values(self):
        manifest = pd.read_csv(EV / "analysis_set_manifest.csv")
        self.assertFalse(any("score" in c or "correct" in c for c in manifest.columns))
        self.assertFalse((manifest.experiment == 2).any())

    def test_primary_set_is_subset_of_coverage_set(self):
        m = pd.read_csv(EV / "analysis_set_manifest.csv")
        self.assertTrue((~m.PAS_E34_core | m.CAS_E34).all())
        self.assertTrue((~m.PAS_E34_four | m.PAS_E34_core).all())


class OutcomeOnlyInputs(unittest.TestCase):
    def test_delta_rule_and_outcome_rule(self):
        s = json.loads((EV / "outcome_psychometrics.json").read_text())
        self.assertFalse(s["physiology_used"])
        oie = s["sets"]["E3+E4_first_view"]["one_item_equivalent_skill"]["mean"]
        self.assertEqual(s["delta"], round(max(0.05, oie), 2))
        self.assertFalse(any(s["outcome_rule_check"].values()))

    def test_kr20_known_values(self):
        spec = importlib.util.spec_from_file_location("op", EV / "outcome_psychometrics.py")
        op = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(op)
        identical = np.repeat(np.array([[0], [1], [1], [0], [1]]), 4, axis=1).astype(float)
        self.assertAlmostEqual(op.kr20(identical), 1.0)
        rng = np.random.default_rng(3)
        noise = rng.integers(0, 2, (4000, 12)).astype(float)
        self.assertLess(abs(op.kr20(noise)), 0.05)


class EstimatorMechanics(unittest.TestCase):
    def setUp(self):
        self.sim = load_sim()

    def test_ridge_path_recovers_ols_at_small_penalty(self):
        rng = np.random.default_rng(5)
        X = rng.normal(size=(200, 4))
        y = X @ np.array([1.0, -2.0, 0.5, 0.0]) + rng.normal(scale=0.1, size=200)
        pred = self.sim.ridge_path(X, y, X, np.array([1e-8]))[:, 0]
        A = np.column_stack([np.ones(200), (X - X.mean(0)) / X.std(0)])
        ols = A @ np.linalg.lstsq(A, y, rcond=None)[0]
        self.assertTrue(np.allclose(pred, ols, atol=1e-6))

    def test_person_folds_are_grouped_and_stratified(self):
        rng = np.random.default_rng(7)
        person = np.repeat(np.arange(30), 3)
        exp_of_person = np.r_[np.full(12, 3), np.full(18, 4)]
        f = self.sim.person_folds(person, exp_of_person, 10, rng)
        for p in range(30):
            self.assertEqual(len(set(f[person == p])), 1)
        per_fold_e3 = np.bincount(f[::3][:12], minlength=10)
        self.assertLessEqual(per_fold_e3.max() - per_fold_e3.min(), 1)

    def test_within_content_metric_is_shift_invariant(self):
        rng = np.random.default_rng(9)
        y, pred = rng.random(60), rng.random(60)
        ev = np.repeat(np.arange(3), 20)
        shifted = pred + np.array([0.3, -0.2, 0.1])[ev]
        self.assertTrue(np.allclose(self.sim.within_content(y, pred, ev), self.sim.within_content(y, shifted, ev)))


class DocumentationIntegrity(unittest.TestCase):
    def test_local_links_resolve(self):
        missing = []
        for md in DESIGN.glob("*.md"):
            for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", md.read_text()):
                if target.startswith("http"):
                    continue
                if not (md.parent / target).exists():
                    missing.append(f"{md.name} -> {target}")
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
