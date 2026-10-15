"""Closure-phase tests (docs/research/novel_method/closure): polynomial within-recording detrending, the
parametrizations P0 / PT / PD / PA, the exact min-p combination, joint permutation tests, the NH4 conditional test,
the new temporal nulls and the closure replicate runner. No test reads a quiz outcome; real-data tests skip when the
git-ignored derived caches are absent."""
from __future__ import annotations

import unittest

import numpy as np

from cairn import design, features as F, inference as I, simulate as SIM
from cairn.paths import DERIVED

HAVE_DATA = (DERIVED / "series10_manifest.parquet").exists()


class TestPolynomialDetrend(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(0)
        t = np.linspace(-1, 1, 240)
        self.A = rng.normal(size=(4, 240, 3)) + (2 + 3 * t - 4 * t ** 2 + 2 * t ** 3)[None, :, None]
        self.A[0, 20:60, 1] = np.nan
        self.t = t

    def test_degree_one_matches_stage1_detrend(self):
        np.testing.assert_allclose(F.detrend_poly(self.A, 1), F.detrend(self.A), atol=1e-10)

    def test_mean_kept_and_polynomial_removed(self):
        for d in (2, 3):
            D = F.detrend_poly(self.A, d)
            np.testing.assert_allclose(np.nanmean(D, 1), np.nanmean(self.A, 1), atol=1e-10)
            for c in range(4):
                ok = np.isfinite(D[c, :, 1])
                coef = np.polynomial.legendre.legfit(self.t[ok], D[c, ok, 1], d)
                np.testing.assert_allclose(coef[1:], 0.0, atol=1e-9)

    def test_fold_safe_by_construction(self):
        """Each series is detrended from its own seconds only: changing one cell leaves the others unchanged."""
        B = self.A.copy()
        B[2] = B[2] * 5 + 7
        np.testing.assert_array_equal(F.detrend_poly(self.A, 2)[[0, 1, 3]], F.detrend_poly(B, 2)[[0, 1, 3]])

    def test_degenerate_series_left_unchanged(self):
        A = np.full((1, 50, 1), np.nan)
        A[0, :3, 0] = [1.0, 2.0, 3.0]
        np.testing.assert_array_equal(F.detrend_poly(A, 2), A)


class TestMinP(unittest.TestCase):
    def test_single_statistic_equals_perm_p(self):
        rng = np.random.default_rng(1)
        st = rng.normal(size=(200, 1))
        st[3] = st[0]                                     # a tie
        self.assertAlmostEqual(I.minp_from_stats(st), I.perm_p(st[0, 0], st[1:, 0]))

    def test_exact_level_under_exchangeability(self):
        rng = np.random.default_rng(2)
        ps = []
        for _ in range(2000):
            z = rng.normal(size=(100, 1))
            st = np.hstack([z, 0.7 * z + 0.7 * rng.normal(size=(100, 1))])   # two correlated statistics
            ps.append(I.minp_from_stats(st))
        ps = np.array(ps)
        self.assertLess(abs(np.mean(ps <= 0.05) - 0.05), 0.015)
        self.assertTrue(np.all((ps > 0) & (ps <= 1)))

    def test_minp_at_least_as_small_as_needed(self):
        st = np.vstack([[10.0, -1.0], np.random.default_rng(3).normal(size=(99, 2))])
        self.assertLessEqual(I.minp_from_stats(st), 2 / 100)


class TestParametrizations(unittest.TestCase):
    def test_unit_direction_is_construct_signed_equal_weight(self):
        w = I.UNIT_W
        self.assertAlmostEqual(float(np.linalg.norm(w)), 1.0)
        np.testing.assert_allclose(np.abs(w), 1 / np.sqrt(6))
        self.assertEqual(list(np.sign(w)), [F.ENGAGED_SIGN[c] for c in F.PRIMARY])

    def test_complement_basis_is_orthonormal_complement(self):
        Q = I.complement_basis(I.UNIT_W)
        self.assertEqual(Q.shape, (6, 5))
        np.testing.assert_allclose(Q.T @ Q, np.eye(5), atol=1e-12)
        np.testing.assert_allclose(Q.T @ I.UNIT_W, 0.0, atol=1e-12)

    def test_ridge_vectors(self):
        pt = I.aniso_variant(2)
        np.testing.assert_array_equal(pt.r_m_vec(6), np.r_[1.0, np.full(5, 100.0)])
        self.assertEqual(pt.degree, 2)
        np.testing.assert_array_equal(I.six_variant(2).r_m_vec(6), np.full(6, 100.0))
        np.testing.assert_array_equal(I.unit_variant(3).r_m_vec(1), [1.0])
        g = I.gaze_given_validity_variant(2)
        np.testing.assert_array_equal(g.r_m_vec(5), np.r_[1.0, np.full(4, 100.0)])
        self.assertIs(I.six_variant(1), I.CL6_DT)          # the Stage-1 primary is reused, not re-defined

    def test_existing_variants_unchanged(self):
        self.assertEqual(I.CL6_DT.degree, 1)
        self.assertEqual(I.CL6.degree, 0)
        np.testing.assert_array_equal(I.CL6_DT.r_m_vec(6), np.full(6, I.R_M_MULTI))


class TestScenarios(unittest.TestCase):
    def test_closure_null_strengths_match_n1q_by_rms(self):
        x = np.linspace(-1, 1, 200001)
        rms = lambda f: float(np.sqrt(np.mean((f - f.mean()) ** 2)))
        q = rms(x ** 2 - 1 / 3) * SIM.N1Q_KAPPA
        self.assertAlmostEqual(rms((5 * x ** 3 - 3 * x) / 2) * SIM.N1C_KAPPA, q, places=4)
        self.assertAlmostEqual(rms(np.exp(-2 * (x + 1))) * SIM.N1E_KAPPA, q, places=4)

    def test_keys_distinguish_development_truth(self):
        a = SIM.Scenario("ALT", 1.5, 0.4, truth="random")
        b = SIM.Scenario("ALT", 1.5, 0.4, truth="random", dev_truth="random_indep")
        self.assertNotEqual(a.key, b.key)
        self.assertEqual(SIM.Scenario("N0").key, "N0_or1_rho0.4_q0.5")     # Stage-1 keys unchanged

    def test_random_direction_is_sign_coherent(self):
        sign = np.array([F.ENGAGED_SIGN[c] for c in F.PRIMARY])
        w = SIM.random_direction(np.random.default_rng(0), sign)
        self.assertAlmostEqual(float(np.linalg.norm(w)), 1.0)
        self.assertTrue(np.all(np.sign(w) == sign))


@unittest.skipUnless(HAVE_DATA, "derived caches absent")
class TestClosureRealData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.S = I.build_structure(design.build("locked_primary"), reps=1, degrees=(2,))
        cls.T = SIM.build_truth(cls.S)

    def test_structure_degrees(self):
        sp = self.S.splits[0]
        self.assertIsNone(sp.mb)
        self.assertIn(2, sp.extra)
        self.assertIsNotNone(self.S.canonical.mb)          # truth is built from raw channels
        self.assertIs(sp.block(I.six_variant(2)), sp.extra[2][1])

    def test_joint_lr_equals_single_variant_tests(self):
        y, _ = SIM.generate(self.S, self.T, SIM.Scenario("ALT", 1.5, 0.4), 0, np.random.default_rng(5))
        v = I.six_variant(2)
        a = I.lr_tests_joint(self.S, y, [v], 9, np.random.default_rng(11), ("T1lr", "T2lr", "T2clr"))
        cv = I.cv_evaluate(self.S, y, [v])
        b = I.run_tests(self.S, y, cv, v, 9, np.random.default_rng(11), ("T1lr", "T2lr", "T2clr"))
        for t in ("T1lr", "T2lr", "T2clr"):
            self.assertEqual(a[f"{v.name}|p_{t}"], b[t])

    def test_joint_cv_equals_single_variant_tests(self):
        y, _ = SIM.generate(self.S, self.T, SIM.Scenario("ALT", 1.5, 0.4), 1, np.random.default_rng(6))
        v = I.unit_variant(2)
        cv = I.cv_evaluate(self.S, y, [v])
        a = I.cv_tests_joint(self.S, y, cv, [v], 4, np.random.default_rng(12), ("T1", "T2"))
        b = I.run_tests(self.S, y, cv, v, 4, np.random.default_rng(12), ("T1", "T2"))
        for t in ("T1", "T2"):
            self.assertEqual(a[f"{v.name}|p_{t}"], b[t])

    def test_nuisance_column_never_permuted(self):
        S = self.S
        sp = S.canonical
        v = I.gaze_given_validity_variant(2)
        true = I.moment_columns(S, sp, v, sp.block(v).m)
        perm = I.learner_block_permutation(S, np.random.default_rng(0))
        moved = I.moment_columns(S, sp, v, sp.block(v).m[perm])
        np.testing.assert_array_equal(true[:, 0], moved[:, 0])
        self.assertFalse(np.array_equal(true[:, 1:], moved[:, 1:]))

    def test_aniso_first_column_is_unit_composite(self):
        S, sp = self.S, self.S.canonical
        a = I.moment_columns(S, sp, I.aniso_variant(2), sp.block(I.aniso_variant(2)).m)
        u = I.moment_columns(S, sp, I.unit_variant(2), sp.block(I.unit_variant(2)).m)
        np.testing.assert_allclose(a[:, 0], u[:, 0], atol=1e-12)

    def test_closure_replicate_deterministic(self):
        sc = SIM.Scenario("N1c")
        r1 = SIM.run_replicate_closure(self.S, self.T, sc, 2, 77, 5, "rg", 2, self.S, self.T)
        r2 = SIM.run_replicate_closure(self.S, self.T, sc, 2, 77, 5, "rg", 2, self.S, self.T)
        keys = [k for k in r1 if k != "seconds"]
        self.assertTrue(all(r1[k] == r2[k] or (isinstance(r1[k], float) and np.isnan(r1[k]) and np.isnan(r2[k]))
                            for k in keys))
        self.assertIn("CAIRN-a-dt2|p_T2lr", r1)            # the adaptive min-p combination is recorded

    def test_random_truth_direction_used(self):
        sc = SIM.Scenario("ALT", 2.0, 0.7, truth="random")
        r = SIM.run_replicate_closure(self.S, self.T, sc, 0, 3, 3, "rg", 2, self.S, self.T)
        self.assertIn("w_truth", r)
        self.assertIn("dev_dir_cosine", r)


if __name__ == "__main__":
    unittest.main()


# ----------------------------------------------------------------------------- G-AN tooling (closure C-D10)
def _fake_human_files(tmp, jitter=(0.0, 2.0), seed=0):
    """Two synthetic 'human' sheets derived from the R2 machine sheet (test fixtures only; never real annotations)."""
    import pandas as pd
    from cairn import anchors as A
    from cairn.paths import STAGE0
    r2 = pd.read_csv(STAGE0 / "annotation" / "anchors_R2_llm_provisional.csv", dtype={"source": str})
    bank = A.item_bank().set_index(["video", "item"])
    rng = np.random.default_rng(seed)
    paths = []
    for k, j in enumerate(jitter, start=1):
        d = pd.DataFrame(dict(annotator_id=f"H-TEST-{k}", video=r2.video, item=r2.item, source=r2.source,
                              span_start_s=r2.span_start_s, span_end_s=r2.span_end_s, extra_spans=r2.extra_spans,
                              type=r2.type, category=[bank.loc[(v, i)].category for v, i in zip(r2.video, r2.item)],
                              confidence=r2.confidence, key_check=r2.key_check, visual_only=r2.visual_check,
                              ambiguity_note=""))
        d["type"] = d.type.replace({"absent_narration": "absent"})          # R2 used two non-protocol labels
        d["key_check"] = d.key_check.replace({"questionable": "partial", "not_in_narration": "not_in_video"})
        d.loc[(d.type == "localized") & (d.span_end_s - d.span_start_s > 45), "type"] = "diffuse"
        sh = rng.uniform(-j, j, len(d))
        d.loc[d.type.isin(["localized", "multi_span"]), "span_start_s"] = np.maximum(0, d.span_start_s + sh)
        d.loc[d.type.isin(["localized", "multi_span"]), "span_end_s"] = d.span_end_s + sh
        from cairn.gan import source_duration
        dur = d.source.map(lambda s_: source_duration(str(s_)) or 1e9)
        d["span_end_s"] = np.minimum(d.span_end_s, dur).clip(lower=1.0)
        d["span_start_s"] = np.minimum(d.span_start_s, d.span_end_s - 1.0).clip(lower=0)
        d["extra_spans"] = d.extra_spans.fillna("").astype(str).str.replace(r"\s+", "", regex=True)
        p = tmp / f"H{k}.csv"
        d.to_csv(p, index=False)
        paths.append(p)
    return paths


@unittest.skipUnless((DERIVED / "series10_manifest.parquet").exists(), "derived caches absent")
class TestGAN(unittest.TestCase):
    def test_validation_flags_problems(self):
        import tempfile
        from pathlib import Path
        import pandas as pd
        from cairn import gan
        with tempfile.TemporaryDirectory() as t:
            h1, _ = _fake_human_files(Path(t))
            v = gan.validate_file(h1)
            self.assertTrue(v["valid"], v["errors"][:3])
            d = pd.read_csv(h1, dtype={"source": str})
            d.loc[0, "annotator_id"] = "R2"
            d.loc[1, "type"] = "somewhere"
            d = d.drop(index=5)
            bad = Path(t) / "bad.csv"
            d.to_csv(bad, index=False)
            v = gan.validate_file(bad)
            self.assertFalse(v["valid"])
            msg = " ".join(v["errors"])
            for frag in ("one annotator", "missing", "type 'somewhere'"):
                self.assertIn(frag, msg)

    def test_end_to_end_agreement_table_freeze_and_design(self):
        import tempfile
        from pathlib import Path
        import pandas as pd
        from cairn import gan
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            h1, h2 = _fake_human_files(t)
            rep, w = gan.agreement(h1, h2)
            self.assertTrue(rep["gate"]["passed"])
            self.assertGreater(rep["kappa_type"], 0.99)
            ws = gan.adjudication_worksheet(w)
            self.assertEqual(len(ws), int(w.needs_adjudication.sum()))
            adj = t / "ADJ.csv"
            pd.read_csv(h1, dtype={"source": str}).assign(annotator_id="ADJ-TEST").to_csv(adj, index=False)
            log = t / "adjudication_log.md"
            log.write_text("# test adjudication log\n")
            comp = gan.freeze_human_set(h1, h2, adj, log, t / "freeze")
            self.assertTrue((t / "freeze" / "ANCHOR_FREEZE.json").exists())
            tab = pd.read_csv(t / "freeze" / "anchors_frozen.csv")
            self.assertGreater(comp["anchorable"], 90)
            inc = design.build("locked_primary", anchors_path=t / "freeze" / "anchors_frozen.csv", provisional=False)
            self.assertFalse(inc.anchor_provisional)
            self.assertEqual(inc.summary()["learners"], 39)
            self.assertGreaterEqual(comp["moments_locked"], 15)
            self.assertEqual(int(tab.anchorable.sum()), comp["anchorable"])

    def test_freeze_refuses_machine_raters_and_failed_gate(self):
        import tempfile
        from pathlib import Path
        import pandas as pd
        from cairn import gan
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            h1, h2 = _fake_human_files(t, jitter=(0.0, 40.0), seed=3)       # large disagreement: G-AN must fail
            adj = t / "ADJ.csv"
            pd.read_csv(h1, dtype={"source": str}).assign(annotator_id="ADJ-TEST").to_csv(adj, index=False)
            log = t / "log.md"
            log.write_text("x")
            with self.assertRaises(RuntimeError):
                gan.freeze_human_set(h1, h2, adj, log, t / "f")
            h1b, h2b = _fake_human_files(t, seed=1)
            pd.read_csv(h2b, dtype={"source": str}).assign(annotator_id="R2").to_csv(h2b, index=False)
            with self.assertRaises(ValueError):
                gan.freeze_human_set(h1b, h2b, adj, log, t / "g")


@unittest.skipUnless((DERIVED / "series10_manifest.parquet").exists(), "derived caches absent")
class TestFreezeTooling(unittest.TestCase):
    """cairn.freezing: refusals, a record the Stage-0 gate verifies, and that authorization stays a user act."""

    def _setup(self, t):
        import json
        from pathlib import Path
        import pandas as pd
        from cairn import gan
        from cairn.paths import sha256_file
        h1, h2 = _fake_human_files(t)
        adj = t / "ADJ.csv"
        pd.read_csv(h1, dtype={"source": str}).assign(annotator_id="ADJ-TEST").to_csv(adj, index=False)
        log = t / "adjudication_log.md"
        log.write_text("# test\n")
        comp = gan.freeze_human_set(h1, h2, adj, log, t / "anchors")
        cfg = t / "design_config.json"
        cfg.write_text(json.dumps(dict(decision_id="D-TEST", parametrization="PT", detrend_degree=2, statistic="LR",
                                       B_lock=999, R_lock=10)))
        rj = t / "rj_record.json"
        rj.write_text(json.dumps(dict(passed=True, anchor_table_sha256=comp["anchor_table_sha256"],
                                      design_config_sha256=sha256_file(cfg))))
        return Path(t / "anchors"), rj, cfg

    def test_record_verifies_through_the_stage0_gate(self):
        import json
        import tempfile
        from pathlib import Path
        from unittest import mock
        from cairn import freezing, gate
        with tempfile.TemporaryDirectory(dir=DERIVED) as t:
            t = Path(t)
            anchors, rj, cfg = self._setup(t)
            rec = freezing.build_record("development", anchors, rj, cfg)
            fd = t / "freeze_dir"
            path = freezing.write_record(rec, fd)
            with mock.patch.object(gate, "FREEZE_RECORD", path), mock.patch.object(gate, "AUTHORIZATION", fd / "AUTHORIZATION.json"):
                self.assertEqual(gate.verify_freeze()["decision_id"], "D-TEST")
                with self.assertRaises(gate.OutcomeAccessDenied):          # no authorization: still refused
                    gate.load_authorization("development")
                tmpl = freezing.authorization_template("development", "test", fd)
                self.assertFalse((fd / "AUTHORIZATION.json").exists())     # the template is printed, never written
                self.assertEqual(tmpl["freeze_record_sha256"], __import__("cairn.paths", fromlist=["x"]).sha256_file(path))
            rec2 = freezing.build_record("development", anchors, rj, cfg)
            freezing.write_record(rec2, fd)                                  # archives the previous record
            self.assertEqual(len(list(fd.glob("FREEZE_RECORD_development_*.json"))), 1)
            self.assertIn("src/cairn/gate.py", rec["bound_files"])

    def test_refusals(self):
        import json
        import tempfile
        from pathlib import Path
        from cairn import freezing
        with tempfile.TemporaryDirectory(dir=DERIVED) as t:
            t = Path(t)
            anchors, rj, cfg = self._setup(t)
            bad = json.loads(rj.read_text())
            bad["passed"] = False
            rj.write_text(json.dumps(bad))
            with self.assertRaises(freezing.FreezeRefused):
                freezing.build_record("development", anchors, rj, cfg)
            bad.update(passed=True, anchor_table_sha256="0" * 64)
            rj.write_text(json.dumps(bad))
            with self.assertRaises(freezing.FreezeRefused):
                freezing.build_record("development", anchors, rj, cfg)
            with self.assertRaises(freezing.FreezeRefused):                   # lock needs development selections
                freezing.build_record("lock", anchors, rj, cfg)
            (anchors / "anchors_frozen.csv").write_text("tampered")
            with self.assertRaises(freezing.FreezeRefused):
                freezing.verify_anchor_freeze(anchors)


class TestStage2Guards(unittest.TestCase):
    def test_dry_run_refuses_protected_locations(self):
        from cairn import gate, stage2
        from cairn.paths import ROOT
        for p in (gate.FREEZE_DIR / "x", ROOT / "results" / "dry"):
            with self.assertRaises(stage2.DryRunViolation):
                stage2._guard_dry_run(p)

    def test_gated_run_refuses_without_freeze(self):
        import subprocess
        import sys
        r = subprocess.run([sys.executable, "-m", "cairn", "run", "--scope", "development"], capture_output=True, text=True,
                           env={**__import__("os").environ, "PYTHONPATH": "src"})
        self.assertEqual(r.returncode, 2)
        self.assertIn("REFUSED", r.stderr)


@unittest.skipUnless((DERIVED / "series10_manifest.parquet").exists(), "derived caches absent")
class TestConsensus(unittest.TestCase):
    def test_consensus_rule_and_required_decisions(self):
        import tempfile
        from pathlib import Path
        import pandas as pd
        from cairn import gan
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            h1, h2 = _fake_human_files(t, jitter=(0.0, 12.0), seed=5)
            _, w = gan.agreement(h1, h2)
            disputed = w[w.needs_adjudication]
            self.assertGreater(len(disputed), 0)
            with self.assertRaises(ValueError):                       # disputed items need decisions
                gan.consensus(h1, h2, None, "ADJ-TEST")
            ws = gan.adjudication_worksheet(w)
            ws["decision_type"] = "diffuse"
            ws["decision_reason"] = "test: unresolved"
            dp = t / "decisions.csv"
            ws.to_csv(dp, index=False)
            c = gan.consensus(h1, h2, dp, "ADJ-TEST")
            out = t / "adj.csv"
            c.to_csv(out, index=False)
            self.assertTrue(gan.validate_file(out)["valid"])
            a, b = pd.read_csv(h1).set_index(["video", "item"]), pd.read_csv(h2).set_index(["video", "item"])
            agree = w[~w.needs_adjudication & (w.type_1 == "localized")].iloc[0]
            k = (agree["video"], int(agree["item"]))
            row = c.set_index(["video", "item"]).loc[k]
            self.assertAlmostEqual(row.span_start_s, (a.loc[k].span_start_s + b.loc[k].span_start_s) / 2)
            self.assertTrue((c.set_index(["video", "item"]).loc[list(zip(disputed.video, disputed.item))].type == "diffuse").all())

    def test_package_verifies(self):
        from cairn import gan
        self.assertTrue(gan.verify_package()["passed"])


@unittest.skipUnless((DERIVED / "series10_manifest.parquet").exists(), "derived caches absent")
class TestDryRuns(unittest.TestCase):
    """The Stage-2 and Stage-4 runners end to end on synthetic outcomes (tiny budgets): same code path as the gated
    runs, no gate call, outputs labelled synthetic."""

    def _cfg(self, t):
        import json
        p = t / "design_config.json"
        p.write_text(json.dumps(dict(decision_id="D-TEST", parametrization="P0", detrend_degree=2, statistic="LR",
                                     B_lock=999, R_lock=10)))
        return p

    def test_stage2_dry_run(self):
        import json
        import tempfile
        from pathlib import Path
        from cairn import gate, stage2
        from cairn.paths_stage1 import PROVISIONAL_ANCHORS
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            rep = stage2.run_development(t / "out", self._cfg(t), PROVISIONAL_ANCHORS, source="synthetic", B=5, R=1,
                                         kernels=False, log=lambda *_: None)
            self.assertTrue(rep["synthetic"])
            self.assertIn("go", rep["stop_rule"])
            sel = json.loads((t / "out" / "selections.json").read_text())
            self.assertTrue(sel["synthetic"])
            man = json.loads((t / "out" / "MANIFEST.json").read_text())
            self.assertTrue(man["outcome_access"].startswith("none: SYNTHETIC"))
        self.assertFalse(gate.ACCESS_LOG.exists())

    def test_lock_dry_run(self):
        import tempfile
        from pathlib import Path
        from cairn import gate, lock
        from cairn.paths_stage1 import PROVISIONAL_ANCHORS
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            rep = lock.run_lock(t / "out", self._cfg(t), PROVISIONAL_ANCHORS, source="synthetic", B=5, R=1,
                                log=lambda *_: None)
            self.assertIn("p_NH1", rep["H_pool"])
            for s in ("locked_primary", "locked_secondary"):
                ct = rep["closed_testing"][s]
                self.assertEqual(ct["claim"], bool(rep["H_pool"]["reject"] and ct["reject"]))
                self.assertIn("lambda_hat", ct)
        self.assertFalse(gate.ACCESS_LOG.exists())


@unittest.skipUnless((DERIVED / "series10_manifest.parquet").exists(), "derived caches absent")
class TestBundle(unittest.TestCase):
    def test_bundle_has_package_no_machine_proposals_and_is_reproducible(self):
        import tempfile
        import zipfile
        from pathlib import Path
        from cairn import gan
        with tempfile.TemporaryDirectory() as t:
            a = gan.bundle(Path(t) / "a.zip", "H1")
            b = gan.bundle(Path(t) / "b.zip", "H1")
            self.assertEqual(a["zip_sha256"], b["zip_sha256"])
            names = zipfile.ZipFile(Path(t) / "a.zip").namelist()
            self.assertEqual(sum(n.startswith("package/") for n in names), 22)
            self.assertFalse(any("R2" in n or "provisional" in n for n in names))
            with self.assertRaises(ValueError):
                gan.bundle(Path(t) / "c.zip", "LLM-1")
