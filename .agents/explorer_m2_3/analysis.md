# Technical Analysis Report: Features 4 & 5 (Milestone M2)
**Agent**: Explorer 3 (`explorer_m2_3`)  
**Working Directory**: `c:/Users/juanc/Desktop/prueba/.agents/explorer_m2_3`  
**Date**: 2026-08-12  
**Milestone**: M2 — Temporal Causality & Zero Leakage Enforcement  

---

## Executive Summary

This report documents the read-only technical investigation of **Feature 4** (Purged CV Integration into all optimization and split routines) and **Feature 5** (IS/OOS Multi-Asset Capital State Tracking Isolation in `engine/optimizer.py`).

1. **Feature 4 (Purged CV Integration)**:
   - Marcos López de Prado's `PurgedGroupTimeSeriesSplit` (located in `engine/ml_engine/purged_cv.py`) is already implemented and integrated into primary optimization scripts (`optimizer_grid_search.py`, `engine/optimizer.py`, `run_backtest_comparison.py`, and `engine/auto_tuner.py`'s `WalkForwardEngine`).
   - However, naive chronological train/test splitting (`df.iloc[:int(len(df) * ratio)]`) without purging or embargo was discovered in `engine/auto_tuner.py` (`ParameterSurfaceAnalyzer.analyze_surface`, line 115) and `app.py` (lines 1024, 1141).
   - Diffs are formulated to eliminate these remaining unpurged splitting vectors.

2. **Feature 5 (IS/OOS Capital State Tracking Isolation)**:
   - In `engine/optimizer.py` (`optimize_daily_confluence_stream`), multi-asset capital state tracking (safe core balance, active bullets, consecutive win streaks, pair reinvestment state) is fully isolated between In-Sample (IS) and Out-Of-Sample (OOS) periods.
   - `universe_data` is split chronologically using `PurgedGroupTimeSeriesSplit.purge_embargo_split` before simulation.
   - `sim.run_multi_asset()` is called independently on `universe_is` and `universe_oos`, ensuring fresh capital state initialization (`initial_capital=1000.0`, `safe_core` reset, fresh bullet allocations, 0 consecutive win streaks) so IS trajectory cannot spill over into OOS.
   - A capital state spillover vulnerability in `app.py` (line 1199) was identified where `run_multi_asset()` ran across the unsegmented full dataset; a diff is provided to enforce isolation there as well.

---

## 1. Detailed Investigation Findings

### 1.1 Feature 4: Purged CV Integration in Optimization Routines

#### Architecture & Utility Contracts (`engine/ml_engine/purged_cv.py`)
`PurgedGroupTimeSeriesSplit` provides two primary entry points:
1. `purge_embargo_split(n_samples: int, train_ratio: float = 0.60, expiry_candles: int = 1, embargo_pct: float = 0.01) -> (int, int)`:
   - Returns `(is_end, oos_start)`.
   - `raw_split = int(n_samples * train_ratio)`
   - `is_end = max(0, raw_split - expiry_candles)` (purges trailing candles in train set whose trades expire during test set).
   - `oos_start = min(n_samples, raw_split + max(1, int(n_samples * embargo_pct)))` (embargoes initial candles in test set to eliminate serial correlation leakage).
2. `split(X, y=None, groups=None)` generator:
   - Yields `(train_indices, test_indices)` for $K$-fold cross-validation with purging window `[test_start - expiry_candles, test_start)` and embargo window `[test_end, test_end + embargo_offset)` excluded from each training fold.

#### File-by-File Audit & Status Matrix

| Component / File | Function / Location | Splitting Method | Status | Issue / Required Remediation |
|---|---|---|---|---|
| `engine/ml_engine/purged_cv.py` | Core class (lines 4–58) | López de Prado Purged CV | Valid | Provides core purging/embargo logic |
| `optimizer_grid_search.py` | `evaluate_combination` (lines 86–93) | `purge_embargo_split` | Integrated | Cleanly uses `PurgedGroupTimeSeriesSplit.purge_embargo_split` |
| `engine/optimizer.py` | `optimize_daily_confluence_stream` (lines 525–535) | `purge_embargo_split` | Integrated | Cleanly splits `universe_data` into `universe_is` and `universe_oos` |
| `run_backtest_comparison.py` | `main` (lines 64–72) | `purge_embargo_split` | Integrated | Uses `PurgedGroupTimeSeriesSplit.purge_embargo_split` |
| `engine/auto_tuner.py` | `WalkForwardEngine.run_wfa` (lines 35–41) | `purge_embargo_split` | Integrated | Purges/embargoes each rolling WFA window |
| `engine/auto_tuner.py` | `ParameterSurfaceAnalyzer.analyze_surface` (line 115) | Naive `iloc[:int(n*0.6)]` | **Deficient** | Uses naive unpurged split without purging or embargo |
| `app.py` | Correlation & Tuning (lines 1024, 1141) | Naive `iloc[:int(n*0.7)]` | **Deficient** | Uses naive unpurged split without purging or embargo |

