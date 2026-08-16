# Survey Report: Optimization Framework, Search Space, and Quantitative Causality/Robustness

**Agent**: `teamwork_preview_explorer_survey_2`  
**Date**: 2026-08-12  
**Target Workspace**: `c:\Users\juanc\Desktop\prueba`  
**Scope**: Optimization Framework, Parameter Search Space, Hyperparameters, Market Regimes, Meta-Filters, Temporal Causality, Data Leakage Prevention, and Walk-Forward Validation.

---

## Executive Summary

An exhaustive read-only inspection was conducted across the optimization framework, hyperparameter search scripts, strategy configuration modules, machine learning meta-filters, and backtesting engines in the workspace.

Key findings:
1. **Temporal Causality Violations & Data Leakage**: Critical quantitative bugs were discovered, including target label shift mismatch for binary contract expiration (`shift(-2)` vs 1-candle expiry simulation), global feature quantile clipping before splitting, adaptive threshold evaluation using end-of-series `.iloc[-1]` indexing and global test medians, global Viterbi sequence decoding in HMM regime detection, and retroactive capital state pollution across train/test splits.
2. **Search Space Limitations & Missing Optimization Mechanisms**: The current search space relies on fixed, narrow grid searches (45 to 360 combinations) and a Rust genetic algorithm with hardcoded genome constraints. Optuna (TPE, CMA-ES, Bayesian optimization) is completely missing. Walk-forward optimization is mocked (evaluating static parameters without in-sample tuning).
3. **Omission of Purged Cross-Validation**: `PurgedGroupTimeSeriesSplit` (purging & embargo) is defined in `engine/ml_engine/purged_cv.py` but is unused in all optimization routines, leading to label overlap leakage across splits.
4. **Performance Bottlenecks**: Serial Python loops in `BinarySimulator.run`, repeated un-cached indicator calculations, and subprocess JSON serialization overhead restrict high-dimensional search space exploration.

---

## 1. Observation

### Observation 1.1: Target Label Expiry Shift Mismatch Between Optimization Labeler and Simulator
- **File**: `optimizer_grid_search.py`, lines 47–50:
```python
def create_labels(df, signals, expiry_candles=1):
    entry_prices = df['open'].shift(-1)
    exit_prices = df['close'].shift(-(1 + expiry_candles))
```
- **File**: `engine/simulator.py`, lines 69–89:
```python
            exit_idx = entry_idx + expiry_candles
            ...
            if entry_idx + 1 < len(df):
                entry_price_raw = float(df.iloc[entry_idx + 1]['open'])
            ...
            exit_price = float(df.iloc[exit_idx]['close'])
```
In `create_labels`, when `expiry_candles=1`, `exit_prices = df['close'].shift(-(1 + 1))` sets the exit price to `df['close'].shift(-2)` (candle $i+2$ close). In contrast, `BinarySimulator.run` sets `exit_idx = entry_idx + 1` (candle $i+1$ close). As a result, ML meta-labelers and regime filters in `optimizer_grid_search.py` are trained on labels generated for a 2-candle expiration while being simulated on a 1-candle expiration.

### Observation 1.2: Global Quantile Feature Clipping Leakage in Feature Preparation
- **File**: `strategies/volatility_squeeze_ml.py`, lines 108–112:
```python
        # Clip extremes to prevent outlier-driven predictions
        for col in features.columns:
            q01 = features[col].quantile(0.01)
            q99 = features[col].quantile(0.99)
            features[col] = features[col].clip(q01, q99)
```
In `VolatilitySqueezeMLStrategy.prepare_data`, `features[col].quantile(0.01)` and `features[col].quantile(0.99)` are computed across the entire DataFrame `df` before any train/test split or walk-forward fold division. This causes future price and volume distributions to leak into feature clipping bounds.

### Observation 1.3: End-of-Series Indexing & Global Test Median Leakage in Adaptive Meta-Filter Thresholding
- **File**: `engine/ml_engine/meta_filter.py`, lines 69–77:
```python
        # Adaptive threshold: subir umbral cuando la volatilidad es alta
        if self.adaptive_threshold and 'natr' in X.columns:
            current_natr = X['natr'].iloc[-1] if len(X) > 0 else 0
            median_natr = X['natr'].median() if len(X) > 0 else 0
            if current_natr > median_natr * 1.5:
                self.probability_threshold = min(self.base_threshold + 0.10, 0.85)
            elif current_natr < median_natr * 0.5:
                self.probability_threshold = max(self.base_threshold - 0.05, 0.55)
            else:
                self.probability_threshold = self.base_threshold
```
In `BinaryMLMetaFilter.filter_signals`:
1. `current_natr = X['natr'].iloc[-1]` retrieves the *last* row of the entire DataFrame `X` (the end of the test set) and uses it to set `probability_threshold` for all trades in the series.
2. `median_natr = X['natr'].median()` computes the median NATR over the entire input DataFrame `X` (including future test observations).

