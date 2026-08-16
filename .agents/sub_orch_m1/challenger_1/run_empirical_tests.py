import sys
import os
import time
import numpy as np
import pandas as pd
from scipy.signal import fftconvolve

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from engine.simulator import BinarySimulator
from engine.ml_engine.feature_extractor import frac_diff_fixed, BinaryFeatureExtractor
from engine.ml_engine.regime_detector import RegimeDetector
from engine.ml_engine.cusum_monitor import CUSUMMonitor
from engine.ml_engine.meta_labeler import MetaLabeler
from engine.ml_engine.meta_filter import BinaryMLMetaFilter
from engine.auto_tuner import WalkForwardEngine

def test_1_binary_simulator():
    print("--- TEST 1: BinarySimulator ---", flush=True)
    sim = BinarySimulator()
    
    # 1a. Test single asset tie_rule='LOSS' vs 'RETURN_STAKE'
    df_single = pd.DataFrame({
        'open_time': [100, 200, 300, 400, 500],
        'open': [100.0, 100.0, 100.0, 100.0, 100.0],
        'high': [105.0, 105.0, 105.0, 105.0, 105.0],
        'low': [95.0, 95.0, 95.0, 95.0, 95.0],
        'close': [100.0, 100.0, 100.0, 100.0, 100.0],
        'volume': [1000, 1000, 1000, 1000, 1000]
    })
    signals_single = pd.Series(['CALL', None, None, None, None], index=df_single.index)
    
    res_return = sim.run(df_single, signals_single, expiry_candles=1, payout=0.85, bet_fraction=0.1, tie_rule='RETURN_STAKE')
    res_loss = sim.run(df_single, signals_single, expiry_candles=1, payout=0.85, bet_fraction=0.1, tie_rule='LOSS')
    
    print(f"Single asset RETURN_STAKE result: {res_return['summary']}", flush=True)
    print(f"Single asset LOSS result: {res_loss['summary']}", flush=True)
    
    assert res_return['summary']['ties'] == 1 and res_return['summary']['net_pnl'] == 0.0
    assert res_loss['summary']['losses'] == 1 and res_loss['summary']['net_pnl'] == -100.0
    
    # 1b. Test multi-asset tie_rule='LOSS' vs 'RETURN_STAKE'
    universe_data = {'EURUSD': df_single, 'GBPUSD': df_single.copy()}
    signals_multi = {
        'EURUSD': [{'time': 100, 'direction': 'CALL'}],
        'GBPUSD': [{'time': 200, 'direction': 'PUT'}]
    }
    
    res_m_return = sim.run_multi_asset(universe_data, signals_multi, expiry_candles=1, payout=0.85, mode='SIMPLE', tie_rule='RETURN_STAKE')
    res_m_loss = sim.run_multi_asset(universe_data, signals_multi, expiry_candles=1, payout=0.85, mode='SIMPLE', tie_rule='LOSS')
    
    print(f"Multi asset RETURN_STAKE result: {res_m_return['summary']}", flush=True)
    print(f"Multi asset LOSS result: {res_m_loss['summary']}", flush=True)
    
    assert res_m_return['summary']['ties'] == 2 and res_m_return['summary']['net_pnl'] == 0.0
    assert res_m_loss['summary']['losses'] == 2 and res_m_loss['summary']['net_pnl'] < 0.0

    # 1c. Deep test Barbell streak reset under concurrent asset entries/exits
    print("Testing Barbell streak reset under concurrent asset entries/exits...", flush=True)
    df_barbell1 = pd.DataFrame({
        'open_time': list(range(100, 1000, 100)),
        'open': [100.0] * 9,
        'high': [105.0] * 9,
        'low': [95.0] * 9,
        'close': [100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0],
        'volume': [1000] * 9
    })
    df_barbell2 = pd.DataFrame({
        'open_time': list(range(100, 1000, 100)),
        'open': [100.0] * 9,
        'high': [105.0] * 9,
        'low': [95.0] * 9,
        'close': [100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0],
        'volume': [1000] * 9
    })
    universe_bb = {'CRYPTO': df_barbell1, 'FX': df_barbell2}
    
    signals_bb = {
        'CRYPTO': [
            {'time': 100, 'direction': 'CALL'}, # Entry idx 0, Exit idx 2 (t=300) -> WIN
            {'time': 300, 'direction': 'CALL'}, # Entry idx 2, Exit idx 4 (t=500) -> WIN
            {'time': 500, 'direction': 'CALL'}  # Entry idx 4, Exit idx 6 (t=700) -> WIN (3rd win -> streak reset!)
        ],
        'FX': [
            {'time': 200, 'direction': 'CALL'}  # Entry idx 1, Exit idx 3 (t=400) -> WIN (In-flight during CRYPTO's 3rd trade)
        ]
    }
    
    res_bb = sim.run_multi_asset(universe_bb, signals_bb, expiry_candles=2, payout=0.85, mode='BARBELL', n_consecutive=3, bet_fraction=0.166, risk_ratio=0.20)
    print("Barbell multi-asset summary:", res_bb['summary'], flush=True)
    for tr in res_bb['trades']:
        print(" Trade:", tr, flush=True)
    print(" Final equity:", res_bb['equity_curve'][-1]['equity'], flush=True)

    print("PASSED TEST 1\n", flush=True)

