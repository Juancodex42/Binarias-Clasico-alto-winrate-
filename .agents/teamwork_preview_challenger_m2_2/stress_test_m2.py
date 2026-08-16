import sys
import os
import numpy as np
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = r"c:\Users\juanc\Desktop\prueba"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.simulator import BinarySimulator
from engine.optimizer import CapitalOptimizer
from engine.ml_engine.purged_cv import PurgedGroupTimeSeriesSplit
from optimizer_grid_search import create_labels as create_labels_grid
from run_backtest_comparison import create_labels as create_labels_comp

def generate_synthetic_df(n_rows=100, seed=42, base_price=100.0, vol=0.01):
    np.random.seed(seed)
    returns = np.random.normal(0, vol, n_rows)
    close_prices = base_price * np.exp(np.cumsum(returns))
    open_prices = np.roll(close_prices, 1)
    open_prices[0] = base_price
    high_prices = np.maximum(open_prices, close_prices) + np.abs(np.random.normal(0, vol/2, n_rows))
    low_prices = np.minimum(open_prices, close_prices) - np.abs(np.random.normal(0, vol/2, n_rows))
    
    open_times = np.arange(1600000000, 1600000000 + n_rows * 60, 60)
    
    return pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'open_time': open_times
    })

def generate_multi_asset_universe(n_assets=3, n_rows=100, seed=42):
    symbols = [f"ASSET_{i}" for i in range(n_assets)]
    universe = {}
    for i, sym in enumerate(symbols):
        universe[sym] = generate_synthetic_df(n_rows=n_rows, seed=seed + i)
    return universe


