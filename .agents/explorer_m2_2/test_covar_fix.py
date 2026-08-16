import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from engine.ml_engine.regime_detector import RegimeDetector

print("--- TESTING DEGENERATE COVARIANCE & FIX ---", flush=True)

# Degenerate case 1: Flat OHLCV DataFrame (constant values -> 0 variance)
dates = pd.date_range('2024-01-01', periods=120, freq='1min')
df_flat = pd.DataFrame({
    'open': [100.0] * 120,
    'high': [100.0] * 120,
    'low': [100.0] * 120,
    'close': [100.0] * 120,
    'volume': [100.0] * 120,
    'open_time': (dates.astype('int64') // 10**6).values
}, index=dates)

rd = RegimeDetector(n_states=3)
try:
    rd.fit(df_flat)
    print("Flat df fit success! is_fitted:", rd.is_fitted)
    covs = rd.model.covars_
    print("Covars:\n", covs)
    st = rd.get_current_state(df_flat)
    print("State:", st)
    probs = rd.get_filtered_state_probabilities(df_flat)
    print("Has NaNs in probs?", np.isnan(probs).any())
except Exception as e:
    print("Flat df FAILED with exception:", type(e), e)

# Degenerate case 2: Near-zero variance with small noise
df_noise = df_flat.copy()
df_noise['close'] = 100.0 + np.random.normal(0, 1e-8, 120)
rd2 = RegimeDetector(n_states=3)
try:
    rd2.fit(df_noise)
    print("Noise df fit success! is_fitted:", rd2.is_fitted)
    covs2 = rd2.model.covars_
    print("Covars 2:\n", covs2)
    st2 = rd2.get_current_state(df_noise)
    print("State 2:", st2)
    probs2 = rd2.get_filtered_state_probabilities(df_noise)
    print("Has NaNs in probs 2?", np.isnan(probs2).any())
except Exception as e:
    print("Noise df FAILED with exception:", type(e), e)

print("--- FINISHED TEST ---", flush=True)
