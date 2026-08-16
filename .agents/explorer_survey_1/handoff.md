# Survey Handoff Report: Quantitative Strategy Engine Architecture & Integrity Audit

**Explorer Agent**: `explorer_survey_1`  
**Working Directory**: `c:/Users/juanc/Desktop/prueba/.agents/explorer_survey_1`  
**Date**: 2026-08-12  

---

## 1. Observation

Direct code examination of the quantitative engine architecture under `c:/Users/juanc/Desktop/prueba/` revealed 11 distinct software bugs, look-ahead biases, data leakage risks, and logic flaws across `engine/` and `strategies/`.

### Summary of Observed Flaws & Exact Code References

| # | Component / File | Location (Lines) | Category | Description / Verbatim Excerpt |
|---|------------------|------------------|----------|--------------------------------|
| 1 | `engine/simulator.py` | 502–553 | State Corruption | **Barbell Bullet Reset Overwrite**: When a campaign completion or reset occurs, in-flight bullets get `pending_reset = True`. When an in-flight bullet exits as a `WIN`: line 502 adds win PnL (`bullet['capital'] += pnl`), line 503 increments wins (`bullet['consecutive_wins'] += 1`), BUT line 549 immediately executes `bullet['capital'] = bullet.pop('next_capital', bet_per_attempt)` and `bullet['consecutive_wins'] = 0`, wiping out the winning PnL and streak increment. |
| 2 | `engine/simulator.py` | 309–312, 481–494, 588 | Disconnect / Schema | **Multi-Asset Tie Rule Handling**: In `run_multi_asset()`, ties return early inside `if is_tie` (line 481), but for non-ties, exit handling hardcodes `'result': 'WIN' if is_win else 'LOSS'` at line 588, creating duplicate trade record formatting paths and potential discrepancy when `tie_rule == 'LOSS'`. |
| 3 | `strategies/volatility_squeeze_ml.py` | 110–112 | Data Leakage | **Global Quantile Feature Clipping**: `q01 = features[col].quantile(0.01)` and `q99 = features[col].quantile(0.99)` calculate outlier bounds across the entire dataset in `prepare_data(df)`. |
| 4 | `engine/auto_tuner.py` | 189 | Look-Ahead Bias | **Global Median in Dynamic Regime Adapter**: `hist_atr_median = atr_14.median()` computes the median of the entire ATR series across the full backtest horizon in `detect_regime(df)`. |
| 5 | `strategies/genetic_composite.py` & `engine/exporter.py` | 181 & 421 | Data Leakage | **Full-Sample Quantile Fallback**: `squeeze_active = bb_width <= rolling_q30.fillna(bb_width.quantile(0.30))` uses `bb_width.quantile(0.30)` calculated over the entire time series to fill initial rolling NaNs. |
| 6 | `engine/optimizer.py` | 561–595 | State Contamination | **Full-Sample Simulation & Post-Hoc Split**: `sim.run_multi_asset()` runs over full multi-year `universe_data` in `optimize_daily_confluence_stream`, and trades are then filtered into `trades_is` and `trades_oos` based on `split_time`. In Barbell/Reinvestment mode, initial OOS capital and bullet states depend on IS trade history. |
| 7 | `engine/ml_engine/regime_detector.py` | 88, 133 | Look-Ahead Bias | **Viterbi Sequence Decoding in HMM**: `self.model.predict(obs)` decodes state sequences via Viterbi algorithm over the entire observation matrix `obs`, incorporating future observations ($O_{t+1}, \dots, O_T$) to determine state $S_t$. |
| 8 | `engine/ml_engine/cusum_monitor.py` | 73–108 | Pause Deadlock | **CUSUM Permanent Pause Deadlock**: When `should_trade()` returns `False` during `PAUSE`, strategy execution stops. If `update()` is only called when trades occur, no new trades are passed to `update()`, locking the system in `PAUSE` indefinitely. |
| 9 | `engine/auto_tuner.py` | 41–78 | Logic Flaw | **`WalkForwardEngine` Missing In-Sample Optimization**: `run_wfa` evaluates fixed `base_params` across rolling windows rather than optimizing parameters on each IS window and testing the winning set OOS. |
| 10 | `engine/ml_engine/meta_filter.py` | 73–85 | Redundant Code | **Last-Signal Threshold Mutation**: `filter_signals` evaluates NATR adaptive threshold using `target_idx = active_indices[-1]` (the last signal in the dataset) before looping through signals, redundantly mutating `self.probability_threshold` globally. |
| 11 | `engine/ml_engine/feature_extractor.py` | 88–99 | Performance Bottleneck | **Non-Vectorized Hurst Exponent Callback**: `returns.rolling(30).apply(calc_hurst, raw=True)` invokes a Python function `calc_hurst` per row, creating a massive execution bottleneck on large datasets. |