# =============================================================================
# SUITE 1: Capital Isolation Stress Tests
# =============================================================================
def test_suite_1_capital_isolation():
    print("--- Running Test Suite 1: Capital Isolation in Multi-Asset IS & OOS Splits ---", flush=True)
    results = []
    
    sim = BinarySimulator()
    universe_is = generate_multi_asset_universe(n_assets=2, n_rows=100, seed=100)
    universe_oos = generate_multi_asset_universe(n_assets=2, n_rows=100, seed=200)
    
    # Generate dense winning signals for IS to swell equity
    signals_is = {}
    for sym, df in universe_is.items():
        signals_list = []
        for idx in range(0, len(df) - 5, 10):
            sig_time = df['open_time'].iloc[idx]
            direction = 'CALL' if df['close'].iloc[idx+2] > df['open'].iloc[idx+1] else 'PUT'
            signals_list.append({'time': sig_time, 'direction': direction})
        signals_is[sym] = signals_list
        
    signals_oos = {}
    for sym, df in universe_oos.items():
        signals_list = []
        for idx in range(0, len(df) - 5, 10):
            sig_time = df['open_time'].iloc[idx]
            signals_list.append({'time': sig_time, 'direction': 'CALL'})
        signals_oos[sym] = signals_list

    # --- Test 1.1: BARBELL Mode High Profit IS -> OOS Isolation ---
    res_is = sim.run_multi_asset(universe_is, signals_is, mode='BARBELL', initial_capital=1000.0)
    is_ending_equity = res_is['equity_curve'][-1]['equity']
    
    res_oos = sim.run_multi_asset(universe_oos, signals_oos, mode='BARBELL', initial_capital=1000.0)
    oos_starting_equity = res_oos['equity_curve'][0]['equity']
    
    t1_1_pass = (oos_starting_equity == 1000.0) and (is_ending_equity != 1000.0)
    results.append(("1.1 BARBELL High-Profit IS -> OOS Isolation", t1_1_pass, f"IS end: {is_ending_equity:.2f}, OOS start: {oos_starting_equity:.2f}"))
    print(f"  [1.1] {'PASS' if t1_1_pass else 'FAIL'}", flush=True)

    # --- Test 1.2: BARBELL Mode Bankruptcy IS -> OOS Isolation ---
    signals_is_loss = {}
    for sym, df in universe_is.items():
        signals_list = []
        for idx in range(0, len(df) - 5, 5):
            sig_time = df['open_time'].iloc[idx]
            direction = 'PUT' if df['close'].iloc[idx+2] > df['open'].iloc[idx+1] else 'CALL'
            signals_list.append({'time': sig_time, 'direction': direction})
        signals_is_loss[sym] = signals_list

    res_is_loss = sim.run_multi_asset(universe_is, signals_is_loss, mode='BARBELL', initial_capital=1000.0)
    is_loss_ending_equity = res_is_loss['equity_curve'][-1]['equity']
    
    res_oos_after_loss = sim.run_multi_asset(universe_oos, signals_oos, mode='BARBELL', initial_capital=1000.0)
    oos_start_after_loss = res_oos_after_loss['equity_curve'][0]['equity']
    
    t1_2_pass = (oos_start_after_loss == 1000.0)
    results.append(("1.2 BARBELL Bankruptcy IS -> OOS Isolation", t1_2_pass, f"IS end loss: {is_loss_ending_equity:.2f}, OOS start: {oos_start_after_loss:.2f}"))
    print(f"  [1.2] {'PASS' if t1_2_pass else 'FAIL'}", flush=True)

    # --- Test 1.3: REINVESTMENT Mode Pair State Isolation ---
    res_is_reinv = sim.run_multi_asset(universe_is, signals_is, mode='REINVESTMENT', initial_capital=1000.0)
    is_reinv_end = res_is_reinv['equity_curve'][-1]['equity']
    
    res_oos_reinv = sim.run_multi_asset(universe_oos, signals_oos, mode='REINVESTMENT', initial_capital=1000.0)
    oos_reinv_start = res_oos_reinv['equity_curve'][0]['equity']
    
    t1_3_pass = (oos_reinv_start == 1000.0)
    results.append(("1.3 REINVESTMENT Pair State IS -> OOS Isolation", t1_3_pass, f"IS end: {is_reinv_end:.2f}, OOS start: {oos_reinv_start:.2f}"))
    print(f"  [1.3] {'PASS' if t1_3_pass else 'FAIL'}", flush=True)

    # --- Test 1.4: SIMPLE Mode Capital Isolation ---
    res_is_simple = sim.run_multi_asset(universe_is, signals_is, mode='SIMPLE', initial_capital=1000.0)
    res_oos_simple = sim.run_multi_asset(universe_oos, signals_oos, mode='SIMPLE', initial_capital=1000.0)
    t1_4_pass = (res_oos_simple['equity_curve'][0]['equity'] == 1000.0)
    results.append(("1.4 SIMPLE Mode IS -> OOS Isolation", t1_4_pass, f"OOS start: {res_oos_simple['equity_curve'][0]['equity']:.2f}"))
    print(f"  [1.4] {'PASS' if t1_4_pass else 'FAIL'}", flush=True)

    # --- Test 1.5: Purged CV Split Multi-Asset Capital Reset ---
    universe_full = generate_multi_asset_universe(n_assets=3, n_rows=200, seed=500)
    uni_is = {}
    uni_oos = {}
    for sym, df in universe_full.items():
        n_sym = len(df)
        is_end, oos_start = PurgedGroupTimeSeriesSplit.purge_embargo_split(
            n_samples=n_sym, train_ratio=0.70, expiry_candles=2, embargo_pct=0.01
        )
        uni_is[sym] = df.iloc[:is_end].copy().reset_index(drop=True)
        uni_oos[sym] = df.iloc[oos_start:].copy().reset_index(drop=True)
        
    res_purged_is = sim.run_multi_asset(uni_is, signals_is, mode='BARBELL', initial_capital=1000.0)
    res_purged_oos = sim.run_multi_asset(uni_oos, signals_oos, mode='BARBELL', initial_capital=1000.0)
    
    t1_5_pass = (res_purged_is['equity_curve'][0]['equity'] == 1000.0) and (res_purged_oos['equity_curve'][0]['equity'] == 1000.0)
    results.append(("1.5 Purged CV Split Multi-Asset Capital Reset", t1_5_pass, f"IS start: {res_purged_is['equity_curve'][0]['equity']}, OOS start: {res_purged_oos['equity_curve'][0]['equity']}"))
    print(f"  [1.5] {'PASS' if t1_5_pass else 'FAIL'}", flush=True)

    # --- Test 1.6: 5-Fold Walk-Forward Sequential Split Capital Reset ---
    wf_passes = []
    for fold in range(5):
        uni_fold = generate_multi_asset_universe(n_assets=2, n_rows=50, seed=300+fold)
        r = sim.run_multi_asset(uni_fold, signals_oos, mode='BARBELL', initial_capital=1000.0)
        wf_passes.append(r['equity_curve'][0]['equity'] == 1000.0)
    t1_6_pass = all(wf_passes)
    results.append(("1.6 5-Fold Walk-Forward Capital Reset", t1_6_pass, f"All 5 folds started with $1000.0: {t1_6_pass}"))
    print(f"  [1.6] {'PASS' if t1_6_pass else 'FAIL'}", flush=True)

    # --- Test 1.7: Custom Initial Capital ($500.0 and $2500.0) Isolation ---
    res_500 = sim.run_multi_asset(universe_is, signals_is, mode='BARBELL', initial_capital=500.0)
    res_2500 = sim.run_multi_asset(universe_oos, signals_oos, mode='BARBELL', initial_capital=2500.0)
    t1_7_pass = (res_500['equity_curve'][0]['equity'] == 500.0) and (res_2500['equity_curve'][0]['equity'] == 2500.0)
    results.append(("1.7 Custom Initial Capital Isolation ($500 / $2500)", t1_7_pass, f"500 start: {res_500['equity_curve'][0]['equity']}, 2500 start: {res_2500['equity_curve'][0]['equity']}"))
    print(f"  [1.7] {'PASS' if t1_7_pass else 'FAIL'}", flush=True)

    return results


