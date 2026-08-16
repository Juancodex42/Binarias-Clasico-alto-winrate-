import sys, os
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

PROJECT_ROOT = r"c:\Users\juanc\Desktop\prueba"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

out_path = os.path.join(os.path.dirname(__file__), "results.txt")
out_file = open(out_path, "w", encoding="utf-8")

def log(msg):
    print(msg, flush=True)
    out_file.write(str(msg) + "\n")
    out_file.flush()

from engine.simulator import BinarySimulator
from engine.ml_engine.regime_detector import RegimeDetector
from engine.ml_engine.purged_cv import PurgedGroupTimeSeriesSplit
from optimizer_grid_search import create_labels as create_labels_grid
from run_backtest_comparison import create_labels as create_labels_comp

def generate_test_ohlcv(n_rows=500, seed=42):
    np.random.seed(seed)
    returns = np.random.normal(0.0002, 0.01, n_rows)
    price = 100.0 * np.exp(np.cumsum(returns))
    high = price * (1.0 + np.abs(np.random.normal(0, 0.005, n_rows)))
    low = price * (1.0 - np.abs(np.random.normal(0, 0.005, n_rows)))
    open_p = price * (1.0 + np.random.normal(0, 0.002, n_rows))
    close_p = price
    volume = np.random.uniform(100, 1000, n_rows)
    open_time = np.arange(n_rows) * 300 + 1600000000

    df = pd.DataFrame({
        'open_time': open_time,
        'open': open_p,
        'high': high,
        'low': low,
        'close': close_p,
        'volume': volume
    })
    return df

log("=== STARTING STRESS TESTS FOR MILESTONE 2 ===")

# -----------------------------------------------------------------------------
# TEST 1: HMM Forward Probabilities Causality (predict_forward_proba)
# -----------------------------------------------------------------------------
log("\n--- Test 1: HMM Forward Probabilities Causality ---")
df = generate_test_ohlcv(n_rows=600, seed=123)
detector = RegimeDetector(n_states=3, lookback=100)
detector.fit(df.iloc[:300])

obs_full = detector._prepare_observations(df)

proba_350 = detector.predict_forward_proba(obs_full[:350])
proba_400 = detector.predict_forward_proba(obs_full[:400])
proba_500 = detector.predict_forward_proba(obs_full[:500])
proba_600 = detector.predict_forward_proba(obs_full[:600])

diff_350_400 = float(np.max(np.abs(proba_350 - proba_400[:350])))
diff_350_500 = float(np.max(np.abs(proba_350 - proba_500[:350])))
diff_350_600 = float(np.max(np.abs(proba_350 - proba_600[:350])))
diff_400_600 = float(np.max(np.abs(proba_400 - proba_600[:400])))

log(f"Max diff T=350 vs T=400 (first 350 rows): {diff_350_400:.18e}")
log(f"Max diff T=350 vs T=500 (first 350 rows): {diff_350_500:.18e}")
log(f"Max diff T=350 vs T=600 (first 350 rows): {diff_350_600:.18e}")
log(f"Max diff T=400 vs T=600 (first 400 rows): {diff_400_600:.18e}")

test1_pass = (diff_350_400 < 1e-12) and (diff_350_500 < 1e-12) and (diff_350_600 < 1e-12) and (diff_400_600 < 1e-12)
log(f"RESULT Test 1 (HMM Causality): {'PASS' if test1_pass else 'FAIL'}")

# -----------------------------------------------------------------------------
# TEST 2: Label Creation 1-Candle Expiry Alignment with BinarySimulator
# -----------------------------------------------------------------------------
log("\n--- Test 2: Label Creation 1-Candle Expiry Alignment with BinarySimulator ---")

test2_failures = []
seeds = [42, 100, 2026, 999]

for s in seeds:
    df_test = generate_test_ohlcv(n_rows=300, seed=s)
    signals = pd.Series(index=df_test.index, dtype=object)
    np.random.seed(s)
    choices = np.random.choice(['CALL', 'PUT', None], size=len(df_test), p=[0.2, 0.2, 0.6])
    signals.iloc[:] = choices

    for label_func_name, label_func in [('optimizer_grid_search', create_labels_grid), ('run_backtest_comparison', create_labels_comp)]:
        labels = label_func(df_test, signals, expiry_candles=1)
        # Use large capital so simulator does not run out of capital mid-dataframe
        sim_res = BinarySimulator().run(df_test, signals, expiry_candles=1, payout=0.85, initial_capital=1e9, tie_rule='RETURN_STAKE')

        sim_trades = {t['index']: t for t in sim_res['trades']}

        for sig_idx in labels.index:
            label_val = labels.loc[sig_idx]
            if sig_idx not in sim_trades:
                test2_failures.append(f"Signal index {sig_idx} in labels but not in simulator trades")
                continue
            
            trade = sim_trades[sig_idx]
            sim_result = trade['result']
            expected_label = 1.0 if sim_result == 'WIN' else 0.0

            if label_val != expected_label:
                test2_failures.append(
                    f"Mismatch at idx {sig_idx} ({label_func_name}): label={label_val}, sim_result={sim_result}, expected={expected_label}"
                )

            entry_p = df_test.iloc[sig_idx + 1]['open']
            exit_p = df_test.iloc[sig_idx + 1]['close']
            sig_dir = signals.loc[sig_idx]
            diff = exit_p - entry_p

            if sig_dir == 'CALL':
                direct_win = 1.0 if diff > 1e-8 else 0.0
            else:
                direct_win = 1.0 if diff < -1e-8 else 0.0

            if label_val != direct_win:
                test2_failures.append(
                    f"Direct price mismatch at idx {sig_idx}: label={label_val}, direct_win={direct_win}, diff={diff}"
                )

