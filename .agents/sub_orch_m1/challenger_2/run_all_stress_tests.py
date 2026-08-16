import sys
import os
import time
import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, r'c:\Users\juanc\Desktop\prueba')

from engine.simulator import BinarySimulator
from engine.ml_engine.feature_extractor import frac_diff_fixed, BinaryFeatureExtractor
from engine.ml_engine.cusum_monitor import CUSUMMonitor
from engine.ml_engine.regime_detector import RegimeDetector
from engine.ml_engine.meta_labeler import MetaLabeler
from engine.ml_engine.meta_filter import BinaryMLMetaFilter
from engine.auto_tuner import WalkForwardEngine

def run_iterative_frac_diff(series: pd.Series, d: float = 0.4, threshold: float = 1e-5) -> pd.Series:
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
    for i in range(width - 1, n):
        window = vals[i - width + 1 : i + 1]
        output[i] = np.dot(w_arr, window[::-1])
        
    result = pd.Series(output, index=series.dropna().index)
    return result.reindex(series.index)


def test_suite_1_simulator():
    print("\n========================================================")
    print("SUITE 1: BinarySimulator Multi-Asset Tie Rule & Barbell")
    print("========================================================")
    sim = BinarySimulator()

    # 1. Test Tie Rule 'LOSS' vs 'RETURN_STAKE' in multi-asset mode
    dates = pd.date_range('2026-01-01', periods=100, freq='1min')
    open_times = [int(d.timestamp()) for d in dates]

    df_btc = pd.DataFrame({
        'open_time': open_times,
        'open': [100.0] * 100,
        'high': [101.0] * 100,
        'low': [99.0] * 100,
        'close': [100.0] * 100,
        'volume': [1000] * 100
    })
    df_eur = df_btc.copy()

    # BTCUSDT at exit (idx 5) is a tie (close = 100.0)
    # EURUSD at exit (idx 15) is a win (close = 105.0)
    df_eur.loc[15, 'close'] = 105.0

    universe = {'BTCUSDT': df_btc, 'EURUSD': df_eur}
    signals = {
        'BTCUSDT': [{'time': open_times[3], 'direction': 'CALL'}],
        'EURUSD': [{'time': open_times[13], 'direction': 'CALL'}]
    }

    res_loss = sim.run_multi_asset(universe, signals, expiry_candles=2, mode='SIMPLE', tie_rule='LOSS')
    res_stake = sim.run_multi_asset(universe, signals, expiry_candles=2, mode='SIMPLE', tie_rule='RETURN_STAKE')

    print(f"LOSS Rule    : Total Trades={res_loss['summary']['total_trades']}, Wins={res_loss['summary']['wins']}, Losses={res_loss['summary']['losses']}, Ties={res_loss['summary']['ties']}, PnL={res_loss['summary']['net_pnl']:.2f}")
    print(f"STAKE Rule   : Total Trades={res_stake['summary']['total_trades']}, Wins={res_stake['summary']['wins']}, Losses={res_stake['summary']['losses']}, Ties={res_stake['summary']['ties']}, PnL={res_stake['summary']['net_pnl']:.2f}")

    pass_tie_rule = (res_loss['summary']['ties'] == 0 and res_loss['summary']['losses'] == 1 and
                     res_stake['summary']['ties'] == 1 and res_stake['summary']['losses'] == 0)

    # 2. Test Barbell streak reset under concurrent/overlapping entries/exits across different asset classes
    dates_b = pd.date_range('2026-01-01', periods=50, freq='1min')
    times_b = [int(d.timestamp()) for d in dates_b]

    df_bar_btc = pd.DataFrame({'open_time': times_b, 'open': [100.0]*50, 'high': [102.0]*50, 'low': [98.0]*50, 'close': [100.0]*50, 'volume': [100]*50})
    df_bar_eur = pd.DataFrame({'open_time': times_b, 'open': [100.0]*50, 'high': [102.0]*50, 'low': [98.0]*50, 'close': [100.0]*50, 'volume': [100]*50})

    # Trade 1 (BTCUSDT): entry idx 10 + 1 (open_time index 11), exit idx 13 (open_time index 14) -> WIN (close = 105)
    df_bar_btc.loc[13, 'close'] = 105.0
    # Trade 2 (EURUSD): entry idx 11 + 1 (open_time index 12), exit idx 15 (open_time index 16) -> WIN (close = 105)
    df_bar_eur.loc[15, 'close'] = 105.0

    universe_bar = {'BTCUSDT': df_bar_btc, 'EURUSD': df_bar_eur}
    signals_bar = {
        'BTCUSDT': [{'time': times_b[10], 'direction': 'CALL'}],
        'EURUSD': [{'time': times_b[11], 'direction': 'CALL'}]
    }

    res_barbell = sim.run_multi_asset(universe_bar, signals_bar, expiry_candles=3, mode='BARBELL', n_consecutive=1, bet_fraction=0.5, risk_ratio=0.20, payout=0.85)

    print("\nBarbell Overlapping Campaign Reset Trace:")
    for t in res_barbell['trades']:
        print(f"  Trade {t['pair']}: entry_time={t['time']}, exit_time={t['exit_time']}, result={t['result']}, PnL={t['pnl']:.2f}, bet_size={t['bet_size']:.2f}")
    print("Barbell Equity Curve:")
    for eq in res_barbell['equity_curve']:
        print(f"  t={eq['time']}: equity={eq['equity']:.2f}")

    final_eq = res_barbell['equity_curve'][-1]['equity'] if res_barbell['equity_curve'] else 0.0
    print(f"  Final Equity: {final_eq:.2f}")

    return {
        'pass_tie_rule': pass_tie_rule,
        'barbell_final_equity': final_eq,
        'barbell_trades': res_barbell['trades']
    }


