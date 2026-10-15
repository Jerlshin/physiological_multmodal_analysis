"""Unit tests for the outcome-free CAIRN Stage-0/1 infrastructure (src/cairn).

They need no BBBD data except where marked (skipped when the derived caches are absent) and
never read a quiz outcome.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd

from cairn import anchors, gate, pooling, stats
from cairn import timeline as tl
from cairn.channels import RefStats, reference_stats
from cairn.encoder import LinearMaskedEncoder, Standardizer, context
from cairn.paths import DERIVED, ITEM_BANK


class TestReferences(unittest.TestCase):
    def test_reference_refuses_target_learner(self):
        people = {"u1": "p1", "u2": "p2"}
        with self.assertRaises(ValueError):
            reference_stats(["u1", "u2"], people, n_s=10, exclude_person="p1")

    @unittest.skipUnless((DERIVED / "series10_manifest.parquet").exists(), "derived series absent")
    def test_reference_excludes_target_by_construction(self):
        m = pd.read_parquet(DERIVED / "series10_manifest.parquet")
        g = m[(m.canonical_video_id == "oCEKMEeZXug") & (m.status == "ok")].head(6)
        people = dict(zip(g.uid, g.qualified_participant_id))
        target = g.iloc[0]
        refs = [u for u in g.uid if people[u] != target.qualified_participant_id]
        r = reference_stats(refs, people, n_s=60, exclude_person=target.qualified_participant_id)
        self.assertIsInstance(r, RefStats)
        self.assertNotIn(target.qualified_participant_id, r.people)


class TestStandardizationAndContext(unittest.TestCase):
    def test_standardizer_fitted_on_training_only(self):
        rng = np.random.default_rng(0)
        train = [rng.normal(5, 2, (100, 3))]
        test = rng.normal(-50, 9, (100, 3))
        s = Standardizer().fit(train)
        mu, sd = s.mu.copy(), s.sd.copy()
        s.transform(test)
        np.testing.assert_array_equal(mu, s.mu)
        np.testing.assert_array_equal(sd, s.sd)
        np.testing.assert_allclose(mu, np.vstack(train).mean(0))

    def test_context_alignment(self):
        U = np.arange(10, dtype=float)[:, None]            # value = second index
        C = context(U, k=2)                                # columns: t-2, t-1, t+1, t+2
        np.testing.assert_array_equal(C[5], [3, 4, 6, 7])
        np.testing.assert_array_equal(C[0], [0, 0, 1, 2])  # zero-padded edge
        self.assertEqual(context(U, 2, drop_centre=False).shape[1], 5)


class TestPooling(unittest.TestCase):
    def test_kernels_sum_to_one_and_diffuse_is_zero(self):
        for kind in ("hard", "gauss"):
            k = pooling.kernel(100, 20, 30, kind)
            self.assertAlmostEqual(k.sum(), 1.0)
        E = np.random.default_rng(1).normal(size=(100, 2))
        an = pd.DataFrame(dict(rec_start_s=[20.0, 0.0], rec_end_s=[30.0, 100.0], localized=[True, False]))
        Z = pooling.anchored_moment_terms(E, an)
        np.testing.assert_allclose(Z[1], 0.0, atol=1e-12)
        np.testing.assert_allclose(Z[0], E[20:30].mean(0) - E.mean(0), atol=1e-12)

    def test_nan_aware_pooling(self):
        E = np.ones((50, 1))
        E[22:25] = np.nan
        z = pooling.pooled(E, pooling.kernel(50, 20, 30)[None, :])
        self.assertAlmostEqual(float(z[0, 0]), 1.0)


class TestTimeline(unittest.TestCase):
    def test_lagged_correlation_matches_numpy(self):
        rng = np.random.default_rng(2)
        b = rng.normal(size=500)
        a = b[100:200] + 0.1 * rng.normal(size=100)
        lags = np.arange(0, 400)
        r = tl._corr_all_lags(a, b, lags)
        self.assertEqual(int(np.nanargmax(r)), 100)
        self.assertAlmostEqual(r[37], np.corrcoef(a, b[37:137])[0, 1], places=10)

    def test_monotone_viterbi_recovers_planted_edit(self):
        W = 40
        states = [("A", o) for o in range(-5, 30)] + [("B", o) for o in range(-40, 0)]
        S = np.full((W, len(states)), 0.0)
        truth = []
        for w in range(W):
            st = ("A", 3) if w < 15 else (("A", 20) if w < 28 else ("B", -30))
            truth.append(states.index(st))
            S[w, states.index(st)] = 1.0
        S += np.random.default_rng(3).normal(0, 0.05, S.shape)
        path, _ = tl.monotone_viterbi(S, states, ["A", "B"], jump_cost=0.5, drift_bins=0)
        self.assertEqual(list(path), truth)

    def test_monotone_viterbi_forbids_backward_jumps(self):
        states = [("A", o) for o in range(0, 20)]
        S = np.zeros((10, len(states)))
        for w in range(10):
            S[w, states.index(("A", 15 if w < 5 else 2))] = 1.0       # a backward step is impossible
        path, _ = tl.monotone_viterbi(S, states, ["A"], jump_cost=0.2, drift_bins=0)
        offs = [states[k][1] for k in path]
        self.assertTrue(all(b >= a for a, b in zip(offs, offs[1:])))


class TestAnchors(unittest.TestCase):
    def test_item_bank_has_no_response_columns(self):
        b = anchors.item_bank()
        self.assertEqual(len(b), 131)
        for c in b.columns:
            self.assertNotIn(c.lower(), {"answer", "is_correct", "score", "correct", "response"})
        self.assertTrue((b.k_keyed >= 1).all())

    def test_span_metrics(self):
        a, b = anchors.Span("v", 10, 20), anchors.Span("v", 15, 25)
        self.assertAlmostEqual(anchors.iou(a, b), 5 / 15)
        self.assertAlmostEqual(anchors.centre_diff(a, b), 5.0)
        self.assertEqual(anchors.iou(a, anchors.Span("w", 10, 20)), 0.0)

    def test_freeze_refuses_machine_annotations(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            row = dict(video="Stars", item=1, source="VVAKFJ8VVp4", span_start_s=11.0, span_end_s=20.0, type="localized")
            pd.DataFrame([dict(row, annotator_id="R2-llm")]).to_csv(td / "h1.csv", index=False)
            pd.DataFrame([dict(row, annotator_id="H2")]).to_csv(td / "h2.csv", index=False)
            for f in ("adj.csv", "log.md"):
                (td / f).write_text("x")
            with self.assertRaises(ValueError):
                anchors.freeze(td / "h1.csv", td / "h2.csv", td / "adj.csv", td / "log.md", td / "out.json")

    def test_freeze_requires_all_files(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(FileNotFoundError):
                anchors.freeze(Path(td) / "a", Path(td) / "b", Path(td) / "c", Path(td) / "d", Path(td) / "o")


class TestGate(unittest.TestCase):
    def test_gate_refuses_before_opening_outcomes(self):
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(gate, "FREEZE_DIR", Path(td)), \
                mock.patch.object(gate, "FREEZE_RECORD", Path(td) / "FREEZE_RECORD.json"), \
                mock.patch.object(gate, "AUTHORIZATION", Path(td) / "AUTHORIZATION.json"), \
                mock.patch("pandas.read_parquet", side_effect=AssertionError("outcome file opened")):
            for scope in gate.SCOPES:
                with self.assertRaises(gate.OutcomeAccessDenied):
                    gate.load_item_outcomes(scope, "test")

    def test_gate_refuses_unbound_or_unscoped_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            rec = dict(bound_files={}, anchor_freeze_sha256="x")
            (td / "FREEZE_RECORD.json").write_text(json.dumps(rec))
            (td / "AUTHORIZATION.json").write_text(json.dumps(dict(freeze_record_sha256="wrong", scopes=["development"])))
            with mock.patch.object(gate, "FREEZE_DIR", td), mock.patch.object(gate, "FREEZE_RECORD", td / "FREEZE_RECORD.json"), \
                    mock.patch.object(gate, "AUTHORIZATION", td / "AUTHORIZATION.json"), \
                    mock.patch("pandas.read_parquet", side_effect=AssertionError("outcome file opened")):
                with self.assertRaises(gate.OutcomeAccessDenied):
                    gate.load_item_outcomes("development", "test")
                from cairn.paths import sha256_file
                (td / "AUTHORIZATION.json").write_text(json.dumps(dict(freeze_record_sha256=sha256_file(td / "FREEZE_RECORD.json"), scopes=["development"])))
                with self.assertRaises(gate.OutcomeAccessDenied):
                    gate.load_item_outcomes("locked_primary", "test")

    def test_no_cairn_authorization_exists_at_stage0(self):
        self.assertFalse(gate.AUTHORIZATION.exists())
        self.assertFalse(gate.FREEZE_RECORD.exists())


class TestStatsAndEncoder(unittest.TestCase):
    def test_group_kfold_disjoint_and_deterministic(self):
        g = np.repeat(np.arange(20), 3)
        f1 = list(stats.group_kfold(g, 5, 7))
        f2 = list(stats.group_kfold(g, 5, 7))
        for (tr, te), (tr2, te2) in zip(f1, f2):
            self.assertFalse(set(g[tr]) & set(g[te]))
            np.testing.assert_array_equal(te, te2)

    def test_two_way_recovers_components(self):
        rng = np.random.default_rng(4)
        a, b = rng.normal(0, 2, 30), rng.normal(0, 1, 50)
        M = a[:, None] + b[None, :] + rng.normal(0, 0.1, (30, 50))
        M[rng.random(M.shape) < 0.1] = np.nan
        v = stats.variance_shares(M)
        self.assertGreater(v["person"], 0.7)
        self.assertLess(v["residual"], 0.02)

    def test_auc(self):
        self.assertAlmostEqual(stats.auc(np.array([0, 0, 1, 1]), np.array([0.1, 0.2, 0.8, 0.9])), 1.0)
        self.assertAlmostEqual(stats.auc(np.array([0, 1]), np.array([0.5, 0.5])), 0.5)

    def test_encoder_deterministic_and_isolated(self):
        rng = np.random.default_rng(5)
        train = [rng.normal(size=(120, 4)) for _ in range(5)]
        test = rng.normal(3, 5, size=(120, 4))
        e1 = LinearMaskedEncoder(K=2).fit(train)
        e2 = LinearMaskedEncoder(K=2).fit(train)
        np.testing.assert_array_equal(e1.B, e2.B)
        B = e1.B.copy()
        out = e1.transform(test)
        self.assertEqual(out.shape, (120, 2))
        np.testing.assert_array_equal(B, e1.B)


class TestItemBankHash(unittest.TestCase):
    def test_item_bank_present(self):
        self.assertTrue(ITEM_BANK.exists())


if __name__ == "__main__":
    unittest.main()