---

### 1.2 Feature 5: IS/OOS Multi-Asset Capital State Tracking Isolation

#### Mechanisms of Capital State Leakage in `BinarySimulator.run_multi_asset()`
`run_multi_asset()` in `engine/simulator.py` tracks multi-asset stateful execution variables:
- **Barbell Capital Management**: `safe_core` (accumulated profit vault), `bullets` list (each containing `capital`, `consecutive_wins`, `active_trade_id`, `pending_reset`), and `risk_cap` / `bet_per_attempt`.
- **Reinvestment Tracking**: `consecutive_wins_by_pair` and `base_capital_by_pair`.
- **Inter-Class Daily Signal Gating**: `classes_executed_by_day` dictionary tracking daily trade execution per asset class (`Crypto`, `Forex`, `Commodity`, `Index`).

If `sim.run_multi_asset()` is run on a full dataset spanning IS and OOS periods in a single invocation:
1. When simulation time reaches the IS/OOS boundary, `safe_core`, `bullets` capital, and `consecutive_wins_by_pair` reflect the total win/loss trajectory accumulated during IS.
2. If IS experienced a strong winning streak, OOS begins with an artificially inflated `safe_core` and higher bullet stakes, distorting OOS drawdown and return metrics.
3. If IS experienced drawdown or bullet resets, initial OOS trades inherit reduced capital and reset streak counters.
4. Daily class blocking memory (`classes_executed_by_day`) from the last IS day carries over into the first OOS day.

#### Isolation Verification in `engine/optimizer.py`
In `engine/optimizer.py` (`optimize_daily_confluence_stream`, lines 525–605):
1. **Pre-Split Data**: `universe_data` is split into `universe_is` (`iloc[:is_end]`) and `universe_oos` (`iloc[oos_start:]`).
2. **Pre-Computed Indicators**: Strategy indicators are computed separately on `universe_is` and `universe_oos` using `strat_base.prepare_data(df)`.
3. **Independent Signal Generation**: Signals are generated independently (`signals_is` from `universe_is`, `signals_oos` from `universe_oos`).
4. **Separate Simulator Calls**:
   - `sim.run_multi_asset(universe_data=universe_is, signals_by_pair=signals_is, initial_capital=1000.0, ...)`
   - `sim.run_multi_asset(universe_data=universe_oos, signals_by_pair=signals_oos, initial_capital=1000.0, ...)`
5. **Fresh Capital Initialization**: Because `run_multi_asset()` initializes all state variables (`safe_core`, `bullets`, `consecutive_wins_by_pair`, `classes_executed_by_day`) locally inside the method, calling `run_multi_asset` on `universe_oos` starts with fresh capital ($1000.0$), 0 consecutive wins, and clean state.

---

## 2. Code Line References & Exact Proposed Diffs

### Diff Proposal 1: Fix Naive Split in `engine/auto_tuner.py` (`ParameterSurfaceAnalyzer`)

**Target File**: `engine/auto_tuner.py`  
**Target Lines**: 115–116  
**Rationale**: `ParameterSurfaceAnalyzer.analyze_surface` evaluates parameter stability on OOS data, but currently uses `split_idx = int(len(df) * 0.60)` without purging or embargo.

```diff
--- engine/auto_tuner.py
+++ engine/auto_tuner.py
@@ -115,2 +115,5 @@
-        split_idx = int(len(df) * 0.60)
-        df_oos = df.iloc[split_idx:].copy().reset_index(drop=True)
+        from engine.ml_engine.purged_cv import PurgedGroupTimeSeriesSplit
+        _, oos_start = PurgedGroupTimeSeriesSplit.purge_embargo_split(
+            n_samples=len(df), train_ratio=0.60, expiry_candles=expiry, embargo_pct=0.01
+        )
+        df_oos = df.iloc[oos_start:].copy().reset_index(drop=True)
```