log(f"Total Test 2 mismatches/failures: {len(test2_failures)}")
if test2_failures:
    for f in test2_failures[:5]:
        log(f"  FAIL DETAIL: {f}")
test2_pass = (len(test2_failures) == 0)
log(f"RESULT Test 2 (Label Expiry Alignment): {'PASS' if test2_pass else 'FAIL'}")

# -----------------------------------------------------------------------------
# TEST 3: Purged CV Embargo Eliminates IS/OOS Trade Overlap
# -----------------------------------------------------------------------------
log("\n--- Test 3: Purged CV Embargo Eliminates IS/OOS Trade Overlap ---")

test3_failures = []

for n_samples in [100, 500, 1000, 5000, 15000]:
    for expiry in [1, 2, 5, 10]:
        for embargo_pct in [0.01, 0.02, 0.05]:
            is_end, oos_start = PurgedGroupTimeSeriesSplit.purge_embargo_split(
                n_samples=n_samples, train_ratio=0.6, expiry_candles=expiry, embargo_pct=embargo_pct
            )

            raw_split = int(n_samples * 0.6)
            embargo_offset = max(1, int(n_samples * embargo_pct))

            max_is_trade_exit = (is_end - 1) + expiry if is_end > 0 else 0

            if is_end > 0 and max_is_trade_exit > raw_split:
                test3_failures.append(f"purge_embargo_split bleeding: max_is_trade_exit ({max_is_trade_exit}) > raw_split ({raw_split})")

            if oos_start < raw_split + embargo_offset:
                test3_failures.append(f"purge_embargo_split embargo violation: oos_start ({oos_start}) < raw_split + embargo ({raw_split + embargo_offset})")

            if is_end > 0 and oos_start < max_is_trade_exit:
                test3_failures.append(f"Overlap detected: oos_start {oos_start} < IS max exit {max_is_trade_exit}")

for n_samples in [200, 500, 1000]:
    for expiry in [1, 2, 5]:
        for embargo_pct in [0.01, 0.05]:
            cv = PurgedGroupTimeSeriesSplit(n_splits=5, expiry_candles=expiry, embargo_pct=embargo_pct)
            X_dummy = np.zeros((n_samples, 2))
            embargo_offset = int(n_samples * embargo_pct)

            for fold_idx, (train_idx, test_idx) in enumerate(cv.split(X_dummy)):
                test_start = min(test_idx)
                test_end = max(test_idx) + 1

                prior_train = train_idx[train_idx < test_start]
                if len(prior_train) > 0:
                    max_prior_train = max(prior_train)
                    trade_exit = max_prior_train + expiry
                    if trade_exit > test_start:
                        test3_failures.append(
                            f"Fold {fold_idx} prior trade overlap! max train={max_prior_train}, expiry={expiry}, exit={trade_exit}, test_start={test_start}"
                        )

                subsequent_train = train_idx[train_idx >= test_end]
                if len(subsequent_train) > 0:
                    min_subsequent_train = min(subsequent_train)
                    expected_min_train = test_end + max(embargo_offset, expiry)
                    if min_subsequent_train < expected_min_train:
                        test3_failures.append(
                            f"Fold {fold_idx} embargo violation! min subsequent train={min_subsequent_train} < expected {expected_min_train}"
                        )

log(f"Total Test 3 failures: {len(test3_failures)}")
if test3_failures:
    for f in test3_failures[:5]:
        log(f"  FAIL DETAIL: {f}")
test3_pass = (len(test3_failures) == 0)
log(f"RESULT Test 3 (Purged CV Embargo): {'PASS' if test3_pass else 'FAIL'}")

overall_pass = test1_pass and test2_pass and test3_pass
log("\n==========================================")
log(f"FINAL MILESTONE 2 VERDICT: {'PASS' if overall_pass else 'FAIL'}")
log("==========================================")
out_file.close()