### Observation 1.4: Global HMM Viterbi Sequence Decoding & Whole-Sample Standard Deviation Imputation
- **File**: `engine/ml_engine/regime_detector.py`, line 41, line 88, line 133:
```python
        feat_vol = returns.rolling(20).std().fillna(returns.std()).values
        ...
        states = self.model.predict(obs)
```
1. `GaussianHMM.predict(obs)` executes Viterbi decoding over the full observation matrix `obs`. Viterbi decoding is a global optimization algorithm that uses future observations $x_{t+1}, x_{t+2}, \dots, x_N$ to estimate the most likely state path at step $t$.
2. `fillna(returns.std())` uses the standard deviation of the full series `returns.std()` to fill initial NaN values.

### Observation 1.5: Dynamic Regime Adapter Global Median and Single End-Candle Evaluation
- **File**: `engine/auto_tuner.py`, lines 188–190:
```python
        current_atr = atr_14.iloc[-1]
        hist_atr_median = atr_14.median()
        vol_q = current_atr / hist_atr_median if hist_atr_median > 0 else 1.0
```
In `DynamicRegimeAdapter.detect_regime`:
1. `hist_atr_median = atr_14.median()` computes the median ATR over the entire DataFrame `df`.
2. `current_atr = atr_14.iloc[-1]` accesses only the final row of `df` to classify the regime.

### Observation 1.6: Retroactive Capital State Pollution Across In-Sample and Out-Of-Sample Trades
- **File**: `engine/optimizer.py`, lines 561–580:
```python
                    if signals_by_pair:
                        sim_res = sim.run_multi_asset(
                            universe_data=universe_data,
                            signals_by_pair=signals_by_pair,
                            expiry_candles=2,
                            payout=payout,
                            mode='BARBELL',
                            n_consecutive=3,
                            bet_fraction=0.166
                        )

                        trades = sim_res.get('trades', [])
                        if len(trades) > 0:
                            min_time = min(t['time'] for t in trades)
                            max_time = max(t['time'] for t in trades)
                            split_time = min_time + 0.7 * (max_time - min_time)

                            trades_is = [t for t in trades if t['time'] < split_time]
                            trades_oos = [t for t in trades if t['time'] >= split_time]
```
`sim.run_multi_asset` runs over all historical timestamps in `universe_data`. In `BARBELL` mode, state variables (`safe_core`, `risk_cap`, `bullets` capital) accumulate sequentially across time. The function then retroactively splits the resulting trade list into `trades_is` and `trades_oos`. Consequently, the trade performance in `trades_oos` depends on capital built up during `trades_is`.