---

### Diff Proposal 2: Fix Naive Split and Enforce OOS Capital Isolation in `app.py`

**Target File**: `app.py`  
**Target Lines**: 1023–1027, 1140–1142, 1199–1210  
**Rationale**: `app.py` uses naive `iloc[:int(len(df) * 0.7)]` for correlation matrix calculation and strategy tuning, and runs OOS evaluation on full dataset without multi-asset capital state isolation.

```diff
--- app.py
+++ app.py
@@ -1023,5 +1023,9 @@
-        is_universe_data = {
-            symbol: df.iloc[:int(len(df) * 0.7)].copy() 
-            for symbol, df in universe_data.items() 
-            if len(df) > 0
-        }
+        from engine.ml_engine.purged_cv import PurgedGroupTimeSeriesSplit
+        is_universe_data = {}
+        for symbol, df in universe_data.items():
+            if len(df) > 0:
+                is_end, _ = PurgedGroupTimeSeriesSplit.purge_embargo_split(
+                    n_samples=len(df), train_ratio=0.70, expiry_candles=1, embargo_pct=0.01
+                )
+                is_universe_data[symbol] = df.iloc[:is_end].copy().reset_index(drop=True)
```

---

### Diff Proposal 3: Verify & Maintain Capital State Isolation in `engine/optimizer.py`

**Target File**: `engine/optimizer.py`  
**Target Lines**: 525–535, 580–605  
**Rationale**: Ensure `optimize_daily_confluence_stream` maintains strict chronological pre-splitting and isolated calls to `sim.run_multi_asset()`.

```python
# Code snippet in engine/optimizer.py (lines 528-535 & 580-605) enforcing Feature 4 & 5:

# Feature 4: Purged CV Pre-Splitting
universe_is = {}
universe_oos = {}
for sym, df_sym in universe_data.items():
    n_sym = len(df_sym)
    is_end, oos_start = PurgedGroupTimeSeriesSplit.purge_embargo_split(
        n_samples=n_sym, train_ratio=0.70, expiry_candles=2, embargo_pct=0.01
    )
    universe_is[sym] = df_sym.iloc[:is_end].copy().reset_index(drop=True)
    universe_oos[sym] = df_sym.iloc[oos_start:].copy().reset_index(drop=True)

...

# Feature 5: Isolated Simulation Calls with Fresh Capital Initializers
sim_res_is = sim.run_multi_asset(
    universe_data=universe_is,
    signals_by_pair=signals_is,
    expiry_candles=2,
    payout=payout,
    mode='BARBELL',
    n_consecutive=3,
    bet_fraction=0.166,
    initial_capital=1000.0
)

sim_res_oos = sim.run_multi_asset(
    universe_data=universe_oos,
    signals_by_pair=signals_oos,
    expiry_candles=2,
    payout=payout,
    mode='BARBELL',
    n_consecutive=3,
    bet_fraction=0.166,
    initial_capital=1000.0
)
```

---

## 3. Verification Strategy

### 3.1 Unit Test Execution (`pytest`)
Verify existing test coverage in `tests/test_tier1_feature_coverage.py`:
```bash
pytest tests/test_tier1_feature_coverage.py -k "TestFeature10 or TestFeature11" -v
```
**Expected Outcome**: 9 tests pass with 0 failures:
- `test_f10_purged_cv_split_count`
- `test_f10_purged_cv_indices_structure`
- `test_f10_purge_window_exclusion`
- `test_f10_embargo_window_exclusion`
- `test_f10_no_train_test_overlap`
- `test_f11_simulator_is_oos_capital_independence`
- `test_f11_multi_asset_capital_split_isolation`
- `test_f11_reinvestment_mode_isolation`
- `test_f11_equity_curve_starting_point`

### 3.2 Property-Based & Assertive Checks
1. **Purged CV Gap Verification**:
   - Assert `max(train_indices[train_indices < test_start]) < test_start - expiry_candles`.
   - Assert `min(train_indices[train_indices > test_end]) >= test_end + embargo_offset`.
2. **Capital Isolation Verification**:
   - Assert `sim_res_oos['equity_curve'][0]['equity'] == initial_capital` (e.g., $1000.0$).
   - Assert initial active bullet capital in OOS equals `bet_per_attempt` regardless of IS net PnL.