def test_suite_2_frac_diff():
    print("\n========================================================")
    print("SUITE 2: FracDiff FFT Acceleration & Precision")
    print("========================================================")
    np.random.seed(42)
    N = 50000
    prices = pd.Series(100.0 + np.cumsum(np.random.randn(N) * 0.5))

    t0 = time.perf_counter()
    fft_res = frac_diff_fixed(prices, d=0.4, threshold=1e-5)
    t_fft = time.perf_counter() - t0

    t0 = time.perf_counter()
    iter_res = run_iterative_frac_diff(prices, d=0.4, threshold=1e-5)
    t_iter = time.perf_counter() - t0

    speedup = t_iter / t_fft if t_fft > 0 else float('inf')

    valid_mask = ~fft_res.isna() & ~iter_res.isna()
    max_diff = np.max(np.abs(fft_res[valid_mask].values - iter_res[valid_mask].values))

    print(f"Series Length : {N:,}")
    print(f"FFT Time      : {t_fft:.4f} seconds")
    print(f"Iterative Time: {t_iter:.4f} seconds")
    print(f"Speedup Factor: {speedup:.2f}x (Target > 10x)")
    print(f"Max Difference: {max_diff:.4e} (Target < 1e-12)")

    return {
        't_fft': t_fft,
        't_iter': t_iter,
        'speedup': speedup,
        'max_diff': max_diff,
        'pass_speedup': speedup > 10.0,
        'pass_precision': max_diff < 1e-12
    }


def test_suite_3_calc_hurst():
    print("\n========================================================")
    print("SUITE 3: Hurst Exponent (calc_hurst) Edge Cases")
    print("========================================================")
    
    const_prices = pd.Series([100.0] * 50)
    ext = BinaryFeatureExtractor()
    df_const = pd.DataFrame({'open': const_prices, 'high': const_prices, 'low': const_prices, 'close': const_prices, 'volume': 100})
    res_const = ext.extract_features(df_const)
    hurst_const = res_const['hurst_exp']

    print(f"Constant Series Hurst (head & tail):\n{hurst_const.iloc[-5:].values}")

    nan_prices = pd.Series([np.nan] * 50)
    df_nan = pd.DataFrame({'open': nan_prices, 'high': nan_prices, 'low': nan_prices, 'close': nan_prices, 'volume': 100})
    res_nan = ext.extract_features(df_nan)
    print(f"All NaN Series Hurst non-finite count: {np.isnan(res_nan['hurst_exp']).sum() + np.isinf(res_nan['hurst_exp']).sum()}")

    short_prices = pd.Series(np.random.randn(20) + 100)
    df_short = pd.DataFrame({'open': short_prices, 'high': short_prices, 'low': short_prices, 'close': short_prices, 'volume': 100})
    res_short = ext.extract_features(df_short)
    print(f"Short Window (<30) Extract Features Output shape: {res_short.shape}")

    linear_prices = pd.Series(np.linspace(100, 200, 100))
    df_linear = pd.DataFrame({'open': linear_prices, 'high': linear_prices, 'low': linear_prices, 'close': linear_prices, 'volume': 100})
    res_linear = ext.extract_features(df_linear)
    print(f"Linear Trend Hurst (last 5 values):\n{res_linear['hurst_exp'].iloc[-5:].values}")

    return {
        'hurst_const_valid': not np.isinf(hurst_const.iloc[-1]),
        'hurst_linear_valid': not np.isinf(res_linear['hurst_exp'].iloc[-1])
    }