---

## 2. Logic Chain

### 2.1 State Corruption Logic Chain (Observation 1)
1. **Observation**: In `engine/simulator.py` (lines 507–553), when bullet 0 completes a winning streak of length `n_consecutive`, it triggers `if bullet['consecutive_wins'] >= n_consecutive:`.
2. **Step**: The engine marks all currently active (in-flight) bullets with `b['pending_reset'] = True` and `b['next_capital'] = bet_per_attempt`.
3. **Step**: Bullet 1 (which was in-flight) finishes its trade later as a **WIN**.
4. **Step**: The code enters `if is_win:` block for Bullet 1, executing:
   - Line 501: `pnl = bet_size * payout`
   - Line 502: `bullet['capital'] += pnl`
   - Line 503: `bullet['consecutive_wins'] += 1`
   - Line 504: `bullet['active_trade_id'] = None`
5. **Step**: At the end of the exit processing (line 549), the code checks `if bullet.get('pending_reset'):`. Since `pending_reset` was `True`, it runs:
   - `bullet['capital'] = bullet.pop('next_capital', bet_per_attempt)`
   - `bullet['consecutive_wins'] = 0`
   - `bullet['pending_reset'] = False`
6. **Conclusion**: The PnL earned by Bullet 1's winning trade is completely overwritten and replaced by `bet_per_attempt`, and its consecutive win counter is reset to 0. This corrupts capital tracking and destroys valid win streaks in multi-asset simulation.

### 2.2 Data Leakage & Look-Ahead Bias Logic Chain (Observations 3, 4, 5, 7)
1. **Observation (Obs 3)**: In `strategies/volatility_squeeze_ml.py` line 110–112, `features[col].quantile(0.01)` and `quantile(0.99)` are calculated on `features` in `prepare_data(df)`.
2. **Step**: The quantiles $q_{0.01}$ and $q_{0.99}$ use all rows from index 0 to $N-1$ of the input DataFrame.
3. **Conclusion**: Feature values at candle $t=10$ are clipped using threshold values determined by market volatility at candle $t=1000$. This leaks future distributional information into past feature representations.

4. **Observation (Obs 4)**: In `engine/auto_tuner.py` line 189, `hist_atr_median = atr_14.median()` computes the global median of the ATR series across the entire input DataFrame `df`.
5. **Step**: In `detect_regime(df)`, `vol_q = current_atr / hist_atr_median`.
6. **Conclusion**: The volatility quantile calculation at any historical bar $t$ compares current ATR to the median ATR of the entire dataset (including future bars). This is a direct look-ahead bias.

7. **Observation (Obs 7)**: In `engine/ml_engine/regime_detector.py` lines 88 and 133, `states = self.model.predict(obs)` is called on `obs`.
8. **Step**: `GaussianHMM.predict()` from `hmmlearn` executes Viterbi sequence decoding, which computes the global optimal state path $\arg\max_S P(S | O_1, \dots, O_T)$ using dynamic programming across the complete sequence $O_1 \dots O_T$.
9. **Conclusion**: The decoded state $S_t$ at bar $t$ is conditioned on future observations $O_{t+1}, \dots, O_T$. Real-time regime filtering requires forward-only probability filtering ($P(S_t | O_1, \dots, O_t)$).