### Observation 1.7: Non-Utilization of `PurgedGroupTimeSeriesSplit` in Search and Backtesting Modules
- **File**: `engine/ml_engine/purged_cv.py`, lines 9–37:
```python
class PurgedGroupTimeSeriesSplit:
    def __init__(self, n_splits: int = 5, expiry_candles: int = 1, embargo_pct: float = 0.01):
...
```
- **Files**: `optimizer_grid_search.py`, lines 83–88; `run_backtest_comparison.py`, lines 65–70; `engine/optimizer.py`, lines 576–580.
`PurgedGroupTimeSeriesSplit` (implementing Marcos López de Prado's purging and embargo methodology) is defined in `purged_cv.py`, but is **never** imported or used in `optimizer_grid_search.py`, `run_backtest_comparison.py`, or `engine/optimizer.py`. Simple static percentage splits (60/40 or 70/30) without purging or embargo are used instead.

### Observation 1.8: Non-Optimizing Walk-Forward Engine
- **File**: `engine/auto_tuner.py`, lines 41–56:
```python
            try:
                pre_is = strat_obj.prepare_data(df_is)
                sigs_is = strat_obj.generate_signals(df_is, base_params, precomputed=pre_is)

                pre_oos = strat_obj.prepare_data(df_oos)
                sigs_oos = strat_obj.generate_signals(df_oos, base_params, precomputed=pre_oos)
...
```
In `WalkForwardEngine.run_wfa`, fixed parameters `base_params` are evaluated on `df_is` and `df_oos` across 5 rolling windows. No parameter tuning, optimization, or selection occurs on `df_is`.

### Observation 1.9: Complete Absence of Optuna Integration
- **Workspace Search**: Grep/search for `optuna`, `optuna.create_study`, `TPESampler`, `CMA-ES`, or `bayesian` across all Python files in `c:\Users\juanc\Desktop\prueba`.
**Result**: 0 matches. Parameter search relies entirely on static grid search scripts (`optimizer_grid_search.py`, `engine/optimizer.py`) and a Rust genetic algorithm binary (`engine/genetic_optimizer/src/main.rs`).

### Observation 1.10: Performance Bottlenecks in Python Backtesting Engine
- **File**: `engine/simulator.py`, lines 50–197:
In `BinarySimulator.run`, simulation iterates through `trade_indices` using explicit Python loops (`for idx in trade_indices: entry_idx = df.index.get_loc(idx)`), performing dataframe indexing (`df.iloc[entry_idx + 1]['open']`, `df.iloc[exit_idx]['close']`) for every trade. This results in $O(N \cdot M)$ execution time during grid searches.

---

## 2. Logic Chain

1. **Target Label Expiry Mismatch Impact**:
   - *From Observation 1.1*: `create_labels` in `optimizer_grid_search.py` calculates `exit_prices` with `shift(-(1 + expiry_candles))`. For `expiry_candles=1`, `shift(-2)` assigns exit price to candle $i+2$.
   - `BinarySimulator.run` calculates `exit_idx = entry_idx + 1` for `expiry_candles=1`, assigning exit price to candle $i+1$.
   - *Inference*: `MetaLabeler` and `RegimeDetector` learn patterns associated with 2-candle price changes, but are evaluated in simulation against 1-candle price changes. This mismatch degrades machine learning filtering accuracy and distorts out-of-sample win rate estimations.

2. **Feature & Threshold Data Leakage Impact**:
   - *From Observations 1.2, 1.3, 1.4, 1.5*:
     - `quantile(0.01)` and `quantile(0.99)` in `volatility_squeeze_ml.py` use the entire dataset's price/volume distribution.
     - `meta_filter.py` retrieves `X['natr'].iloc[-1]` (the last row of the test set) and compares it against `X['natr'].median()` (global test median).
     - `regime_detector.py` runs `GaussianHMM.predict(obs)` (global Viterbi sequence optimization incorporating future observations $t+1 \dots N$).
     - `auto_tuner.py` calculates `atr_14.median()` globally and `atr_14.iloc[-1]` at the end of the dataframe.
   - *Inference*: Information from future time steps (test period) influences indicator scaling, feature boundaries, threshold adjustments, and regime classification at earlier time steps. This produces artificially inflated In-Sample and Out-Of-Sample backtest results that fail in live trading.

3. **Capital State Pollution Impact**:
   - *From Observation 1.6*: `CapitalOptimizer.optimize_daily_confluence_stream` runs `sim.run_multi_asset` over the entire dataset continuously before splitting trades by time.
   - *Inference*: In `BARBELL` mode, trade sizing in the Out-Of-Sample period depends on the equity accumulated during the In-Sample period. OOS metrics are not independent of IS performance.

4. **Absence of Purging & True Walk-Forward Optimization Impact**:
   - *From Observations 1.7 & 1.8*:
     - `PurgedGroupTimeSeriesSplit` is defined but unused in grid search and strategy optimization scripts.
     - `WalkForwardEngine.run_wfa` evaluates static parameters without optimizing on training windows.
   - *Inference*: Without purging and embargo at split boundaries, trades near the split point leak target outcomes across the boundary. Without actual in-sample optimization in walk-forward evaluation, parameter stability across regime shifts cannot be evaluated.

5. **Search Space & Engine Bottleneck Impact**:
   - *From Observations 1.9 & 1.10*:
     - Grid searches are limited to 45–360 fixed parameter combinations.
     - The Rust genetic algorithm operates on a single composite genome (`rsi`, `bb`, `ema`, `htf_ema`, `rejection`, `volatility`).
     - No Optuna framework is available for adaptive sampling (TPE, CMA-ES, Bayesian optimization, hyperparameter pruning).
     - Python backtest loops perform scalar DataFrame slicing per trade.
   - *Inference*: High-dimensional parameter spaces (expiration periods 1–12, session time filters, payout sensitivity, indicator parameters) cannot be explored efficiently with current static grid search tools.

---

## 3. Caveats

1. **Rust Binary Compilation Dependency**: `engine/genetic_optimizer/src/main.rs` requires a compiled binary (`genetic_optimizer.exe`). While `main.rs` includes parallel Rayon fitness computation and neighborhood stability filters, it is limited to a single hardcoded `Genome` architecture.
2. **Strategy Code Scope**: Base strategy implementations (`strategies/daily_confluence.py`, `strategies/genetic_composite.py`) use backward-looking indicators (EMAs, Wilders RSI, rolling ATR). Look-ahead leakage is primary concentrated in ML feature extraction, target labeling, HMM regime detection, and adaptive thresholding routines.
3. **Execution Mode**: Investigation was conducted strictly read-only. No source code files or project configurations were altered.

---

## 4. Conclusion

1. **Quantitative Validity Assessment**: Current backtest and optimization results overestimate Out-Of-Sample performance due to five distinct temporal causality / data leakage bugs:
   - Target label shift mismatch (`shift(-2)` vs 1-candle expiry).
   - Global feature quantile clipping (`quantile(0.01/0.99)` across full series).
   - Adaptive meta-filter thresholding using `.iloc[-1]` and global medians.
   - Global Viterbi sequence decoding in HMM regime detection.
   - Retroactive capital state division in multi-asset Barbell simulations.
2. **Search Space & Optimization Framework Deficiencies**:
   - Parameter search is constrained to low-density grid searches (45–360 combos) or single-genome genetic optimization.
   - Optuna integration (TPE / Bayesian optimization / Multi-objective Pareto optimization) is missing.
   - `PurgedGroupTimeSeriesSplit` is not integrated into search scripts.
   - `WalkForwardEngine` evaluates fixed parameters rather than performing rolling In-Sample parameter optimization.
3. **Actionable Recommendations**:
   - Fix target label logic: align `create_labels` shift (`df['close'].shift(-expiry_candles)`) with `BinarySimulator`.
   - Eliminate future data leakage: compute feature quantiles, NATR medians, and ATR baselines strictly on training splits or rolling historical windows.
   - Replace HMM Viterbi decoding (`predict`) with forward-only filtered state probabilities (`predict_proba` on historical observations up to $t$).
   - Integrate `PurgedGroupTimeSeriesSplit` across all train/test splits.
   - Implement Optuna for multi-dimensional search (timeframes, expirations 1–12, session hours, indicator periods, payout levels).
   - Upgrade `WalkForwardEngine` to perform true Walk-Forward Optimization (WFO).

---

## 5. Verification Method

To independently verify all observations and conclusions:

### 1. Target Label Shift Mismatch Verification
Inspect lines 47–50 of `optimizer_grid_search.py` and compare against lines 69–89 of `engine/simulator.py`:
```powershell
python -c "
import pandas as pd
df = pd.DataFrame({'open': [10, 11, 12, 13, 14], 'close': [10.5, 11.5, 12.5, 13.5, 14.5]})
signals = pd.Series(['CALL', None, None, None, None])
entry_prices = df['open'].shift(-1)
exit_prices = df['close'].shift(-(1 + 1))
print('Entry price for candle 0:', entry_prices.iloc[0]) # Candle 1 Open (11)
print('Exit price for candle 0 (create_labels):', exit_prices.iloc[0]) # Candle 2 Close (12.5) -> 2 candles!
"
```

### 2. Adaptive Meta-Filter `.iloc[-1]` & Global Median Leakage Verification
Inspect lines 69–77 of `engine/ml_engine/meta_filter.py`:
Observe that `current_natr = X['natr'].iloc[-1]` reads index `-1` of DataFrame `X`, regardless of which signal index in `active_indices` is currently being evaluated.

### 3. HMM Global Viterbi Decoding Leakage Verification
Inspect line 88 and line 133 of `engine/ml_engine/regime_detector.py`:
Confirm call to `self.model.predict(obs)`, which invokes `GaussianHMM.predict()` (global Viterbi path decoding across all rows of `obs`).

### 4. Search Space & Optuna Absence Verification
Execute a global code search for Optuna in the workspace:
```powershell
python -c "
import glob
matches = [f for f in glob.glob('**/*.py', recursive=True) if 'optuna' in open(f, encoding='utf-8', errors='ignore').read().lower()]
print('Optuna occurrences:', len(matches))
"
```
Output: `Optuna occurrences: 0`

### 5. Unit Test Execution
Execute the project unit test suite:
```powershell
python -m unittest test_high_winrate_mechanisms.py
```
Output: `5 tests, 0 failures`. Note that existing unit tests cover basic function execution but do not assert zero look-ahead bias or OOS split isolation.