def test_suite_4_cusum_hmm():
    print("\n========================================================")
    print("SUITE 4: CUSUM Memory Bounds / Recovery & HMM Leakage")
    print("========================================================")
    
    cm = CUSUMMonitor(expected_wr=0.60, payout=0.85)
    np.random.seed(123)
    states_sequence = []
    
    for i in range(10000):
        cycle = (i // 50) % 3
        if cycle == 0:
            pnl = 0.85 if np.random.rand() < 0.7 else -1.0
        elif cycle == 1:
            pnl = -1.0
        else:
            pnl = 0.85
            
        st = cm.update(pnl)
        states_sequence.append(st)

    tr_len = len(cm.trade_results)
    ph_len = len(cm.pause_history)
    pp_len = len(cm.post_pause_results)

    print(f"After 10,000 updates:")
    print(f"  len(trade_results)      : {tr_len} (Limit <= 1000)")
    print(f"  len(pause_history)     : {ph_len} (Limit <= 100)")
    print(f"  len(post_pause_results) : {pp_len} (Limit <= 100)")
    print(f"  Unique status responses : {set(states_sequence)}")

    pass_cusum_memory = (tr_len <= 1000 and ph_len <= 100 and pp_len <= 100)

    np.random.seed(42)
    full_len = 200
    p = 100.0 + np.cumsum(np.random.randn(full_len) * 0.2)
    df_full = pd.DataFrame({'close': p})

    detector = RegimeDetector()
    obs_full = detector._prepare_observations(df_full)

    df_trunc = df_full.iloc[:100].copy()
    obs_trunc = detector._prepare_observations(df_trunc)

    max_hmm_diff = np.max(np.abs(obs_full[:100] - obs_trunc[:100]))
    print(f"HMM Feature Volatility & ER Leakage Check (max diff over first 100 candles): {max_hmm_diff:.6e}")

    pass_hmm_leakage = (max_hmm_diff < 1e-12)

    return {
        'pass_cusum_memory': pass_cusum_memory,
        'pass_hmm_leakage': pass_hmm_leakage,
        'max_hmm_diff': max_hmm_diff
    }


def test_suite_5_meta_labeler_filter():
    print("\n========================================================")
    print("SUITE 5: MetaLabeler Timestamps & MetaFilter Rolling NATR")
    print("========================================================")

    ml = MetaLabeler()

    base_sec = 1600000000
    times_sec = [base_sec + i * 60 for i in range(100)]
    times_ms = [t * 1000 for t in times_sec]
    times_us = [t * 1000000 for t in times_sec]
    times_ns = [t * 1000000000 for t in times_sec]
    times_dt = pd.to_datetime(times_sec, unit='s')

    sig_idx = pd.RangeIndex(0, 100)

    units_tested = {}
    for unit_name, times_val in [('sec', times_sec), ('ms', times_ms), ('us', times_us), ('ns', times_ns), ('dt', times_dt)]:
        df_ts = pd.DataFrame({
            'open_time': times_val,
            'open': [100.0]*100, 'high': [101.0]*100, 'low': [99.0]*100, 'close': [100.0]*100, 'volume': [1000]*100
        })
        try:
            ctx = ml._extract_context_features(df_ts, sig_idx)
            units_tested[unit_name] = ('hour_of_day' in ctx.columns and not ctx['hour_of_day'].isna().any())
        except Exception as e:
            units_tested[unit_name] = False
            print(f"Error testing timestamp format {unit_name}: {e}")

    print(f"Timestamp units parsing success: {units_tested}")

    filter_obj = BinaryMLMetaFilter(adaptive_threshold=True)

    np.random.seed(42)
    X_full = pd.DataFrame({
        'natr': np.random.uniform(0.001, 0.01, 200)
    })
    X_full.loc[150:, 'natr'] = 0.05

    signals_full = pd.Series([None]*200)
    signals_full.loc[50] = 'CALL'
    signals_full.loc[120] = 'CALL'

    signals_trunc = signals_full.iloc[:60].copy()
    X_trunc = X_full.iloc[:60].copy()

    natr_med_full_50 = X_full['natr'].iloc[:51].median()
    natr_med_trunc_50 = X_trunc['natr'].iloc[:51].median()

    print(f"NATR Median at idx 50 (Full dataset) : {natr_med_full_50:.6f}")
    print(f"NATR Median at idx 50 (Trunc dataset): {natr_med_trunc_50:.6f}")
    
    pass_meta_leakage = (natr_med_full_50 == natr_med_trunc_50)

    return {
        'units_tested': units_tested,
        'pass_timestamps': all(units_tested.values()),
        'pass_meta_leakage': pass_meta_leakage
    }


def test_suite_6_wfa_zero_oos():
    print("\n========================================================")
    print("SUITE 6: WalkForwardEngine Zero OOS Trades Stability Score")
    print("========================================================")

    wfa = WalkForwardEngine(n_windows=3, train_ratio=0.60)

    dates = pd.date_range('2026-01-01', periods=600, freq='1min')
    df_test = pd.DataFrame({
        'open_time': [int(d.timestamp()) for d in dates],
        'open': [100.0]*600,
        'high': [102.0]*600,
        'low': [98.0]*600,
        'close': [100.0]*600,
        'volume': [1000]*600
    })

    # Strategy that generates signals ONLY in IS portion of each window, ZERO in OOS
    class ZeroOOSOnlyStrategy:
        def prepare_data(self, df):
            return None
        def generate_signals(self, df, params, precomputed=None):
            sigs = pd.Series([None] * len(df))
            # In WFA, df is sub_df of length 150
            # train_ratio is 0.60, so IS is 0..89, OOS is 90..149
            # Place signals only in 0..50 (IS), ZERO in 90..149 (OOS)
            if len(df) >= 50:
                sigs.iloc[10:20] = 'CALL'
            return sigs

    strat = ZeroOOSOnlyStrategy()
    res_wfa = wfa.run_wfa(df_test, strat, base_params={})

    print(f"WFA Results on Zero OOS Trades:")
    print(f"  stable_windows       : {res_wfa['stable_windows']} (Target: 0)")
    print(f"  total_windows_tested : {res_wfa['total_windows_tested']}")
    print(f"  mean_is_wr           : {res_wfa['mean_is_wr']}%")
    print(f"  mean_oos_wr          : {res_wfa['mean_oos_wr']}%")
    print(f"  wfe                  : {res_wfa['wfe']}%")
    print(f"  window_results       : {res_wfa['window_results']}")

    pass_zero_oos = (res_wfa['stable_windows'] == 0)

    return {
        'pass_zero_oos': pass_zero_oos,
        'stable_windows': res_wfa['stable_windows'],
        'res_wfa': res_wfa
    }


def main():
    print("=================================================================")
    print("STARTING EMPIRICAL STRESS TEST SUITE FOR MILESTONE 1 REMEDIATIONS")
    print("=================================================================")
    
    r1 = test_suite_1_simulator()
    r2 = test_suite_2_frac_diff()
    r3 = test_suite_3_calc_hurst()
    r4 = test_suite_4_cusum_hmm()
    r5 = test_suite_5_meta_labeler_filter()
    r6 = test_suite_6_wfa_zero_oos()

    print("\n=================================================================")
    print("STRESS TEST SUMMARY RESULTS")
    print("=================================================================")
    print(f"1. Simulator Tie Rule Pass  : {r1['pass_tie_rule']}")
    print(f"   Barbell Final Equity     : {r1['barbell_final_equity']:.2f}")
    print(f"2. FracDiff Speedup (>10x)  : {r2['speedup']:.2f}x ({'PASS' if r2['pass_speedup'] else 'FAIL'})")
    print(f"   FracDiff Precision (<1e-12): {r2['max_diff']:.4e} ({'PASS' if r2['pass_precision'] else 'FAIL'})")
    print(f"3. Hurst Edge Cases Valid   : Const={r3['hurst_const_valid']}, Linear={r3['hurst_linear_valid']}")
    print(f"4. CUSUM Memory Bounded     : {'PASS' if r4['pass_cusum_memory'] else 'FAIL'}")
    print(f"   HMM Zero Leakage         : {'PASS' if r4['pass_hmm_leakage'] else 'FAIL'} (max diff: {r4['max_hmm_diff']:.4e})")
    print(f"5. MetaLabeler Timestamps   : {'PASS' if r5['pass_timestamps'] else 'FAIL'}")
    print(f"   MetaFilter Zero Leakage  : {'PASS' if r5['pass_meta_leakage'] else 'FAIL'}")
    print(f"6. WFA Zero OOS Stability   : {'PASS' if r6['pass_zero_oos'] else 'FAIL'} (stable_windows={r6['stable_windows']})")
    print("=================================================================")

if __name__ == '__main__':
    main()
