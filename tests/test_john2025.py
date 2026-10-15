"""Tests of the John 2025 replication package (outcome-free; the posttest is never read here)."""
import importlib.util
import unittest
from unittest import mock

import numpy as np
import pandas as pd

from g01r.features.synchrony import reference_correlations
from g01r.population import AnalysisSet
from g01r.references import regime_A
from john2025 import features, freeze, outcomes, population
from john2025.paths import WORKBOOK
from john2025.provider import reference_correlations_chunked

HAS_XLSX = importlib.util.find_spec("openpyxl") is not None and WORKBOOK.exists()


def _aset(n):
    cells = pd.DataFrame(dict(experiment=0, participant_id=[f"P{i:03d}" for i in range(n)],
                              qualified_participant_id=[f"J:P{i:03d}" for i in range(n)], session=1,
                              local_stimulus_id="mine", canonical_video_id="mine"))
    return AnalysisSet("TEST", cells)


class TestChunkedISC(unittest.TestCase):
    def test_bit_identical_to_frozen_function(self):
        rng = np.random.default_rng(3)
        n, k, T = 23, 2, 3000
        common = rng.normal(size=(1, k, T))
        Y = 0.7 * common + rng.normal(size=(n, k, T))
        Y[rng.random(Y.shape) < 0.1] = np.nan
        Y[4, :, :2500] = np.nan                   # a person below the 60 s rule at min_valid = 600
        V = np.isfinite(Y)
        Yz = np.where(V, Y, 0.0)
        aset = _aset(n)
        for frac in (0.5, 0.9, 1.0):
            train = rng.random(n) < frac
            train[:2] = True
            plan = regime_A(aset, train, np.ones(n, bool))
            refs = {int(c): np.asarray(r, int) for c, r in plan.refs.items()}
            r1, n1 = reference_correlations(Y, np.arange(n), refs, 600)
            r2, n2 = reference_correlations_chunked(Y, V, Yz, refs, 600, chunk=5)
            for i in r1:
                np.testing.assert_array_equal(r1[i], r2[i])
                self.assertEqual(n1[i], n2[i])
            self.assertTrue(np.isnan(r2[4]).all())


class TestFeatureHelpers(unittest.TestCase):
    def test_blink_mask_buffer(self):
        t = np.arange(0, 1000, 2.0)
        m = features.blink_mask(t, np.array([[400.0, 500.0]]), 100.0)
        self.assertTrue(m[(t >= 300) & (t <= 600)].all())
        self.assertFalse(m[(t < 300) | (t > 600)].any())

    def test_nearest_sample(self):
        t = np.arange(0, 100, 2.0)
        idx = features.nearest_sample(t, np.array([0.0, 3.0, 4.9, 98.0, 150.0]), 1.0)
        self.assertEqual(idx.tolist(), [0, 1, 2, 49, -1])

    def test_bin_average(self):
        v = np.array([1.0, 3.0, 5.0, 7.0])
        valid = np.array([True, True, False, True])
        bins = np.array([0, 0, 1, 2])
        out = features.bin_average(v, valid, bins, 4)
        np.testing.assert_array_equal(out, [2.0, np.nan, 7.0, np.nan])


class TestOutcomeIsolation(unittest.TestCase):
    def test_covariate_reader_never_requests_posttest(self):
        self.assertFalse(any(c.startswith("knowPost") for c in population.COVARIATE_SOURCE))

    @unittest.skipUnless(HAS_XLSX, "workbook or openpyxl unavailable")
    def test_covariate_table_has_no_posttest(self):
        q = population.quest_covariates()
        self.assertFalse(any(c.startswith("knowPost") for c in q.columns))
        self.assertTrue((q.pretest_sum == q.knowPre_sum).all())

    def test_outcome_gate_refuses_without_verified_freeze(self):
        with mock.patch.object(freeze, "verify", return_value=["no feature-freeze record"]), \
                mock.patch.object(pd, "read_excel", side_effect=AssertionError("posttest must not be read")):
            with self.assertRaises(outcomes.OutcomeAccessDenied):
                outcomes.load_posttest(["A010223"], purpose="test")


class TestPlanTimestamp(unittest.TestCase):
    def test_plan_identical_to_time_stamping_commit(self):
        try:
            ident = freeze.plan_identity()
        except Exception as exc:          # no git in the environment
            self.skipTest(str(exc))
        self.assertTrue(ident["identical_to_commit"])


if __name__ == "__main__":
    unittest.main()