### 2.3 Capital State Contamination Logic Chain (Observation 6)
1. **Observation**: In `engine/optimizer.py` line 561, `sim.run_multi_asset()` is called with `universe_data` containing the full history. Then lines 577–578 split trades into `trades_is` and `trades_oos` based on `split_time`.
2. **Step**: In `run_multi_asset()`, `safe_core`, `bullets`, `risk_cap`, and streak counters are continuously modified as trades complete.
3. **Step**: When the simulation crosses `split_time`, the initial capital and active bullet state of the first OOS trade are direct results of the wins/losses accumulated during IS.
4. **Conclusion**: Out-Of-Sample performance metrics depend on In-Sample trajectory, violating IS/OOS capital isolation (Feature #11 in `PROJECT.md`).

---

## 3. Caveats

- **Rust Genetic Engine**: The Rust source files in `engine/genetic_optimizer/src` were not modified during this survey. They use FFI bindings; any Rust-level modifications would require a `cargo build` pass.
- **External Data Dependencies**: Historical CSV files in `data/raw/` contain varying timestamp formats (10-digit unix seconds vs 13-digit milliseconds). All timestamp conversion logic must remain resilient to both formats.
- **No Code Implementation Executed**: Per the Read-Only Explorer mandate, no bug fixes were committed to source files during this task. All identified flaws are documented for remediation in Milestone M1/M2.

---

## 4. Conclusion

The quantitative engine architecture is mathematically sophisticated and features advanced concepts (FFD, HMM regime gating, CUSUM drift detection, Barbell capital allocation, and Purged CV). However, **critical software bugs and data leakage vulnerabilities currently invalidate backtest reliability and Out-Of-Sample performance claims**.

### Priority Remediation Plan

1. **M1 (Core Software Integrity)**:
   - Fix Barbell bullet reset overwrite in `engine/simulator.py` (lines 502–553).
   - Unify single-asset and multi-asset tie rule handling in `engine/simulator.py`.
   - Resolve CUSUM monitor paper-trading update contract in `engine/ml_engine/cusum_monitor.py`.
   - Upgrade `WalkForwardEngine` in `engine/auto_tuner.py` to perform true In-Sample parameter tuning per fold.

2. **M2 (Zero-Leakage & Temporal Causality)**:
   - Replace global `.quantile()` clipping in `strategies/volatility_squeeze_ml.py` with rolling/in-sample quantile scalers.
   - Replace global `atr_14.median()` in `engine/auto_tuner.py` with rolling median `atr_14.rolling(window).median()`.
   - Replace Viterbi `predict()` in `engine/ml_engine/regime_detector.py` with forward-only filtered state probabilities.
   - Enforce independent capital state initialization between IS and OOS splits in `engine/optimizer.py`.

---

## 5. Verification Method

To independently verify all findings and validate fixes once implemented:

### Command Line Verification
Run the standard unit test suite:
```bash
pytest tests/ -v
pytest test_high_winrate_mechanisms.py -v
```

### Direct Inspection Checks
1. **Barbell Bullet Reset**: Run `pytest tests/test_simulator_integrity.py` or inspect `engine/simulator.py` around line 549 to verify that `bullet['capital']` is not overwritten after a winning trade when `pending_reset` is True.
2. **Data Leakage Inspection**:
   - Check `strategies/volatility_squeeze_ml.py`: ensure no call to `features[col].quantile()` on full DataFrame.
   - Check `engine/auto_tuner.py`: ensure `hist_atr_median` uses `.rolling().median()`.
   - Check `engine/ml_engine/regime_detector.py`: ensure HMM state prediction uses forward filtering rather than `model.predict()`.
3. **Zero Cheating Audit Script**:
   - Execute `python scratch/audit_zero_cheating.py` to verify strict temporal causality across all feature extractors and signal generators.
