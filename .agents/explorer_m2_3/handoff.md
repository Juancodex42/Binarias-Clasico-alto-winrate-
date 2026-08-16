# Handoff Report: Milestone M2 Features 4 & 5 Technical Investigation

**Explorer Agent**: `explorer_m2_3`  
**Working Directory**: `c:/Users/juanc/Desktop/prueba/.agents/explorer_m2_3`  
**Date**: 2026-08-12  
**Target Features**:
- **Feature 4**: Integrate `PurgedGroupTimeSeriesSplit` into all optimization and split routines.
- **Feature 5**: Isolate multi-asset capital state tracking between IS and OOS periods in `engine/optimizer.py`.

---

## 1. Observation

Direct inspection of the codebase under `c:/Users/juanc/Desktop/prueba/` revealed the following observations regarding Purged CV integration and multi-asset IS/OOS capital isolation:

1. **Purged CV Integration Status (`engine/ml_engine/purged_cv.py`)**:
   - `PurgedGroupTimeSeriesSplit` provides `purge_embargo_split(n_samples, train_ratio, expiry_candles, embargo_pct)` (lines 15–27) returning `(is_end, oos_start)`, and `split(X, y=None, groups=None)` (lines 32–57) yielding purged/embargoed train/test folds.
   - `optimizer_grid_search.py` (lines 86–93): Successfully integrates `PurgedGroupTimeSeriesSplit.purge_embargo_split(n_samples=len(df), train_ratio=0.6, expiry_candles=expiry, embargo_pct=0.01)`.
   - `engine/optimizer.py` (`optimize_daily_confluence_stream`, lines 525–535): Successfully integrates `PurgedGroupTimeSeriesSplit.purge_embargo_split(n_samples=n_sym, train_ratio=0.70, expiry_candles=2, embargo_pct=0.01)` to pre-split `universe_data` into `universe_is` and `universe_oos`.
   - `run_backtest_comparison.py` (lines 64–72): Successfully integrates `PurgedGroupTimeSeriesSplit.purge_embargo_split`.
   - `engine/auto_tuner.py` (`WalkForwardEngine.run_wfa`, lines 35–41): Successfully integrates `PurgedGroupTimeSeriesSplit.purge_embargo_split` inside each rolling window.

2. **Unpurged Split Vulnerabilities Identified**:
   - `engine/auto_tuner.py` (`ParameterSurfaceAnalyzer.analyze_surface`, line 115): Uses `split_idx = int(len(df) * 0.60)` and `df_oos = df.iloc[split_idx:]` without purging trailing expiry candles or applying embargo offset.
   - `app.py` (lines 1024 & 1141): Uses naive `iloc[:int(len(df) * 0.7)]` slicing for universe correlation analysis and strategy tuning.

3. **Multi-Asset IS/OOS Capital State Tracking Isolation (`engine/optimizer.py`)**:
   - In `engine/optimizer.py` (`optimize_daily_confluence_stream`, lines 525–605), `universe_data` is split into `universe_is` and `universe_oos` BEFORE simulation.
   - `sim.run_multi_asset` is executed twice as independent method calls:
     - `sim_res_is = sim.run_multi_asset(universe_data=universe_is, signals_by_pair=signals_is, initial_capital=1000.0, ...)` (lines 581–591)
     - `sim_res_oos = sim.run_multi_asset(universe_data=universe_oos, signals_by_pair=signals_oos, initial_capital=1000.0, ...)` (lines 595–605)
   - In `BinarySimulator.run_multi_asset()` (`engine/simulator.py`, lines 240–440), all capital allocation state variables (`safe_core`, `bullets`, `risk_cap`, `consecutive_wins_by_pair`, `base_capital_by_pair`, `classes_executed_by_day`) are local variables initialized at the start of each invocation. Calling `run_multi_asset` on `universe_oos` starts with a fresh $1000.0$ capital base, isolated from IS profits/losses.

4. **Capital State Spillover Vulnerability in UI Layer (`app.py`)**:
   - In `app.py` (lines 1199–1210), `sim_res = simulator.run_multi_asset(universe_data=filtered_universe_data, ...)` evaluates OOS by running a single pass over the unsegmented full dataset (`filtered_universe_data`), causing IS capital accumulation (`safe_core` & streak counters) to carry over into OOS evaluation.

5. **Unit Test Execution Verification**:
   - Running `pytest tests/test_tier1_feature_coverage.py -k "TestFeature10 or TestFeature11" -v` executed 9 unit tests targeting Features 10 & 11, with **all 9 tests passing cleanly**:
     - `test_f10_purged_cv_split_count` PASSED
     - `test_f10_purged_cv_indices_structure` PASSED
     - `test_f10_purge_window_exclusion` PASSED
     - `test_f10_embargo_window_exclusion` PASSED
     - `test_f10_no_train_test_overlap` PASSED
     - `test_f11_simulator_is_oos_capital_independence` PASSED
     - `test_f11_multi_asset_capital_split_isolation` PASSED
     - `test_f11_reinvestment_mode_isolation` PASSED
     - `test_f11_equity_curve_starting_point` PASSED

