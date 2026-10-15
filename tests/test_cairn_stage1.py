"""Stage-1 tests for the outcome-free CAIRN infrastructure (Stage-1 spec §2-§3).

Spec §3 leakage tests map to classes as follows:
1 learner independence -> TestFoldsAndPermutations, TestRealData; 2 reference rule -> TestReferences;
3 normalization isolation -> TestFeatures, TestRealData; 4 pretraining isolation -> TestFeatures;
5 anchor freeze -> TestManifestAndGate; 6 outcome gate -> TestManifestAndGate; 7 temporal alignment ->
TestClock; 8 identity probe -> TestRealData; 9 permutation-null sanity -> TestNullCalibration;
10 determinism -> TestModel, TestRealData.

No test reads a quiz outcome. Tests that need the git-ignored derived caches skip when they are absent.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd
from scipy.special import expit

from cairn import clock, design, features as F, gate, inference as I, item_keys, manifest, model
from cairn.paths import DERIVED
from cairn.paths_stage1 import STAGE1_EVIDENCE

HAVE_DATA = (DERIVED / "series10_manifest.parquet").exists()


# ----------------------------------------------------------------------------- toy fixtures
def toy_incidence():
    cells = pd.DataFrame(dict(uid=["c0", "c1", "c2", "c3", "c4", "c5"], person=["p0", "p0", "p1", "p1", "p2", "p2"],
                              experiment=[3] * 6, video=["v1", "v2"] * 3, video_name=["V1", "V2"] * 3,
                              valid_fraction=[.9, .8, .95, .7, .85, .9], n_bins=[600, 500] * 3))
    spans = {"v1": [(5, 15, 0), (5, 15, 0), (30, 40, 1), (None, None, -1)],
             "v2": [(2, 9, 0), (20, 31, 1), (40, 48, 2), (None, None, -1)]}
    rows = []
    for c in cells.itertuples():
        for j, (s, e, m) in enumerate(spans[c.video], start=1):
            rows.append(dict(uid=c.uid, person=c.person, experiment=3, video=c.video, video_name=c.video_name, item=j,
                             question_no=j, item_key=f"e3:{c.video_name}:{j}", category="R", k_keyed=1,
                             anchorable=s is not None, start=np.nan if s is None else float(s),
                             end=np.nan if e is None else float(e), moment=m,
                             anchor_pos=np.nan if s is None else (s + e) / 2 / 60, quiz_pos=(j - 1) / 3))
    return design.Incidence("toy", cells, pd.DataFrame(rows), {"v1": 60, "v2": 50}, "x", True)


def toy_split(inc, train_persons, seed=0):
    rng = np.random.default_rng(seed)
    arrays, idx = {}, {}
    for v, n_s in inc.n_s.items():
        ci = list(np.flatnonzero((inc.cells.video == v).to_numpy()))
        A = rng.normal(size=(len(ci), n_s, len(F.PRIMARY)))
        A[0, 3:6, 2] = np.nan
        arrays[v], idx[v] = A, ci
    return F.SplitChannels("k", inc.set_name, "A", frozenset(train_persons), list(inc.cells.uid), list(inc.cells.video),
                           arrays, idx, np.zeros(len(F.PRIMARY)), np.ones(len(F.PRIMARY)))


# ----------------------------------------------------------------------------- design
class TestDesign(unittest.TestCase):
    def test_moment_groups_single_linkage(self):
        g = design.moment_groups(np.array([60.0, 10.0, 15.0, 31.0, 30.0]))
        np.testing.assert_array_equal(g, [2, 0, 0, 1, 1])

    def test_anchor_table_rejects_outcome_columns(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "a.csv"
            cols = ["canonical_video_id", "video", "item", "question_no", "category", "k_keyed", "anchorable",
                    "rec_start_s", "rec_end_s", "rec_centre_s", "is_correct"]
            pd.DataFrame([dict.fromkeys(cols, 1)]).to_csv(p, index=False)
            with self.assertRaises(AssertionError):
                design.anchor_table(p)

    def test_sets_follow_plan_partition(self):
        self.assertEqual({s["experiment"] for s in design.SETS["development"]}, {1, 3})
        self.assertEqual({s["experiment"] for s in design.SETS["locked_pooled"]}, {4, 5})
        self.assertNotIn(4, {s["experiment"] for s in design.SETS["development"]})

    @unittest.skipUnless(HAVE_DATA, "derived series absent")
    def test_set_incidence_matches_plan(self):
        for s in ("development", "locked_primary", "locked_secondary", "locked_pooled"):
            inc = design.build(s)
            sm = inc.summary()
            self.assertEqual((sm["learners"], sm["cells"], sm["videos"]), design.EXPECTED_COUNTS[s])
        e4 = design.build("locked_primary").summary()
        self.assertEqual((e4["anchorable_items"], e4["distinct_moments"]), (26, 19))


class TestItemKeys(unittest.TestCase):
    def test_key_map_is_one_to_one_from_item_content(self):
        m = item_keys.key_map()
        self.assertEqual(len(m), 203)
        self.assertFalse(m.duplicated(["experiment", "canonical_video_id", "item"]).any())

    def test_verify_item_table(self):
        m = item_keys.key_map()
        r = m.iloc[:3][["experiment", "local_stimulus_id", "question_no", "canonical_video_id"]].copy()
        out = item_keys.verify_item_table(r, m)
        self.assertTrue(out.item.notna().all())
        bad = r.copy()
        bad.loc[bad.index[0], "question_no"] = 99
        with self.assertRaises(AssertionError):
            item_keys.verify_item_table(bad, m)


# ----------------------------------------------------------------------------- clock (spec test 7)
class TestClock(unittest.TestCase):
    def test_round_trip_every_second(self):
        tab = clock.table()
        for r in tab.itertuples():
            for t in np.arange(r.rec_start_s, r.rec_end_s, 7) + 0.5:
                src, vs = clock.rec_to_source(r.canonical_video_id, t, tab)
                self.assertAlmostEqual(clock.source_to_rec(r.canonical_video_id, src, vs, tab), t, places=9)

    def test_anchor_on_fail_second_rejected(self):
        rows = pd.DataFrame([dict(anchorable=True, video="zQGOcOUBi6s", video_name="Immune", item=99, start=213.0, end=217.0)])
        with self.assertRaises(AssertionError):
            clock.assert_anchors_on_pass_seconds(rows)
        ok = rows.assign(start=100.0, end=104.0)
        clock.assert_anchors_on_pass_seconds(ok)


# ----------------------------------------------------------------------------- features
class TestFeatures(unittest.TestCase):
    def test_long_loss_counts_only_long_episodes(self):
        v = np.ones(60)
        v[5:20] = 0.0      # 1.5 s episode
        v[40:43] = 0.0     # 0.3 s episode
        ll = F.long_loss(v, 6)
        np.testing.assert_allclose(ll, [0.5, 1.0, 0.0, 0.0, 0.0, 0.0])

    def test_detrend_removes_slope_keeps_mean(self):
        t = np.arange(100.0)
        A = (3 + 0.5 * t)[None, :, None] + np.zeros((1, 100, 1))
        A[0, 10:20, 0] = np.nan
        D = F.detrend(A)
        ok = np.isfinite(D[0, :, 0])
        self.assertLess(np.ptp(D[0, ok, 0]), 1e-9)
        self.assertAlmostEqual(np.nanmean(D), np.nanmean(A), places=9)

    def test_window_bounds_match_hard_kernel(self):
        from cairn import pooling
        rng = np.random.default_rng(0)
        for _ in range(200):
            s = rng.uniform(0, 80)
            e = s + rng.uniform(1, 30)
            lo, hi = F.window_bounds(np.array([s]), np.array([e]), np.array([120]))
            k = pooling.kernel(120, s, e, "hard")
            np.testing.assert_array_equal(np.flatnonzero(k > 0), np.arange(lo[0], hi[0]))

    def test_pooler_means_and_circular_shift(self):
        inc = toy_incidence()
        sc = toy_split(inc, {"p0", "p1"})
        pl = F.Pooler(inc, sc)
        z = pl.means()
        a = inc.rows[inc.rows.anchorable].reset_index(drop=True)
        for i, r in a.iterrows():
            ci = inc.cells.index[inc.cells.uid == r.uid][0]
            A = sc.arrays[r.video][sc.cell_index[r.video].index(ci)]
            lo, hi = F.window_bounds(np.array([r.start]), np.array([r.end]), np.array([inc.n_s[r.video]]))
            seg = A[lo[0]:hi[0]]
            cov = np.isfinite(seg).mean(0)
            exp = np.where(cov > F.MIN_COVERAGE, np.nanmean(seg, 0), np.nan)
            np.testing.assert_allclose(z[i], exp, equal_nan=True)
        # circular shift equals rolling the series
        shift = np.full(len(a), 45)
        zs = pl.means(shift=shift)
        for i, r in a.iterrows():
            ci = inc.cells.index[inc.cells.uid == r.uid][0]
            A = np.roll(sc.arrays[r.video][sc.cell_index[r.video].index(ci)], -45, axis=0)
            lo, hi = F.window_bounds(np.array([r.start]), np.array([r.end]), np.array([inc.n_s[r.video]]))
            seg = A[lo[0]:hi[0]]
            exp = np.where(np.isfinite(seg).mean(0) > F.MIN_COVERAGE, np.nanmean(seg, 0), np.nan)
            np.testing.assert_allclose(zs[i], exp, equal_nan=True)

    def test_moment_regressors_within_cell_and_training_only(self):
        rng = np.random.default_rng(1)
        cell = np.repeat(np.arange(10), 4)
        item = np.tile(np.arange(4), 10)
        train = cell < 7
        m = rng.normal(size=(40, 2))
        x0, st = F.moment_regressors(m, cell, item, train, return_stats=True)
        # within-cell centring before item centring: cell sums of the centred terms are zero
        np.testing.assert_allclose(np.bincount(cell, F.within_cell_centre(m, cell)[:, 0]), 0, atol=1e-12)
        # training statistics do not depend on test rows
        m2 = m.copy()
        m2[~train] += 100.0
        x1, st1 = F.moment_regressors(m2, cell, item, train, return_stats=True)
        np.testing.assert_allclose(st["item_mean"], st1["item_mean"])
        np.testing.assert_allclose(st["sd"], st1["sd"])
        np.testing.assert_allclose(x0[train], x1[train])

    def test_fold_encoder_uses_training_cells_only(self):          # spec test 4
        inc = toy_incidence()
        sc = toy_split(inc, {"p0", "p1"})
        e1 = F.fit_fold_encoder(sc, inc.cells, K=2)
        sc2 = toy_split(inc, {"p0", "p1"})
        for v in sc2.arrays:                                          # perturb only the test learner p2
            for i, ci in enumerate(sc2.cell_index[v]):
                if inc.cells.person.iloc[ci] == "p2":
                    sc2.arrays[v][i] += 50.0
        e2 = F.fit_fold_encoder(sc2, inc.cells, K=2)
        np.testing.assert_array_equal(e1.B, e2.B)
        self.assertEqual(e1.fitted_on, frozenset({"p0", "p1"}))


class TestReferences(unittest.TestCase):                              # spec test 2
    def setUp(self):
        self.cells = pd.DataFrame(dict(uid=[f"u{i}" for i in range(8)], person=["a", "a", "b", "b", "c", "c", "d", "d"],
                                       experiment=[4] * 8, video=["v", "w"] * 4))

    def test_regime_a_training_only_never_self(self):
        refs = F.regime_a_references(self.cells, {"a", "b", "c"})
        person = dict(zip(self.cells.uid, self.cells.person))
        for u, rs in refs.items():
            self.assertNotIn(person[u], {person[r] for r in rs})
            self.assertTrue({person[r] for r in rs} <= {"a", "b", "c"})
        self.assertEqual({person[r] for r in refs["u6"]}, {"a", "b", "c"})   # test learner d: all training peers

    def test_regime_c_depends_on_ids_only(self):
        h1 = F.regime_c_halves(self.cells.person, seed=3)
        shuffled = self.cells.sample(frac=1, random_state=0).assign(quality=np.arange(8), condition="x")
        h2 = F.regime_c_halves(shuffled.person, seed=3)
        self.assertEqual(h1, h2)
        refs = F.regime_c_references(self.cells, seed=3)
        person = dict(zip(self.cells.uid, self.cells.person))
        for u, rs in refs.items():
            self.assertTrue(all(h1[person[r]] != h1[person[u]] for r in rs))


# ----------------------------------------------------------------------------- model
class TestModel(unittest.TestCase):
    def _data(self, seed=0, P=30, K=24):
        rng = np.random.default_rng(seed)
        p = np.repeat(np.arange(P), K)
        k = np.tile(np.arange(K), P)
        G = np.eye(2)[k // 12]
        x = rng.normal(size=len(p))
        beta = rng.normal(0.5, 1.0, K)
        u = rng.normal(0, 0.7, P)
        y = (rng.random(len(p)) < expit(beta[k] + u[p] + 0.4 * x)).astype(float)
        return p, k, G, x, y, P, K

    def test_newton_matches_logistic_when_random_effects_vanish(self):
        p, k, G, x, y, P, K = self._data()
        f = model.Fitter(k, p, K, P)
        D = np.column_stack([G, x])
        prm = f.newton(D, y, np.array([0.0, 0.0, 1e-8]), tau2=1e-8, sb2=1e-8)
        w, _ = model.penalized_logistic(np.column_stack([np.ones(len(y)), G[:, 1], x]), y, np.array([0.0, 0.0, 1e-8]))
        np.testing.assert_allclose(prm.b[2], w[2], atol=1e-5)

    def test_fit_is_deterministic(self):                                 # spec test 10 (model level)
        p, k, G, x, y, P, K = self._data(1)
        f = model.Fitter(k, p, K, P)
        D = np.column_stack([G, x])
        a = f.fit_em(D, y, np.array([1e-4, 1e-4, 1.0]))
        b = f.fit_em(D, y, np.array([1e-4, 1e-4, 1.0]))
        np.testing.assert_array_equal(a.b, b.b)
        self.assertEqual(a.tau2, b.tau2)
        self.assertGreater(a.b[-1], 0.15)

    def test_marginal_prediction_approximates_integral(self):
        prm = model.Params(np.zeros(1), np.zeros(1), np.array([0.0]), tau2=1.2, sb2=1.0)
        for eta in (-2.0, -0.5, 0.0, 1.0, 2.5):
            z = np.random.default_rng(0).normal(0, np.sqrt(1.2), 200000)
            mc = expit(eta + z).mean()
            p = model.predict_marginal(prm, np.array([0]), np.array([[1.0]]), offset=np.array([eta]))[0]
            self.assertAlmostEqual(p, mc, delta=0.01)


# ----------------------------------------------------------------------------- folds, permutations, metrics
class TestFoldsAndPermutations(unittest.TestCase):
    def test_stratified_group_folds(self):
        persons = np.array([f"p{i}" for i in range(23)])
        strata = np.array([4] * 13 + [5] * 10)
        f1 = I.stratified_group_folds(persons, strata, 5, 7)
        f2 = I.stratified_group_folds(persons, strata, 5, 7)
        self.assertEqual(f1, f2)
        for s in (4, 5):
            counts = np.bincount([f1[p] for p in persons[strata == s]], minlength=5)
            self.assertLessEqual(counts.max() - counts.min(), 1)

    def test_perm_p(self):
        self.assertAlmostEqual(I.perm_p(1.0, np.array([0.0, 2.0, 0.5, 1.0])), 3 / 5)

    def test_cell_auc_matches_reference(self):
        from cairn.stats import auc
        rng = np.random.default_rng(2)
        y = rng.integers(0, 2, 40).astype(float)
        p = rng.random(40)
        cell = np.repeat(np.arange(4), 10)
        a = I.cell_auc(y, p, cell)
        for c in range(4):
            m = cell == c
            ref = auc(y[m], p[m])
            if np.isnan(ref):
                self.assertTrue(np.isnan(a[c]))
            else:
                self.assertAlmostEqual(a[c], ref)

    def test_corrected_upper(self):
        d = np.array([0.01, 0.02, 0.0, 0.015, 0.005])
        self.assertGreater(I.corrected_upper(d, 5, 3.0), I.corrected_upper(d, 5, 1.645))


@unittest.skipUnless(HAVE_DATA, "derived series absent")
class TestRealData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.S = I.build_structure(design.build("locked_primary"))

    def test_learner_independence_every_split(self):                     # spec test 1
        S = self.S
        for sp in S.splits:
            self.assertFalse(set(S.person[sp.train]) & set(S.person[sp.test]))
        for r in range(I.R_REPS):
            tested = np.concatenate([np.flatnonzero(sp.test) for sp in S.splits if sp.rep == r])
            self.assertEqual(sorted(tested), list(range(S.n)))                # each row tested exactly once per repetition

    def test_learner_block_permutation_moves_whole_learners(self):
        S = self.S
        perm = I.learner_block_permutation(S, np.random.default_rng(0))
        tgt = np.array([t[0] for t in S.anch_pvj])
        src = np.array([S.anch_pvj[i][0] for i in perm])
        for p in np.unique(tgt):
            self.assertEqual(len(set(src[tgt == p])), 1)
            q = src[tgt == p][0]
            self.assertEqual(S.person_exp[p], S.person_exp[q])
        self.assertEqual(sorted(perm), list(range(len(perm))))               # a bijection

    def test_relocation_identity_and_moment_sharing(self):
        S = self.S
        ident = {v: np.arange(n) for v, n in S.n_moments.items()}
        d = I.relocation_shift(S, ident)
        np.testing.assert_array_equal(d, 0.0)
        sp = S.splits[0]
        np.testing.assert_allclose(I.relocated_terms(S, sp, d), sp.mb.m, equal_nan=True)
        perm = I.moment_permutation(S, np.random.default_rng(1))
        d = I.relocation_shift(S, perm)
        for v in S.n_moments:                                               # items of one moment move together
            sel = S.anch_video == v
            for mm in np.unique(S.anch_moment[sel]):
                self.assertEqual(len(np.unique(np.round(d[sel][S.anch_moment[sel] == mm], 6))), 1)

    def test_circular_shift_at_least_30s(self):
        S = self.S
        sh = I.circular_shift(S, np.random.default_rng(3))
        for v, n_s in S.inc.n_s.items():
            s = sh[S.anch_video == v]
            self.assertEqual(len(np.unique(s)), 1)
            self.assertTrue(I.CIRC_MIN_S <= s[0] <= n_s - I.CIRC_MIN_S)

    def test_determinism_of_a_replicate(self):                            # spec test 10
        from cairn import simulate as SIM
        T = SIM.build_truth(self.S)
        sc = SIM.Scenario("ALT", 1.35, 0.4)
        a = SIM.run_replicate(self.S, T, sc, 5, 11, 3, mode="n1decision")
        b = SIM.run_replicate(self.S, T, sc, 5, 11, 3, mode="n1decision")
        for k in a:
            if k != "seconds":
                self.assertTrue(a[k] == b[k] or (isinstance(a[k], float) and np.isnan(a[k]) and np.isnan(b[k])), k)

    def test_identity_probe_item_centred_at_chance(self):                 # spec test 8
        from cairn import checks
        r = checks.check_identity_probe("development", n_perm=9)
        self.assertTrue(r["passed"], r)

    def test_fold_safety_on_real_split(self):                             # spec tests 1-3 on real data
        from cairn import checks
        r = checks.check_fold_safety("locked_primary")
        self.assertTrue(r["passed"], r)


# ----------------------------------------------------------------------------- gate, CLI, manifests
class TestManifestAndGate(unittest.TestCase):
    def test_cli_run_refuses_without_freeze(self):                       # spec test 6
        from cairn import cli
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(gate, "FREEZE_RECORD", Path(td) / "FREEZE_RECORD.json"), \
                mock.patch.object(gate, "AUTHORIZATION", Path(td) / "AUTHORIZATION.json"), \
                mock.patch("pandas.read_parquet", side_effect=AssertionError("outcome file opened")):
            for scope in ("development", "locked_primary"):
                self.assertEqual(cli.main(["run", "--scope", scope]), 2)

    def test_no_cairn_freeze_or_authorization_or_access_log(self):
        self.assertFalse(gate.FREEZE_RECORD.exists())
        self.assertFalse(gate.AUTHORIZATION.exists())
        self.assertFalse(gate.ACCESS_LOG.exists())

    def test_manifest_refuses_provisional_anchors_after_stage1(self):    # spec test 5
        m = dict(stage="2-development", inputs={}, anchor_freeze_sha256=None, anchor_provisional=True)
        bad = manifest.verify_inputs(m)
        self.assertTrue(any("anchor_freeze" in b for b in bad))
        self.assertTrue(any("provisional" in b for b in bad))
        with self.assertRaises(ValueError):
            manifest.build("x", "2-development", [], "A", [], {}, {}, {}, {}, outcome_access="none")

    def test_manifest_hash_ignores_timestamp_only(self):
        m = dict(a=1, created_utc="t1")
        self.assertEqual(manifest.manifest_sha256(m), manifest.manifest_sha256(dict(m, created_utc="t2")))
        self.assertNotEqual(manifest.manifest_sha256(m), manifest.manifest_sha256(dict(m, a=2)))


# ----------------------------------------------------------------------------- null calibration (spec test 9)
class TestNullCalibration(unittest.TestCase):
    """Reads the stored Stage-1 simulation output (synthetic outcomes) when present."""

    def _load(self, set_name, scen):
        p = STAGE1_EVIDENCE / "sim" / set_name / f"{scen}.jsonl"
        if not p.exists():
            self.skipTest(f"{p} absent")
        return pd.DataFrame([json.loads(line) for line in p.read_text().splitlines() if line.strip()])

    def test_pure_null_p_values_are_uniform(self):
        from scipy.stats import kstest
        for set_name in ("locked_primary", "development"):
            d = self._load(set_name, "N0_or1_rho0.4_q0.5")
            for c in [c for c in d.columns if c.endswith(("p_T1", "p_T2", "p_T2c", "p_T1lr", "p_T2lr", "p_T2clr"))]:
                p = d[c].dropna().to_numpy()
                # randomized (mid-rank) p-values remove the discreteness of the permutation grid
                pr = p - np.random.default_rng(0).random(len(p)) / (1 + d.B.iloc[0])
                self.assertGreater(kstest(pr, "uniform").pvalue, 0.001, f"{set_name} {c}")
                self.assertLessEqual((p <= 0.05).mean(), 0.07, f"{set_name} {c}")



@unittest.skipUnless(HAVE_DATA, "derived series absent")
class TestBaselines(unittest.TestCase):
    def test_interface_matches_cv_engine_and_refuses_test_outcomes(self):
        from cairn import baselines as BL
        S = I.build_structure(design.build("locked_primary"))
        sp = S.splits[0]
        rng = np.random.default_rng(0)
        y = (rng.random(S.n) < 0.6).astype(float)
        with self.assertRaises(ValueError):
            BL.ItemData(S, sp, y)                       # test outcomes present -> refused
        yt = np.where(sp.train, y, np.nan)
        tr = te = BL.ItemData(S, sp, yt)
        ff = I.fit_base(S, sp, y)
        for name, m in BL.ladder("dt").items():
            if isinstance(m, BL._Unavailable):
                with self.assertRaises(BL.MissingDependency):
                    m.fit(tr, {}, rng)
                continue
            if isinstance(m, BL.FrozenRidge):
                tr.video_features = te.video_features = rng.normal(size=(len(S.inc.cells), 3))
            p = m.fit(tr, {}, rng).predict_proba(te)
            self.assertEqual(len(p), int(sp.test.sum()), name)
            self.assertTrue(np.all((p > 0) & (p < 1)), name)
            self.assertGreater(m.n_params(), 0)
        np.testing.assert_allclose(BL.GLMM(I.BASE).fit(tr).predict_proba(te), ff.p_base)
        _, p6 = I.fit_variant(S, sp, ff, I.CL6_DT, y)
        np.testing.assert_allclose(BL.GLMM(I.CL6_DT).fit(tr).predict_proba(te), p6)


@unittest.skipUnless(HAVE_DATA, "derived series absent")
class TestNestedCV(unittest.TestCase):
    def test_nested_cv_interval_brackets_and_is_fold_safe(self):
        S = I.build_structure(design.build("locked_primary"))
        rng = np.random.default_rng(4)
        y = (rng.random(S.n) < 0.62).astype(float)
        r = I.nested_cv(S, y, I.CL6_DT, reps=1)
        self.assertLess(r["s_item_lo"], r["s_item_hi"])
        self.assertTrue(np.isfinite(r["root_over_se"]))
        self.assertLessEqual(r["s_item_lo"], 0.01)          # pure-noise outcomes: the interval must reach below .01


@unittest.skipUnless(HAVE_DATA, "derived series absent")
class TestKernel(unittest.TestCase):
    """Kernel lag / width grid (spec §2.2; S1-D11): windows move, moments and nulls keep their form."""

    def test_default_kernel_is_identity_and_grid_is_small(self):
        a = design.build("locked_primary")
        pd.testing.assert_frame_equal(a.rows, design.build("locked_primary", kernel=(0, 0)).rows)
        self.assertLessEqual(len(design.KERNEL_GRID), 20)
        self.assertIn(design.KERNEL_DEFAULT, design.KERNEL_GRID)

    def test_kernel_moves_and_widens_windows_only(self):
        a = design.build("locked_primary")
        b = design.build("locked_primary", kernel=(5.0, 10.0))
        m = a.rows.anchorable.to_numpy()
        hi = a.rows.video.map(a.n_s).to_numpy(float)[m]
        np.testing.assert_allclose(b.rows.start[m], np.clip(a.rows.start[m] - 5.0, 0, hi))
        np.testing.assert_allclose(b.rows.end[m], np.clip(a.rows.end[m] + 15.0, 0, hi))
        for col in ("moment", "anchor_pos", "anchorable", "item_key"):
            pd.testing.assert_series_equal(a.rows[col], b.rows[col])
        with self.assertRaises(ValueError):
            design.build("locked_primary", kernel=(0.0, -1.0))

    def test_nulls_run_under_a_kernel(self):
        S = I.build_structure(design.build("locked_primary", kernel=(-5.0, 5.0)), reps=1)
        rng = np.random.default_rng(2)
        y = (rng.random(S.n) < 0.6).astype(float)
        cv = I.cv_evaluate(S, y, [I.CL6_DT])
        r = I.run_tests(S, y, cv, I.CL6_DT, 9, rng, ("T1", "T2", "T2c", "T1lr", "T2lr"))
        for t in ("T1", "T2", "T2c", "T1lr", "T2lr"):
            self.assertTrue(0.1 <= r[t] <= 1.0, (t, r[t]))


if __name__ == "__main__":
    unittest.main()
