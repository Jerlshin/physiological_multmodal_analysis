"""G01-R feature formulas, synchrony and reference-access rules on synthetic signals (protocol §6, §17.1).

Covers the valid-sample rules, the 16 Hz exclusion, leave-self-out references and the CorrCA fit scope.
"""
import unittest

import numpy as np
import pandas as pd
from scipy.signal import welch

from g01r import references as R
from g01r.config import load_config
from g01r.features import reference_free as rf
from g01r.features.extract import apply_missing_rule
from g01r.features.raw_route import raw_route_eeg
from g01r.features.synchrony import CorrCAStats, _pad, masked_pearson, reference_correlations
from g01r.population import AnalysisSet
from g01r.signals import zero_digital_codes

FS = 128
CFG = load_config()


def toy_set(n_e3=8, n_e4=10):
    rows = []
    for i in range(n_e3):
        for v in ["a", "b", "rel"]:
            rows.append(dict(experiment=3, participant_id=f"s{i}", qualified_participant_id=f"exp-3:s{i}", session=1,
                             local_stimulus_id=0, canonical_video_id=v, condition="x", exposure_number=1))
    for i in range(n_e4):
        for v in ["c", "rel"]:
            rows.append(dict(experiment=4, participant_id=f"s{i}", qualified_participant_id=f"exp-4:s{i}", session=2,
                             local_stimulus_id=0, canonical_video_id=v, condition="x", exposure_number=1))
    return AnalysisSet("toy", pd.DataFrame(rows))


