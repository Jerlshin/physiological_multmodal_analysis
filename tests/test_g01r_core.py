"""G01-R production pipeline: configuration, population, splits, models, metrics, inference.

Protocol §17 items 1-3 (unit tests on synthetic data; no real outcome is read).
"""
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from g01r import inference as inf
from g01r import metrics as met
from g01r.config import CONFIG_PATH, load_config
from g01r.design import FixedFeatureProvider
from g01r.models import FAMILY, ModelSpec, choose_lambda, fit_predict, impute_train_mean, ridge_path
from g01r.pipeline import Pipeline, content_offsets, run_regime_A
from g01r.population import AnalysisSet
from g01r.rng import rng_for
from g01r.splits import bc_splits, inner_folds, outer_folds, person_folds


def toy_set(n_e3=12, n_e4=15, seed=0):
    """Synthetic crossed incidence resembling PAS-core: E3 people see subsets of 4 videos, E4 people 3."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_e3):
        for v in rng.choice(["a", "b", "c", "rel"], size=rng.integers(2, 5), replace=False):
            rows.append(dict(experiment=3, participant_id=f"s{i}", qualified_participant_id=f"exp-3:s{i}", session=1,
                             local_stimulus_id=0, canonical_video_id=v, condition="x", exposure_number=1))
    for i in range(n_e4):
        for v in ["d", "e", "rel"]:
            rows.append(dict(experiment=4, participant_id=f"s{i}", qualified_participant_id=f"exp-4:s{i}", session=2,
                             local_stimulus_id=0, canonical_video_id=v, condition="x", exposure_number=1))
    return AnalysisSet("toy", pd.DataFrame(rows))


class FrozenConfiguration(unittest.TestCase):
    def test_protocol_constants(self):
        cfg = load_config()
        inf_ = cfg.inference
        self.assertEqual(inf_["delta"], 0.05)
        self.assertEqual(inf_["futility_threshold"], 0.10)
        self.assertEqual(inf_["futility_z"], 3.0)
        self.assertEqual(inf_["n_permutations"], 999)
        self.assertEqual(inf_["reps_permutation"], 10)
        self.assertEqual(inf_["ncv_reps"], 200)
        self.assertEqual((cfg.resampling["outer_folds_A"], cfg.resampling["reps_A"]), (10, 50))
        self.assertEqual((cfg.resampling["folds_BC"], cfg.resampling["reps_BC"]), (5, 20))
        grid = cfg.lambda_grid_rel
        self.assertEqual(len(grid), 13)
        self.assertAlmostEqual(grid[0], 1e-3)
        self.assertAlmostEqual(grid[-1], 1e3)
        self.assertEqual(cfg.eeg["alpha_channels"], ["P3", "Pz", "P4", "PO3", "POz", "PO4", "O1", "Oz", "O2"])
        self.assertEqual(cfg.eeg["theta_channels"], ["Afz", "Fz", "F1", "F2", "FCz", "Cz"])
        self.assertEqual(cfg.eeg["excluded_band_hz"], [14.5, 17.5])
        self.assertEqual(cfg.syn["corrca_shrinkage"], 0.5)
        self.assertEqual(cfg.data["min_valid_seconds"], 60.0)
        self.assertTrue(cfg.is_frozen)

    def test_edited_frozen_value_is_refused(self):
        text = CONFIG_PATH.read_text().replace("n_permutations = 999", "n_permutations = 99")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "edited.toml"
            p.write_text(text)
            with self.assertRaises(ValueError):
                load_config(p)

    def test_overrides_are_flagged(self):
        cfg = load_config().with_overrides(**{"inference.n_permutations": 19})
        self.assertFalse(cfg.is_frozen)
        self.assertEqual(cfg.inference["n_permutations"], 19)
        with self.assertRaises(KeyError):
            load_config().with_overrides(**{"inference.not_a_key": 1})


class Splits(unittest.TestCase):
    def test_person_folds_grouped_stratified_balanced(self):
        aset = toy_set()
        f = person_folds(aset.exp_of_person, 10, np.random.default_rng(1))
        for e in (3, 4):
            counts = np.bincount(f[aset.exp_of_person == e], minlength=10)
            self.assertLessEqual(counts.max() - counts.min(), 1)
        sizes = np.bincount(f, minlength=10)
        self.assertLessEqual(sizes.max() - sizes.min(), 1)

    def test_outer_folds_deterministic_and_label_addressed(self):
        aset = toy_set()
        a = outer_folds(aset, 10, 3, 7, "toy", "A")
        b = outer_folds(aset, 10, 3, 7, "toy", "A")
        c = outer_folds(aset, 10, 3, 7, "other", "A")
        self.assertTrue(np.array_equal(a, b))
        self.assertFalse(np.array_equal(a, c))
        self.assertFalse(np.array_equal(a[0], a[1]))

    def test_bc_splits_hold_out_person_and_canonical_video(self):
        aset = toy_set()
        fold = person_folds(aset.exp_of_person, 5, np.random.default_rng(2))
        tested = np.zeros(aset.n, int)
        for v, k, test, train in bc_splits(aset, fold):
            self.assertFalse(np.intersect1d(aset.person[test], aset.person[train]).size)
            self.assertFalse(np.intersect1d(aset.video[test], aset.video[train]).size)
            # the shared video is held out in both experiments jointly
            self.assertTrue((aset.video[train] != v).all())
            tested[test] += 1
        self.assertTrue((tested == 1).all())

    def test_inner_folds_cover_training_people(self):
        persons = np.repeat(np.arange(20), 3)
        f = inner_folds(persons, 5, 1, "x")
        self.assertEqual(set(f), set(range(20)))
        self.assertEqual(sorted(np.bincount(list(f.values())).tolist()), [4, 4, 4, 4, 4])


class Learner(unittest.TestCase):
    def test_ridge_path_matches_closed_form(self):
        rng = np.random.default_rng(5)
        X = rng.normal(size=(80, 4))
        y = X @ np.array([1.0, -2.0, 0.5, 0.0]) + rng.normal(size=80)
        lam = 7.0
        Z = (X - X.mean(0)) / X.std(0)
        b = np.linalg.solve(Z.T @ Z + lam * np.eye(4), Z.T @ (y - y.mean()))
        pred = ridge_path(X, y, X[:5], np.array([lam]))[:, 0]
        self.assertTrue(np.allclose(pred, y.mean() + Z[:5] @ b))

    def test_no_feature_model_predicts_training_mean(self):
        y = np.array([0.1, 0.2, 0.6])
        p = ridge_path(np.zeros((3, 0)), y, np.zeros((2, 0)), np.array([1.0]))
        self.assertTrue(np.allclose(p, y.mean()))
        self.assertEqual(choose_lambda(np.zeros((3, 0)), y, np.array([0, 1, 2]), np.array([1.0])), 0.0)

    def test_imputation_uses_training_rows_only(self):
        Xtr = np.array([[1.0, np.nan], [3.0, 4.0]])
        Xte = np.array([[np.nan, 100.0], [1000.0, np.nan]])
        a, b, mu = impute_train_mean(Xtr, Xte)
        self.assertTrue(np.allclose(mu, [2.0, 4.0]))
        self.assertTrue(np.allclose(b, [[2.0, 100.0], [1000.0, 4.0]]))

    def test_model_families_are_the_prespecified_list(self):
        self.assertEqual(FAMILY["M2"].blocks, ("C", "Q"))
        self.assertEqual(FAMILY["M5"].blocks, ("C", "Q", "RF_EEG", "RF_ECG", "RF_GAZE", "SYN_EEG", "SYN_ECG", "SYN_GAZE"))
        self.assertEqual(FAMILY["M5_B"].blocks, ("C", "Q", "RF_EEG", "RF_ECG", "RF_GAZE"))
        self.assertNotIn("SYN_PUPIL", FAMILY["M5"].blocks)


class Pipeline_(unittest.TestCase):
    def setUp(self):
        self.cfg = load_config().with_overrides(**{"resampling.reps_A": 2})
        self.aset = toy_set()
        rng = np.random.default_rng(3)
        n = self.aset.n
        self.blocks = {"C": rng.normal(size=(n, 2)), "Q": rng.normal(size=(n, 2)), "PHYS": rng.normal(size=(n, 3))}
        self.y = np.clip(0.5 + 0.1 * rng.normal(size=n), 0, 1)
        self.prov = FixedFeatureProvider(self.blocks, n)
        self.models = [ModelSpec("BASE", ("C", "Q")), ModelSpec("FULL", ("C", "Q", "PHYS"))]

    def test_content_offsets_A_and_B(self):
        aset, y = self.aset, self.y
        train = aset.person % 3 != 0
        off, resid = content_offsets(aset, y[train], train, ~train, "A")
        ev_mean = pd.Series(y[train]).groupby(aset.ev[train]).mean()
        self.assertTrue(np.allclose(off, ev_mean.reindex(aset.ev[~train]).to_numpy()))
        offB, _ = content_offsets(aset, y[train], train, ~train, "B")
        exp_mean = pd.Series(y[train]).groupby(aset.experiment[train]).mean()
        self.assertTrue(np.allclose(offB, exp_mean.reindex(aset.experiment[~train]).to_numpy()))

    def test_split_rejects_person_overlap(self):
        pipe = Pipeline(self.cfg, self.aset, self.prov, self.models)
        cells = np.flatnonzero(self.aset.person == 0)
        train = np.ones(self.aset.n, bool)
        train[cells[0]] = False
        test = ~train
        with self.assertRaises(AssertionError):
            pipe.fit_split(self.y[train], train, test)

    def test_test_outcomes_cannot_influence_predictions(self):
        pipe = Pipeline(self.cfg, self.aset, self.prov, self.models)
        test = np.isin(self.aset.person, [0, 1, 2])
        res1 = pipe.fit_split(self.y[~test], ~test, test, labels=("t",))
        y2 = self.y.copy()
        y2[test] = 1 - y2[test]          # arbitrary change of test labels only
        res2 = pipe.fit_split(y2[~test], ~test, test, labels=("t",))
        for m in ("BASE", "FULL"):
            self.assertTrue(np.array_equal(res1.preds[m], res2.preds[m]))
            self.assertTrue(((res1.preds[m] >= 0) & (res1.preds[m] <= 1)).all())

    def test_regime_A_tests_every_cell_once_per_repetition_and_is_deterministic(self):
        pipe = Pipeline(self.cfg, self.aset, self.prov, self.models)
        cv1 = run_regime_A(pipe, self.y)
        cv2 = run_regime_A(pipe, self.y)
        for m in ("BASE", "FULL"):
            self.assertTrue(np.isfinite(cv1.preds[m]).all())
            self.assertTrue(np.array_equal(cv1.preds[m], cv2.preds[m]))
        self.assertEqual(cv1.split_id, cv2.split_id)


class Metrics(unittest.TestCase):
    def test_person_balanced_versus_cell_weighted(self):
        person = np.array([0, 0, 0, 1])
        lb = np.array([1.0, 1.0, 1.0, 1.0])
        lf = np.array([0.0, 0.0, 0.0, 1.0])
        self.assertAlmostEqual(met.skill_person_balanced(lb, lf, person), 0.5)
        self.assertAlmostEqual(met.skill_cell_weighted(lb, lf), 0.75)

    def test_within_content_loss_is_shift_invariant(self):
        rng = np.random.default_rng(9)
        y, p = rng.random(60), rng.random(60)
        ev = np.repeat(np.arange(3), 20)
        shifted = p + np.array([0.3, -0.2, 0.1])[ev]
        self.assertTrue(np.allclose(met.within_content_losses(y, p, ev), met.within_content_losses(y, shifted, ev)))

    def test_state_loss_removes_additive_person_and_content(self):
        person = np.repeat(np.arange(6), 3)
        ev = np.tile(np.arange(3), 6)
        y = 0.1 * person + 0.05 * ev
        pred = np.full(len(y), 0.4)
        loss, keep = met.state_losses(y, pred, person, ev)
        self.assertTrue(keep.all())
        self.assertLess(np.nanmax(loss), 1e-20)

    def test_calibration_of_perfect_prediction(self):
        y = np.linspace(0, 1, 13)
        c = met.calibration(y, y)
        self.assertAlmostEqual(c["slope"], 1.0)
        self.assertAlmostEqual(c["intercept"], 0.0)


class Inference(unittest.TestCase):
    def test_person_block_permutation_respects_exchangeability_groups(self):
        aset = toy_set()
        groups = inf.pattern_groups(aset)
        for b in range(20):
            perm = inf.person_block_permutation(aset, np.random.default_rng(b))
            self.assertEqual(sorted(perm.tolist()), list(range(aset.n)))       # bijection
            self.assertTrue((aset.ev[perm] == aset.ev).all())                   # same content unit
            src_person = aset.person
            dst_person = aset.person[perm]
            for (_, pat), members in groups.items():
                m = np.isin(src_person, members)
                self.assertTrue(np.isin(dst_person[m], members).all())         # within group only
                if len(members) == 1:
                    self.assertTrue((perm[m] == np.flatnonzero(m)).all())      # unique patterns fixed
            for p in np.unique(src_person):                                     # whole learners move together
                self.assertEqual(len(np.unique(dst_person[src_person == p])), 1)

    def test_identity_permutation_reproduces_observed_fit(self):
        cfg = load_config().with_overrides(**{"resampling.reps_A": 2})
        aset = toy_set()
        rng = np.random.default_rng(4)
        blocks = {"C": rng.normal(size=(aset.n, 2)), "Q": rng.normal(size=(aset.n, 2)), "PHYS": rng.normal(size=(aset.n, 3))}
        y = np.clip(0.5 + 0.1 * rng.normal(size=aset.n), 0, 1)
        prov = FixedFeatureProvider(blocks, aset.n)
        pipe = Pipeline(cfg, aset, prov, [ModelSpec("BASE", ("C", "Q")), ModelSpec("FULL", ("C", "Q", "PHYS"))])
        cv = run_regime_A(pipe, y, keep_design_reps=2)
        setup = inf.PermutationSetup(cv.designs, "FULL", prov.block_columns("PHYS"), prov.block_columns("C") + prov.block_columns("Q"))
        prepared = inf.prepare_permutation(aset, setup)
        lf = inf.full_model_losses(aset, prepared, y, np.arange(aset.n), cfg.lambda_grid_rel, 1e-12)
        self.assertTrue(np.allclose(lf, met.cell_losses(cv.preds["FULL"], y)))

    def test_permutation_p_value(self):
        self.assertAlmostEqual(inf.permutation_p(1.0, np.array([0.0] * 999)), 1 / 1000)
        self.assertAlmostEqual(inf.permutation_p(0.0, np.array([0.0] * 999)), 1.0)

    def test_holm(self):
        adj = inf.holm({"a": 0.01, "b": 0.04, "c": 0.03, "d": 0.5})
        self.assertAlmostEqual(adj["a"], 0.04)
        self.assertAlmostEqual(adj["c"], 0.09)
        self.assertAlmostEqual(adj["b"], 0.09)
        self.assertAlmostEqual(adj["d"], 0.5)

    def test_h1_decision_table(self):
        d = lambda p, s, u: inf.h1_decision(p, s, u, 0.05, 0.10, 0.05)["category"]
        self.assertEqual(d(0.01, 0.08, 0.2), "detected_useful")
        self.assertEqual(d(0.01, 0.02, 0.2), "detected_small")
        self.assertEqual(d(0.30, 0.01, 0.08), "bounded_negative")
        self.assertEqual(d(0.30, 0.04, 0.12), "inconclusive")

    def test_corrected_t_upper(self):
        fd = np.array([0.001, 0.003, -0.002, 0.0, 0.002])
        r = inf.corrected_t_upper(fd, 10, 3.0, 0.04)
        se = np.sqrt(fd.var(ddof=1) * (1 / 5 + 1 / 9))
        self.assertAlmostEqual(r["upper"], fd.mean() + 3.0 * se)
        self.assertAlmostEqual(r["upper_skill"], (fd.mean() + 3.0 * se) / 0.04)

    def test_nested_cv_interval_bias_correction_and_clipping(self):
        pieces = [dict(a=[1e-6, 2e-6], b=[5e-7, 5e-7], e_in=[np.array([0.002, 0.001])])]
        diffs = np.array([0.001, 0.002, 0.0, 0.003])
        r = inf.nested_cv_interval(pieces, delta_cv=0.001, person_diffs=diffs, base_loss=0.04, K=10)
        se = diffs.std(ddof=1) / 2
        self.assertGreaterEqual(r["hi"] - r["centre"], 1.6448 * se * 0.999)
        self.assertAlmostEqual(r["centre"], 0.0015 - (1 + 8 / 10) * (0.0015 - 0.001))

    def test_two_way_bootstrap_brackets_point_estimate(self):
        aset = toy_set()
        rng = np.random.default_rng(1)
        lb = rng.random(aset.n) + 0.5
        lf = lb * 0.9
        r = inf.two_way_bootstrap(lb, lf, aset, np.random.default_rng(2), 500)
        self.assertLess(r["lo"], 0.1 + 1e-9)
        self.assertGreater(r["hi"], 0.1 - 1e-9)


if __name__ == "__main__":
    unittest.main()