# =============================================================================
# SUITE 2: Label Alignment & BinarySimulator 100% Agreement Stress Tests
# =============================================================================
def test_suite_2_label_matching():
    print("\n--- Running Test Suite 2: Label Alignment & BinarySimulator 100% Agreement ---", flush=True)
    results = []
    sim = BinarySimulator()
    
    # --- Test 2.1: Randomized Synthetic Datasets (100 iterations across varied conditions) ---
    mismatches_grid = 0
    mismatches_comp = 0
    total_evaluated_trades = 0
    
    for seed in range(100):
        n_rows = np.random.randint(15, 150)
        vol = np.random.uniform(0.001, 0.05)
        df = generate_synthetic_df(n_rows=n_rows, seed=seed, vol=vol)
        
        sig_choices = ['CALL', 'PUT', None]
        probs = [0.25, 0.25, 0.50]
        signals = pd.Series(np.random.choice(sig_choices, size=n_rows, p=probs), index=df.index)
        
        expiry = np.random.choice([1, 2, 3, 5])
        
        sim_res = sim.run(df, signals, expiry_candles=expiry, payout=0.85)
        sim_trades = {t['index']: 1.0 if t['result'] == 'WIN' else 0.0 for t in sim_res['trades']}
        
        labels_grid = create_labels_grid(df, signals, expiry_candles=expiry)
        labels_comp = create_labels_comp(df, signals, expiry_candles=expiry)
        
        for idx, sim_win_label in sim_trades.items():
            total_evaluated_trades += 1
            
            if idx not in labels_grid or labels_grid.loc[idx] != sim_win_label:
                mismatches_grid += 1
                
            if idx not in labels_comp or labels_comp.loc[idx] != sim_win_label:
                mismatches_comp += 1
                
    t2_1_pass = (mismatches_grid == 0) and (mismatches_comp == 0) and (total_evaluated_trades > 0)
    results.append(("2.1 Randomized 100-Iteration Harness", t2_1_pass, f"Evaluated {total_evaluated_trades} trades. Mismatches Grid: {mismatches_grid}, Comp: {mismatches_comp}"))
    print(f"  [2.1] {'PASS' if t2_1_pass else 'FAIL'} ({total_evaluated_trades} trades tested)", flush=True)

    # --- Test 2.2: Multi-Candle Expiries (1, 2, 3, 5, 10, 12, 15) ---
    multi_expiry_mismatches = 0
    df = generate_synthetic_df(n_rows=150, seed=777)
    signals = pd.Series(['CALL' if i % 2 == 0 else 'PUT' for i in range(len(df))], index=df.index)
    
    for exp in [1, 2, 3, 5, 10, 12, 15]:
        sim_res = sim.run(df, signals, expiry_candles=exp)
        sim_trades = {t['index']: 1.0 if t['result'] == 'WIN' else 0.0 for t in sim_res['trades']}
        l_grid = create_labels_grid(df, signals, expiry_candles=exp)
        l_comp = create_labels_comp(df, signals, expiry_candles=exp)
        
        for idx, win_val in sim_trades.items():
            if l_grid.loc[idx] != win_val or l_comp.loc[idx] != win_val:
                multi_expiry_mismatches += 1
                
    t2_2_pass = (multi_expiry_mismatches == 0)
    results.append(("2.2 Multi-Candle Expiries (1..15)", t2_2_pass, f"Expiries tested: [1,2,3,5,10,12,15]. Mismatches: {multi_expiry_mismatches}"))
    print(f"  [2.2] {'PASS' if t2_2_pass else 'FAIL'}", flush=True)

    # --- Test 2.3: Boundary Signals (First, Last Valid, Out-of-Bounds, Single/Two-Row DFs) ---
    boundary_mismatches = 0
    
    # Case A: Signal on last candle (len-1)
    df_short = generate_synthetic_df(n_rows=5, seed=888)
    sig_last = pd.Series([None, None, None, None, 'CALL'], index=df_short.index)
    res_last = sim.run(df_short, sig_last, expiry_candles=1)
    lbl_last_g = create_labels_grid(df_short, sig_last, expiry_candles=1)
    lbl_last_c = create_labels_comp(df_short, sig_last, expiry_candles=1)
    if len(res_last['trades']) != 0 or len(lbl_last_g) != 0 or len(lbl_last_c) != 0:
        boundary_mismatches += 1
        
    # Case B: Signal on index len - expiry_candles (cannot execute exit)
    sig_oob = pd.Series([None, None, None, 'CALL', None], index=df_short.index)
    res_oob = sim.run(df_short, sig_oob, expiry_candles=2)
    lbl_oob_g = create_labels_grid(df_short, sig_oob, expiry_candles=2)
    lbl_oob_c = create_labels_comp(df_short, sig_oob, expiry_candles=2)
    if len(res_oob['trades']) != 0 or len(lbl_oob_g) != 0 or len(lbl_oob_c) != 0:
        boundary_mismatches += 1

    # Case C: 1-Row DataFrame
    df_1 = generate_synthetic_df(n_rows=1, seed=999)
    sig_1 = pd.Series(['CALL'], index=df_1.index)
    res_1 = sim.run(df_1, sig_1, expiry_candles=1)
    lbl_1_g = create_labels_grid(df_1, sig_1, expiry_candles=1)
    if len(res_1['trades']) != 0 or len(lbl_1_g) != 0:
        boundary_mismatches += 1

    t2_3_pass = (boundary_mismatches == 0)
    results.append(("2.3 Boundary & Out-of-Bounds Signal Matching", t2_3_pass, f"Boundary mismatches: {boundary_mismatches}"))
    print(f"  [2.3] {'PASS' if t2_3_pass else 'FAIL'}", flush=True)

    # --- Test 2.4: Epsilon Boundary Cases (_PRICE_EPS = 1e-8) ---
    eps_mismatches = 0
    
    # Case A: Exact Tie (diff = 0.0)
    df_eps = pd.DataFrame({
        'open': [100.0, 100.0, 100.0],
        'high': [101.0, 101.0, 101.0],
        'low': [99.0, 99.0, 99.0],
        'close': [100.0, 100.0, 100.0],
        'open_time': [1000, 2000, 3000]
    })
    sig_eps = pd.Series(['CALL', None, None], index=df_eps.index)
    res_eps = sim.run(df_eps, sig_eps, expiry_candles=1)
    lbl_eps_g = create_labels_grid(df_eps, sig_eps, expiry_candles=1)
    if res_eps['trades'][0]['result'] != 'TIE' or lbl_eps_g.iloc[0] != 0.0:
        eps_mismatches += 1
        
    # Case B: Diff exactly 1e-8 (Tie limit)
    df_eps2 = pd.DataFrame({
        'open': [100.0, 100.0, 100.0],
        'close': [100.0, 100.0 + 1e-8, 100.0],
        'high': [101.0, 101.0, 101.0],
        'low': [99.0, 99.0, 99.0],
        'open_time': [1000, 2000, 3000]
    })
    res_eps2 = sim.run(df_eps2, sig_eps, expiry_candles=1)
    lbl_eps2_g = create_labels_grid(df_eps2, sig_eps, expiry_candles=1)
    if res_eps2['trades'][0]['result'] != 'TIE' or lbl_eps2_g.iloc[0] != 0.0:
        eps_mismatches += 1

    # Case C: Diff 1e-8 + 1e-12 (Win for CALL)
    df_eps3 = pd.DataFrame({
        'open': [100.0, 100.0, 100.0],
        'close': [100.0, 100.0 + 1e-8 + 1e-12, 100.0],
        'high': [101.0, 101.0, 101.0],
        'low': [99.0, 99.0, 99.0],
        'open_time': [1000, 2000, 3000]
    })
    res_eps3 = sim.run(df_eps3, sig_eps, expiry_candles=1)
    lbl_eps3_g = create_labels_grid(df_eps3, sig_eps, expiry_candles=1)
    if res_eps3['trades'][0]['result'] != 'WIN' or lbl_eps3_g.iloc[0] != 1.0:
        eps_mismatches += 1

    t2_4_pass = (eps_mismatches == 0)
    results.append(("2.4 Epsilon Boundary Tolerances (_PRICE_EPS = 1e-8)", t2_4_pass, f"Epsilon mismatches: {eps_mismatches}"))
    print(f"  [2.4] {'PASS' if t2_4_pass else 'FAIL'}", flush=True)

    # --- Test 2.5: Non-Standard Index Types (DatetimeIndex) ---
    df_dt = generate_synthetic_df(n_rows=50, seed=555)
    df_dt.index = pd.date_range("2026-01-01", periods=50, freq="1h")
    sig_dt = pd.Series([None]*50, index=df_dt.index)
    sig_dt.iloc[10] = 'CALL'
    sig_dt.iloc[20] = 'PUT'
    
    res_dt = sim.run(df_dt, sig_dt, expiry_candles=1)
    lbl_dt_g = create_labels_grid(df_dt, sig_dt, expiry_candles=1)
    lbl_dt_c = create_labels_comp(df_dt, sig_dt, expiry_candles=1)
    
    dt_mismatches = 0
    for t in res_dt['trades']:
        dt_idx = df_dt.index[t['index']]
        expected_val = 1.0 if t['result'] == 'WIN' else 0.0
        if lbl_dt_g.loc[dt_idx] != expected_val or lbl_dt_c.loc[dt_idx] != expected_val:
            dt_mismatches += 1
            
    t2_5_pass = (dt_mismatches == 0)
    results.append(("2.5 Non-Standard Indexing Support (DatetimeIndex)", t2_5_pass, f"Index mismatches: {dt_mismatches}"))
    print(f"  [2.5] {'PASS' if t2_5_pass else 'FAIL'}", flush=True)

    return results


def run_all_stress_tests():
    print("=========================================================================", flush=True)
    print("       EMPIRICAL STRESS TEST SUITE — MILESTONE 2 CHALLENGER 2            ", flush=True)
    print("=========================================================================\n", flush=True)
    
    suite1_res = test_suite_1_capital_isolation()
    suite2_res = test_suite_2_label_matching()
    
    all_res = suite1_res + suite2_res
    all_passed = all(r[1] for r in all_res)
    
    print("\n=========================================================================", flush=True)
    print("                           SUMMARY OF RESULTS                            ", flush=True)
    print("=========================================================================", flush=True)
    for title, status, details in all_res:
        status_str = "PASS" if status else "FAIL"
        print(f"[{status_str}] {title}", flush=True)
        print(f"       Details: {details}", flush=True)
        
    verdict = "PASS" if all_passed else "FAIL"
    print("\n=========================================================================", flush=True)
    print(f"FINAL VERDICT: {verdict}", flush=True)
    print("=========================================================================\n", flush=True)
    
    return verdict, all_res

if __name__ == '__main__':
    verdict, _ = run_all_stress_tests()
    sys.exit(0 if verdict == "PASS" else 1)