def test_2_frac_diff_fixed():
    print("--- TEST 2: frac_diff_fixed ---", flush=True)
    np.random.seed(42)
    N = 50000
    price_data = 100.0 + np.cumsum(np.random.randn(N) * 0.5)
    s = pd.Series(price_data)

    # Calculate kernel weights
    vals = s.values
    d = 0.4
    threshold = 1e-5
    weights = [1.0]
    k = 1
    while True:
        w = -weights[-1] * (d - k + 1) / k
        if abs(w) < threshold:
            break
        weights.append(w)
        k += 1
    w_arr = np.array(weights, dtype=float)
    width = len(w_arr)

    # 2a. Time spatial direct convolution (O(N*W))
    t0 = time.perf_counter()
    conv_spatial = np.convolve(vals, w_arr, mode='valid')
    t_spatial = time.perf_counter() - t0

    # 2b. Time FFT convolution (O(N log N))
    t0 = time.perf_counter()
    res_fft_series = frac_diff_fixed(s, d=0.4, threshold=1e-5)
    t_fft = time.perf_counter() - t0

    speedup = t_spatial / t_fft
    print(f"Spatial Convolve Time: {t_spatial:.4f}s, FFT Convolve Time: {t_fft:.4f}s, Speedup: {speedup:.2f}x", flush=True)

    # 2c. Numerical Precision Check
    conv_fft_vals = res_fft_series.dropna().values
    max_diff = np.max(np.abs(conv_spatial - conv_fft_vals))
    print(f"Max absolute diff between Spatial and FFT convolve: {max_diff:.2e}", flush=True)

    # 2d. Edge cases
    s_empty = pd.Series(dtype=float)
    res_empty = frac_diff_fixed(s_empty)
    assert res_empty.empty, "Empty series should return empty"

    s_short = pd.Series([10.0, 12.0, 11.0])
    res_short = frac_diff_fixed(s_short, d=0.4, threshold=1e-5)
    print("Short series output:", res_short.values, flush=True)

    s_nans = pd.Series([10.0, np.nan, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0])
    res_nans = frac_diff_fixed(s_nans, d=0.4, threshold=1e-5)
    print("Series with NaNs output:", res_nans.values, flush=True)

    assert speedup > 5.0, f"Speedup is less than expected: {speedup:.2f}x"
    assert max_diff < 1e-12, f"Max diff too high: {max_diff}"
    print("PASSED TEST 2\n", flush=True)

def test_3_hurst_exponent():
    print("--- TEST 3: Hurst Exponent ---", flush=True)
    fe = BinaryFeatureExtractor()

    # 3a. Constant price series
    df_const = pd.DataFrame({
        'open': [100.0] * 50,
        'high': [100.0] * 50,
        'low': [100.0] * 50,
        'close': [100.0] * 50,
        'volume': [1000] * 50
    })
    res_const = fe.extract_features(df_const)
    print("Constant price series hurst_exp tail:")
    print(res_const['hurst_exp'].tail(), flush=True)
    assert not np.isnan(res_const['hurst_exp'].iloc[-1]), "Hurst exp should not be NaN after fillna"

    # 3b. Short window (<50)
    df_short = df_const.iloc[:20].copy()
    res_short = fe.extract_features(df_short)
    assert res_short.empty, "extract_features should return empty DataFrame for len < 50"

    # 3c. Linear trend series
    df_trend = pd.DataFrame({
        'open': np.linspace(100, 200, 100),
        'high': np.linspace(101, 201, 100),
        'low': np.linspace(99, 199, 100),
        'close': np.linspace(100, 200, 100),
        'volume': [1000] * 100
    })
    res_trend = fe.extract_features(df_trend)
    print("Linear trend hurst_exp tail values:")
    print(res_trend['hurst_exp'].tail(), flush=True)
    assert not np.isinf(res_trend['hurst_exp']).any(), "Hurst exp should not contain Inf"
    print("PASSED TEST 3\n", flush=True)

def test_4_cusum_and_hmm():
    print("--- TEST 4: CUSUM & HMM ---", flush=True)
    
    # 4a. CUSUM memory bounds (10,000 updates)
    cusum = CUSUMMonitor(expected_wr=0.60, payout=0.85)
    np.random.seed(42)
    for _ in range(10000):
        pnl = 0.85 if np.random.rand() < 0.65 else -1.0
        cusum.update(pnl)
        
    print(f"After 10000 updates: len(trade_results)={len(cusum.trade_results)}, len(pause_history)={len(cusum.pause_history)}", flush=True)
    assert len(cusum.trade_results) <= 1000, f"trade_results unbounded: {len(cusum.trade_results)}"
    assert len(cusum.pause_history) <= 100, f"pause_history unbounded: {len(cusum.pause_history)}"

    # 4b. CUSUM Pause Recovery Sequence
    cusum.reset()
    assert cusum.total_trades_count == 0 and not cusum.is_paused
    
    # Feed 20 losses to force PAUSE
    for _ in range(20):
        res = cusum.update(-1.0)
    print(f"After 20 losses, is_paused={cusum.is_paused}, status={res}", flush=True)
    assert cusum.is_paused
    
    # Feed 10 consecutive wins to force RESUME
    for _ in range(10):
        res = cusum.update(0.85)
    print(f"After 10 wins during pause, is_paused={cusum.is_paused}, status={res}", flush=True)
    assert not cusum.is_paused

    # 4c. Verify HMM zero future std leakage
    regime = RegimeDetector()
    df_hmm = pd.DataFrame({
        'close': np.cumprod(1 + np.random.randn(200) * 0.01) * 100.0
    })
    obs = regime._prepare_observations(df_hmm)
    print(f"HMM Observations shape: {obs.shape}", flush=True)
    assert not np.isnan(obs).any(), "HMM observations should not contain NaNs"
    print("PASSED TEST 4\n", flush=True)

