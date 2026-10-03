"""Numerical controls for transfer-response identification, not source truth."""
import unittest
import numpy as np
from scipy import signal
from bbbd_audit.gate_closure import spectral_candidates


class TransferControls(unittest.TestCase):
    def test_known_causal_filter_and_nonunit_gain(self):
        x=np.random.default_rng(410).normal(size=32768)
        sos=np.vstack([signal.butter(5,.5,'high',fs=128,output='sos'),
                       signal.butter(5,25,'low',fs=128,output='sos')])
        y=2*signal.sosfilt(sos,x)
        result=spectral_candidates(x,y,'ecg')
        self.assertEqual(result[0]['candidate'],'hp0.5_order5_designfs128_causal')
        self.assertEqual(result[0]['grid_lag_samples'],0)
        self.assertAlmostEqual(result[0]['gain'],2,places=2)

    def test_identity_negative_control(self):
        x=np.random.default_rng(411).normal(size=32768)
        result=spectral_candidates(x,x,'ecg')
        self.assertEqual(result[0]['candidate'],'identity')
        self.assertLess(result[0]['relative_complex_transfer_error'],1e-10)

    def test_nonfinite_source_never_identifies_filter(self):
        x=np.full(32768,np.nan)
        y=np.random.default_rng(412).normal(size=32768)
        self.assertEqual(spectral_candidates(x,y,'ecg'),[])


if __name__=='__main__':
    unittest.main()
