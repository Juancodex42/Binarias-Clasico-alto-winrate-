import sys
import os
import time
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from engine.ml_engine.feature_extractor import frac_diff_fixed

def frac_diff_loop(series: pd.Series, d: float = 0.4, threshold: float = 1e-5) -> pd.Series:
    """Original non-vectorized loop implementation of FFD."""
    vals = series.dropna().values
    n = len(vals)
    if n == 0:
        return pd.Series(dtype=float)
    
    weights = [1.0]
    k = 1
    while True:
        w = -weights[-1] * (d - k + 1) / k
        if abs(w) < threshold:
            break
        weights.append(w)
        k += 1
    
    w_arr = np.array(weights, dtype=float)
    if len(w_arr) > n:
        w_arr = w_arr[:n]
    width = len(w_arr)
    
    output = np.full(n, np.nan)
    w_rev = w_arr[::-1]
    
    for i in range(width - 1, n):
        output[i] = np.dot(w_rev, vals[i - width + 1 : i + 1])
        
    result = pd.Series(output, index=series.dropna().index)
    return result.reindex(series.index)

def run_test_2c():
    print("=== TEST 2C: BinaryFeatureExtractor.frac_diff_fixed (FFT vs Loop) ===")
    
    # 1. Generate synthetic price data (3,000 candles)
    np.random.seed(42)
    n_samples = 3000
    returns = np.random.normal(0, 0.001, n_samples)
    price_path = 100.0 * np.exp(np.cumsum(returns))
    series = pd.Series(price_path, index=pd.date_range("2026-01-01", periods=n_samples, freq="1min"))
    
    # 2. Test mathematical equivalence across d values (0.2, 0.4, 0.6)
    d_values = [0.2, 0.4, 0.6]
    max_deltas = []
    
    for d in d_values:
        res_fft = frac_diff_fixed(series, d=d)
        res_loop = frac_diff_loop(series, d=d)
        
        # Align valid (non-NaN) values
        valid_mask = ~res_fft.isna() & ~res_loop.isna()
        diff = np.abs(res_fft[valid_mask] - res_loop[valid_mask])
        max_diff = np.max(diff) if len(diff) > 0 else 0.0
        max_deltas.append(max_diff)
        
        print(f"d={d:.1f}: Max Delta between FFT and Loop = {max_diff:.3e}")
        assert max_diff < 1e-10, f"Mathematical equivalence failed for d={d}: max_diff = {max_diff}"

    overall_max_delta = max(max_deltas)
    print(f"\n[PASS] All max deltas are < 1e-10 (Overall Max Delta: {overall_max_delta:.3e})")

    # 3. Performance Benchmark (2 iterations of 3,000 samples)
    iterations = 2
    print(f"\nRunning benchmark: {iterations} iterations on N={n_samples} samples (d=0.4)...")
    
    t0 = time.perf_counter()
    for _ in range(iterations):
        _ = frac_diff_loop(series, d=0.4)
    t_loop = time.perf_counter() - t0
    
    t0 = time.perf_counter()
    for _ in range(iterations):
        _ = frac_diff_fixed(series, d=0.4)
    t_fft = time.perf_counter() - t0
    
    avg_loop_ms = (t_loop / iterations) * 1000.0
    avg_fft_ms = (t_fft / iterations) * 1000.0
    speedup = t_loop / t_fft if t_fft > 0 else float('inf')
    
    print(f"Loop implementation total time: {t_loop:.4f} seconds ({avg_loop_ms:.2f} ms/iter)")
    print(f"FFT implementation total time:  {t_fft:.4f} seconds ({avg_fft_ms:.2f} ms/iter)")
    print(f"Speedup Factor: {speedup:.2f}x")

    return {
        'max_delta': overall_max_delta,
        't_loop': t_loop,
        't_fft': t_fft,
        'speedup': speedup
    }

if __name__ == "__main__":
    run_test_2c()