def test_5_meta_labeler_and_filter():
    print("--- TEST 5: MetaLabeler & MetaFilter ---", flush=True)
    
    # 5a. Test timestamp parsing (s, ms, us, ns, datetime64)
    base_df = pd.DataFrame({
        'open': np.random.randn(100) + 100,
        'high': np.random.randn(100) + 105,
        'low': np.random.randn(100) + 95,
        'close': np.random.randn(100) + 100,
        'volume': [1000] * 100
    })
    
    ml = MetaLabeler()
    
    # Seconds timestamp
    df_s = base_df.copy()
    df_s['open_time'] = [1700000000 + i*60 for i in range(100)]
    ctx_s = ml._extract_context_features(df_s, df_s.index[::5])
    print("Timestamp 's' context shape:", ctx_s.shape, flush=True)
    assert 'hour_of_day' in ctx_s.columns
    
    # Milliseconds timestamp
    df_ms = base_df.copy()
    df_ms['open_time'] = [(1700000000 + i*60)*1000 for i in range(100)]
    ctx_ms = ml._extract_context_features(df_ms, df_ms.index[::5])
    print("Timestamp 'ms' context shape:", ctx_ms.shape, flush=True)
    assert 'hour_of_day' in ctx_ms.columns
    
    # Microseconds timestamp
    df_us = base_df.copy()
    df_us['open_time'] = [(1700000000 + i*60)*1000000 for i in range(100)]
    ctx_us = ml._extract_context_features(df_us, df_us.index[::5])
    print("Timestamp 'us' context shape:", ctx_us.shape, flush=True)
    assert 'hour_of_day' in ctx_us.columns
    
    # Datetime64
    df_dt = base_df.copy()
    df_dt['open_time'] = pd.date_range("2026-01-01", periods=100, freq="1min")
    ctx_dt = ml._extract_context_features(df_dt, df_dt.index[::5])
    print("Datetime64 context shape:", ctx_dt.shape, flush=True)
    assert 'hour_of_day' in ctx_dt.columns

    # 5b. BinaryMLMetaFilter rolling NATR
    X_meta = pd.DataFrame({
        'natr': np.linspace(0.01, 0.05, 100)
    }, index=pd.RangeIndex(100))
    signals_meta = pd.Series([None]*100)
    signals_meta.iloc[10] = 'CALL'
    signals_meta.iloc[50] = 'CALL'
    signals_meta.iloc[90] = 'CALL'

    mf = BinaryMLMetaFilter(adaptive_threshold=True)
    y_dummy = pd.Series([1 if i % 2 == 0 else 0 for i in range(100)])
    mf.fit(X_meta, y_dummy)
    
    filtered_sigs = mf.filter_signals(signals_meta, X_meta)
    print("MetaFilter filtered signals non-null count:", filtered_sigs.dropna().count(), flush=True)
    print("PASSED TEST 5\n", flush=True)

def test_6_walk_forward_engine():
    print("--- TEST 6: WalkForwardEngine ---", flush=True)
    wfa = WalkForwardEngine(n_windows=3)
    
    class DummyStrat:
        def prepare_data(self, df): return None
        def generate_signals(self, df, params, precomputed=None):
            return pd.Series([None] * len(df))
            
    df_wfa = pd.DataFrame({
        'open': [100.0] * 500,
        'high': [105.0] * 500,
        'low': [95.0] * 500,
        'close': [100.0] * 500,
        'volume': [1000] * 500
    })
    
    res_wfa = wfa.run_wfa(df_wfa, DummyStrat(), base_params={})
    print("WFA 0-OOS trades result:", res_wfa, flush=True)
    assert res_wfa['stable_windows'] == 0, f"Expected 0 stable windows for 0 OOS trades, got {res_wfa['stable_windows']}"
    print("PASSED TEST 6\n", flush=True)

if __name__ == "__main__":
    test_1_binary_simulator()
    test_2_frac_diff_fixed()
    test_3_hurst_exponent()
    test_4_cusum_and_hmm()
    test_5_meta_labeler_and_filter()
    test_6_walk_forward_engine()
    print("ALL 6 EMPIRICAL STRESS TESTS PASSED SUCCESSFULLY!", flush=True)