class EEGFeatures(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(0)
        self.T = FS * 120
        t = np.arange(self.T) / FS
        self.labels = CFG.eeg["alpha_channels"] + CFG.eeg["theta_channels"]
        self.x = rng.normal(size=(self.T, len(self.labels)))
        self.x[:, :9] += 3 * np.sin(2 * np.pi * 10 * t)[:, None]       # posterior alpha
        self.invalid = np.zeros_like(self.x, bool)
        self.t = t

    def test_masked_welch_equals_scipy_on_valid_data(self):
        f, p, cov = rf.masked_welch(self.x[:, :3], self.invalid[:, :3], FS, 4.0, 0.5)
        f2, p2 = welch(self.x[:, :3], fs=FS, window="hann", nperseg=512, noverlap=256, axis=0)
        self.assertTrue(np.allclose(f, f2))
        self.assertTrue(np.allclose(p, p2))
        self.assertTrue((cov == self.T).all())

    def test_windows_with_zeroed_samples_are_excluded(self):
        x = self.x.copy()
        inv = self.invalid.copy()
        x[1000:1100, 0] = 0.0
        inv[1000:1100, 0] = True
        x2 = x.copy()
        x2[1000:1100, 0] = 1e6        # whatever the zeroed span contains must not matter
        _, p1, c1 = rf.masked_welch(x[:, :1], inv[:, :1], FS, 4.0, 0.5)
        _, p2, _ = rf.masked_welch(x2[:, :1], inv[:, :1], FS, 4.0, 0.5)
        self.assertTrue(np.allclose(p1, p2))
        self.assertLess(c1[0], self.T)

    def test_relative_alpha_and_16hz_exclusion(self):
        a, dur = rf.eeg_relative_band(self.x, self.invalid, self.labels, CFG.eeg["alpha_channels"], CFG.eeg["alpha_band_hz"],
                                      CFG.eeg, FS, CFG.min_valid_samples)
        self.assertGreater(a, np.log10(0.2))       # dominant 10 Hz rhythm
        self.assertAlmostEqual(dur, 120.0)
        x16 = self.x + 5 * np.sin(2 * np.pi * 16 * self.t)[:, None]
        a16, _ = rf.eeg_relative_band(x16, self.invalid, self.labels, CFG.eeg["alpha_channels"], CFG.eeg["alpha_band_hz"],
                                      CFG.eeg, FS, CFG.min_valid_samples)
        self.assertLess(abs(a16 - a), 1e-3)         # 16 Hz contamination does not enter the ratio

    def test_feature_missing_when_valid_data_below_60s(self):
        inv = np.ones_like(self.invalid)
        inv[: FS * 50] = False
        a, dur = rf.eeg_relative_band(self.x, inv, self.labels, CFG.eeg["alpha_channels"], CFG.eeg["alpha_band_hz"],
                                      CFG.eeg, FS, CFG.min_valid_samples)
        self.assertTrue(np.isnan(a))

    def test_zero_code_detection_for_symmetric_16bit_ranges(self):
        lo, hi = zero_digital_codes(np.array([-45.7301]), np.array([45.7301]), np.array([-32768.0]), np.array([32767.0]))
        self.assertEqual((lo[0], hi[0]), (-1.0, 0.0))

    def test_raw_route_removes_eog_and_masks_artifacts_with_extension(self):
        rng = np.random.default_rng(1)
        T = FS * 90
        eog = np.cumsum(rng.normal(size=(T, 2)), axis=0) * 5 + 15000
        x = rng.normal(size=(T, 8)) + (eog - eog.mean(0)) @ rng.normal(size=(2, 8)) * 0.3
        x[5000, 3] += 500.0
        y, bad, regressed = raw_route_eeg(x, eog, FS, CFG.raw_route)
        self.assertTrue(regressed)
        # The mask is exactly the 4 x IQR exceedance set dilated by +/- 40 ms (5 samples at 128 Hz).
        med = np.median(y, axis=0)
        q75, q25 = np.percentile(y, [75, 25], axis=0)
        raw = np.abs(y - med) > 4 * (q75 - q25)
        dil = np.zeros_like(raw)
        for c in range(raw.shape[1]):
            for i in np.flatnonzero(raw[:, c]):
                dil[max(0, i - 5):i + 6, c] = True
        self.assertTrue(np.array_equal(bad, dil))
        self.assertTrue(bad[4995:5006, 3].all())


class ECGAndEyeFeatures(unittest.TestCase):
    def test_heart_rate_and_rmssd(self):
        rr = np.tile([0.79, 0.81], 100)
        peaks = np.cumsum(np.r_[0.1, rr])
        hr, dur = rf.heart_rate(peaks, peaks[-1] + 0.1)
        self.assertAlmostEqual(hr, np.median(60 / rr))
        self.assertAlmostEqual(rf.ln_rmssd(peaks, peaks[-1] + 0.1)[0], np.log(20.0), places=6)

    def test_rr_validity_and_successive_difference_rule(self):
        rr = np.r_[np.tile([0.79, 0.81], 25), 2.5, np.tile([0.79, 0.81], 25), 1.2, np.tile([0.79, 0.81], 25)]
        peaks = np.cumsum(np.r_[0.0, rr])
        hr, dur = rf.heart_rate(peaks, peaks[-1])
        r = np.diff(peaks)
        valid = (r >= 0.3) & (r <= 2.0)
        self.assertAlmostEqual(dur, r[valid].sum())
        d = np.diff(r)
        pair = valid[:-1] & valid[1:] & (np.abs(d) < 0.2 * r[:-1])
        self.assertEqual(int((~pair).sum()), 4)          # 2 pairs touch the 2.5 s RR, 2 pairs touch the 1.2 s jump
        lr, _ = rf.ln_rmssd(peaks, peaks[-1])
        self.assertAlmostEqual(lr, np.log(np.sqrt(np.mean((d[pair] * 1000) ** 2))), places=10)

    def test_peaks_outside_video_ignored(self):
        peaks = np.r_[-1.0, np.arange(0, 100, 1.0), 150.0]
        hr, dur = rf.heart_rate(peaks, 100.0)
        self.assertAlmostEqual(hr, 60.0)
        self.assertAlmostEqual(dur, 99.0)

    def test_hr_series_interpolates_within_beats_only(self):
        peaks = np.arange(10.0, 90.0, 1.0)
        s = rf.hr_series(peaks, 100.0, 2.0)
        grid = np.arange(0, 100, 0.5)
        self.assertTrue(np.isnan(s[grid < 11.0]).all())
        self.assertTrue(np.allclose(s[(grid >= 11.0) & (grid <= 89.0)], 60.0))
        self.assertTrue(np.isnan(s[grid > 89.0]).all())

    def test_gaze_valid_sample_rules(self):
        xy = np.array([[0.0, 0.0], [1919.9, 1079.9], [1920.0, 10.0], [10.0, 1080.0], [np.nan, 1.0], [-0.1, 5.0], [5.0, 5.0]])
        corrected = np.array([False, False, False, False, False, False, True])
        v = rf.gaze_valid_mask(xy, corrected, 1920, 1080)
        self.assertEqual(v.tolist(), [True, True, False, False, False, False, False])

    def test_pupil_valid_requires_positive_value_and_gaze_on_screen(self):
        p = np.array([300.0, 0.0, np.nan, 310.0, 320.0])
        corrected = np.array([False, False, False, True, False])
        screen = np.array([True, True, True, True, False])
        self.assertEqual(rf.pupil_valid_mask(p, corrected, screen).tolist(), [True, False, False, False, False])

    def test_saccade_rate_excludes_onsets_in_correction_intervals(self):
        intervals = np.array([[10.0, 20.0]])
        onsets = np.array([1.0, 12.0, 19.99, 20.0, 30.0, 200.0])
        rate, _ = rf.saccade_rate(onsets, intervals, valid_gaze_samples=60 * FS, end_s=100.0, fs=FS)
        self.assertAlmostEqual(rate, 3.0)              # 1.0, 20.0, 30.0 per one valid minute

    def test_dispersion_normalized_by_diagonal(self):
        xy = np.column_stack([np.r_[np.zeros(50), np.full(50, 100.0)], np.zeros(100)])
        d, _ = rf.gaze_dispersion(xy, np.ones(100, bool), 2203.0, FS)
        self.assertAlmostEqual(d, 50.0 / 2203.0)

    def test_missing_rule(self):
        f = pd.DataFrame(dict(RF1_eeg_posterior_alpha=[0.1, 0.2], RF1_valid_s=[59.9, 60.0]))
        g = apply_missing_rule(f, CFG)
        self.assertTrue(np.isnan(g.RF1_eeg_posterior_alpha[0]))
        self.assertEqual(g.RF1_eeg_posterior_alpha[1], 0.2)


class Synchrony(unittest.TestCase):
    def test_reference_correlation_leaves_self_out(self):
        rng = np.random.default_rng(2)
        shared = rng.normal(size=2000)
        Y = np.stack([shared + rng.normal(size=2000) for _ in range(6)])[:, None, :]
        refs = {i: np.array([j for j in range(5) if j != i]) for i in range(6)}     # 5 is a test person
        r, n = reference_correlations(Y, np.arange(6), refs, 10)
        for i in range(6):
            manual = np.corrcoef(Y[i, 0], Y[refs[i], 0].mean(axis=0))[0, 1]
            self.assertAlmostEqual(r[i][0], manual, places=10)
        Y2 = Y.copy()
        Y2[0] += 100 * rng.normal(size=(1, 2000))      # changing person 0 cannot change person 0's reference
        r2, _ = reference_correlations(Y2, np.arange(6), {0: refs[0]}, 10)
        ref_mean = Y[refs[0], 0].mean(axis=0)
        self.assertAlmostEqual(r2[0][0], np.corrcoef(Y2[0, 0], ref_mean)[0, 1], places=10)

    def test_reference_mean_uses_valid_people_and_pairwise_complete_samples(self):
        rng = np.random.default_rng(3)
        Y = rng.normal(size=(4, 1, 500))
        Y[1, 0, :100] = np.nan
        Y[0, 0, 400:] = np.nan
        r, n = reference_correlations(Y, np.arange(4), {0: np.array([1, 2, 3])}, 10)
        ref = np.nanmean(Y[1:, 0], axis=0)
        m = np.isfinite(Y[0, 0])
        self.assertAlmostEqual(r[0][0], np.corrcoef(Y[0, 0, m], ref[m])[0, 1], places=10)
        self.assertEqual(n[0], 400)

    def test_min_valid_rule(self):
        Y = np.random.default_rng(4).normal(size=(3, 1, 50))
        r, _ = reference_correlations(Y, np.arange(3), {0: np.array([1, 2])}, 60)
        self.assertTrue(np.isnan(r[0][0]))

    def test_masked_pearson(self):
        a = np.arange(10.0)[:, None]
        b = (2 * np.arange(10.0) + 1)[:, None]
        r, n = masked_pearson(a, b, np.ones((10, 1), bool))
        self.assertAlmostEqual(r[0], 1.0)

    def test_corrca_recovers_shared_component_and_respects_fit_scope(self):
        rng = np.random.default_rng(5)
        aset = toy_set()
        D, T = 8, 3000
        mixing = rng.normal(size=D)
        sources = {v: rng.normal(size=T) for v in aset.cells.canonical_video_id.unique()}
        data = {}
        for i, r in enumerate(aset.cells.itertuples(index=False)):
            x = 0.7 * sources[r.canonical_video_id][:, None] * mixing[None, :] + rng.normal(size=(T, D))
            data[f"u{i}"] = (x - x.mean(0)).astype(np.float32)

        class Store:
            route = "test"

            def eeg(self, uid):
                return data[uid], np.ones(T, bool)

        uids = [f"u{i}" for i in range(aset.n)]
        import g01r.config as gc
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            old = gc.DERIVED
            gc.DERIVED = Path(d)
            try:
                stats = CorrCAStats(Store(), aset, uids, np.ones(aset.n, bool))
                fit = aset.person % 2 == 0
                W, ev = stats.fit(fit, 3, 0.5)
                w = W[:, 0] / np.linalg.norm(W[:, 0])
                target = np.linalg.solve(np.cov(np.vstack(list(data.values())).T), mixing)
                self.assertGreater(abs(w @ target / np.linalg.norm(target)), 0.95)
                # Perturbing a non-fitting person's EEG leaves the filters unchanged (fit scope).
                victim = int(np.flatnonzero(~fit)[0])
                data[uids[victim]] = (data[uids[victim]] * 0 + rng.normal(size=(T, D))).astype(np.float32)
                stats2 = CorrCAStats(Store(), AnalysisSet("toy2", aset.cells.drop(columns=["person", "video", "ev", "ev_key"])),
                                     uids, np.ones(aset.n, bool))
                W2, _ = stats2.fit(fit, 3, 0.5)
                self.assertTrue(np.allclose(np.abs(W), np.abs(W2)))
            finally:
                gc.DERIVED = old


class ReferencePlans(unittest.TestCase):
    def setUp(self):
        self.aset = toy_set()
        self.test = np.isin(self.aset.person, [0, 1, 9])
        self.train = ~self.test

    def test_regime_A(self):
        a = self.aset
        plan = R.regime_A(a, self.train, np.ones(a.n, bool))
        self.assertTrue(np.array_equal(plan.corrca_fit, self.train))
        for c, refs in plan.refs.items():
            self.assertTrue(self.train[refs].all())                      # references are training people only
            self.assertNotIn(a.person[c], a.person[refs])                # never one's own person
            self.assertTrue((a.ev[refs] == a.ev[c]).all())               # same experiment x video
            if self.test[c]:
                expected = np.flatnonzero(self.train & (a.ev == a.ev[c]))
                self.assertTrue(np.array_equal(np.sort(refs), expected))

    def test_regime_C(self):
        a = self.aset
        v = a.video[np.flatnonzero(a.cells.canonical_video_id == "rel")[0]]
        fold = (a.person % 3 == 0)
        test = (a.video == v) & fold
        train = (a.video != v) & ~fold
        half = R.half_split(a, np.random.default_rng(0))
        plan = R.regime_C(a, train, test, half)
        for c, refs in plan.refs.items():
            self.assertNotIn(a.person[c], a.person[refs])
            self.assertTrue((half[a.person[refs]] != half[a.person[c]]).all())
            if test[c]:
                self.assertTrue((a.ev[refs] == a.ev[c]).all())
            else:
                self.assertTrue(train[refs].all())                       # training refs never use test people
        self.assertFalse((plan.corrca_fit & (a.video == v)).any())       # filters never see the held-out video
        with self.assertRaises(AssertionError):
            R.regime_C(a, np.ones(a.n, bool) & ~test, test, half)

    def test_transport(self):
        a = self.aset
        src = a.experiment == 3
        with self.assertRaises(AssertionError):
            R.transport(a, src | (a.person == a.person[~src][0]), ~src)
        e4_rel = (a.experiment == 4) & (a.cells.canonical_video_id == "rel").to_numpy()
        plan = R.transport(a, src, e4_rel)
        for c in np.flatnonzero(e4_rel):
            self.assertTrue(src[plan.refs[c]].all())
        self.assertTrue(np.array_equal(plan.corrca_fit, src))


if __name__ == "__main__":
    unittest.main()
