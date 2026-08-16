import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import numpy as np
import pandas as pd
from tests.conftest import generate_synthetic_ohlcv
from engine.ml_engine.regime_detector import RegimeDetector

print("--- HMM DEEP DIVE TEST ---", flush=True)

df = generate_synthetic_ohlcv(n_rows=500, seed=42)
rd = RegimeDetector(n_states=3)
rd.fit(df)

obs = rd._prepare_observations(df)

# Check Viterbi vs Forward Proba
viterbi_states = rd.model.predict(obs)
forward_probs = rd.predict_forward_proba(obs)
forward_states = rd.predict_forward(obs)

diff_count = np.sum(viterbi_states != forward_states)
print(f"Viterbi vs Forward-only state differences: {diff_count} / {len(obs)} bars differ", flush=True)

# Print first 10 bars comparison
for t in range(10):
    print(f"Bar {t}: Viterbi={viterbi_states[t]} | Forward={forward_states[t]} | Probs={np.round(forward_probs[t], 4)}", flush=True)

# Test zero-variance column in obs
obs_zero_var = obs.copy()
obs_zero_var[:, 0] = 0.0  # zero returns everywhere

from hmmlearn.hmm import GaussianHMM
hmm_zv = GaussianHMM(n_components=3, covariance_type='diag', min_covar=1e-3, n_iter=100, random_state=42)
try:
    hmm_zv.fit(obs_zero_var)
    print("Zero variance fit success! covars:\n", hmm_zv.covars_, flush=True)
except Exception as e:
    print("Zero variance fit FAILED:", type(e), e, flush=True)

# Test min_covar effect with 1e-6 vs 1e-3
hmm_regularized = GaussianHMM(n_components=3, covariance_type='diag', min_covar=1e-6, n_iter=100, random_state=42)
try:
    hmm_regularized.fit(obs)
    print("Min covar 1e-6 fit success! covars:\n", hmm_regularized.covars_, flush=True)
except Exception as e:
    print("Min covar 1e-6 fit FAILED:", type(e), e, flush=True)

print("--- FINISHED DEEP DIVE ---", flush=True)