---

## 2. Logic Chain

1. **Purged CV Integration Logic Chain (Feature 4)**:
   - *Premise*: Standard train/test splits without purging allow trades initiated near the end of training set to expire during the test set, creating look-ahead target leakage. Lack of embargo allows serial correlation spillover between adjacent candles across the split boundary.
   - *Observation*: `purged_cv.py` defines `purge_embargo_split()` which computes `is_end = max(0, raw_split - expiry_candles)` and `oos_start = min(n_samples, raw_split + embargo_offset)`. Primary optimization scripts (`optimizer_grid_search.py`, `engine/optimizer.py`, `run_backtest_comparison.py`, `WalkForwardEngine`) correctly call `purge_embargo_split()`.
   - *Observation*: `ParameterSurfaceAnalyzer.analyze_surface` (`engine/auto_tuner.py`:115) and `app.py` (:1024, :1141) still contained unpurged `iloc[:int(len(df) * ratio)]` slicing.
   - *Conclusion*: Replacing naive `iloc` slicing in `ParameterSurfaceAnalyzer` and `app.py` with `PurgedGroupTimeSeriesSplit.purge_embargo_split()` guarantees 100% codebase compliance with Feature 4.

2. **IS/OOS Capital State Tracking Isolation Logic Chain (Feature 5)**:
   - *Premise*: Multi-asset trading strategies in `BinarySimulator.run_multi_asset()` track stateful capital variables (`safe_core` vault, active `bullets` capital, consecutive win counters). If simulation runs on full IS+OOS data in a single invocation, initial OOS trades execute using capital accrued during IS.
   - *Observation*: In `engine/optimizer.py` (`optimize_daily_confluence_stream`), lines 525–535 partition `universe_data` into `universe_is` and `universe_oos`. Lines 581–605 execute `sim.run_multi_asset()` separately for `universe_is` and `universe_oos`.
   - *Observation*: Local scope initialization inside `run_multi_asset()` guarantees that calling `sim.run_multi_asset(universe_oos, ...)` resets `safe_core`, `bullets`, and pair streak counters to fresh initial state ($1000.0$).
   - *Observation*: Unit tests `test_f11_simulator_is_oos_capital_independence` and `test_f11_multi_asset_capital_split_isolation` verify this behavior and pass with 0 errors.
   - *Conclusion*: Capital state tracking between IS and OOS is fully isolated in `engine/optimizer.py`. A diff is formulated for `app.py` to fix single-pass OOS evaluation.

---

## 3. Caveats

- **Read-Only Exploration Mandate**: In compliance with Explorer role constraints, no direct modifications were applied to project source files. Diffs are formatted in `analysis.md` for implementation by the parent orchestrator or implementer agent.
- **`app.py` Interface Scope**: `app.py` serves as the Web GUI backend. While `engine/optimizer.py` is the primary algorithmic optimization engine, updating `app.py` ensures user-facing optimizations share the identical zero-leakage guarantee.

---

## 4. Conclusion

1. **Feature 4 Assessment**: `PurgedGroupTimeSeriesSplit` is properly implemented in `engine/ml_engine/purged_cv.py` and integrated into all primary optimization routines (`optimizer_grid_search.py`, `engine/optimizer.py`, `run_backtest_comparison.py`, `WalkForwardEngine`). Two localized naive splits in `engine/auto_tuner.py` (`ParameterSurfaceAnalyzer`) and `app.py` have been identified with exact diff proposals.
2. **Feature 5 Assessment**: Multi-asset capital state tracking between IS and OOS periods in `engine/optimizer.py` (`optimize_daily_confluence_stream`) is completely isolated. `sim.run_multi_asset()` runs on pre-split `universe_is` and `universe_oos` datasets with fresh capital initialization ($1000.0$), eliminating IS trajectory spillover.

---

## 5. Verification Method

To independently verify these findings:

1. **Run Unit Tests for Features 10 & 11**:
   ```bash
   pytest tests/test_tier1_feature_coverage.py -k "TestFeature10 or TestFeature11" -v
   ```
   *Expected Output*: 9 passed, 0 failed.

2. **Inspect Pre-Splitting and Capital Isolation in `engine/optimizer.py`**:
   - View `engine/optimizer.py` lines 525–535: verify `PurgedGroupTimeSeriesSplit.purge_embargo_split` partitions `universe_data` into `universe_is` and `universe_oos`.
   - View `engine/optimizer.py` lines 581–605: verify `sim.run_multi_asset` is called separately on `universe_is` and `universe_oos` with `initial_capital=1000.0`.

3. **Inspect `ParameterSurfaceAnalyzer` in `engine/auto_tuner.py`**:
   - View line 115 of `engine/auto_tuner.py` to check for `split_idx = int(len(df) * 0.60)` and apply proposed Diff 1.
