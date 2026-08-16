import sys
import os
import numpy as np
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.ml_engine.regime_detector import RegimeDetector

def test_regime_detector_lookahead_leakage():
    """
    Verify that RegimeDetector initial volatility feature `returns.rolling(20, min_periods=1).std().fillna(0.0)`
    does NOT use full-sample `returns.std()` and has zero look-ahead leakage.
    """
    np.random.seed(42)
    n = 200
    prices = 100 + np.cumsum(np.random.randn(n) * 0.5)
    df_short = pd.DataFrame({'close': prices[:100]})
    df_full = pd.DataFrame({'close': prices})
    
    detector = RegimeDetector()
    
    # 1. Prepare observations for short dataset (100 rows)
    obs_short = detector._prepare_observations(df_short)
    
    # 2. Prepare observations for full dataset (200 rows) where future rows (100..199) have extreme volatility
    prices_extreme = prices.copy()
    prices_extreme[100:] += np.cumsum(np.random.randn(100) * 50.0) # huge extreme variance in future
    df_extreme = pd.DataFrame({'close': prices_extreme})
    obs_extreme = detector._prepare_observations(df_extreme)
    
    # Check that historical observations (0..99) are 100% IDENTICAL despite massive future volatility
    vol_short_hist = obs_short[:, 1]
    vol_extreme_hist = obs_extreme[:100, 1]
    
    diff = np.abs(vol_short_hist - vol_extreme_hist).max()
    print(f"[RegimeDetector Test] Max difference between short and extreme future dataset for first 100 rows: {diff}")
    
    assert diff < 1e-12, f"Look-ahead leakage detected! Historical vol changed when future data changed (diff={diff})"
    
    # 3. Check row 0 initial volatility value
    assert obs_short[0, 1] == 0.0, f"Row 0 volatility feature should be 0.0, got {obs_short[0, 1]}"
    
    # 4. Check that full-sample returns.std() is NOT used
    returns_full = pd.Series(prices).pct_change().fillna(0)
    full_sample_std = returns_full.std()
    rolling_vol_row0 = obs_short[0, 1]
    print(f"[RegimeDetector Test] Row 0 rolling vol: {rolling_vol_row0}, Full sample std: {full_sample_std}")
    assert rolling_vol_row0 != full_sample_std, "Initial volatility uses full-sample std!"
    
    print("[RegimeDetector Test] PASS: Zero look-ahead leakage confirmed.")
    return True

if __name__ == '__main__':
    test_regime_detector_lookahead_leakage()
