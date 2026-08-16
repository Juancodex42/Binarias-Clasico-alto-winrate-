# Handoff Report: Milestone 2 — Temporal Causality & Zero Leakage Enforcement

**Agent**: `teamwork_preview_explorer_m2_1`  
**Date**: 2026-08-12  
**Target Workspace**: `c:\Users\juanc\Desktop\prueba`  
**Milestone**: Milestone 2 (Temporal Causality & Zero Leakage Enforcement)

---

## 1. Observation

### Feature 7: Target Expiry Label Alignment Mismatch
- **`optimizer_grid_search.py` (lines 47–50)**:
  ```python
  def create_labels(df, signals, expiry_candles=1):
      entry_prices = df['open'].shift(-1)
      exit_prices = df['close'].shift(-(1 + expiry_candles))
  ```
- **`run_backtest_comparison.py` (lines 16–26 & 123–125)**:
  ```python
  entry_price = float(df.iloc[entry_idx + 1]['open'])
  exit_idx = entry_idx + 1 + expiry_candles
  exit_price = float(df.iloc[exit_idx]['close'])
  ```
- **`engine/simulator.py` (lines 69–85)**:
  ```python
  entry_price_raw = float(df.iloc[entry_idx + 1]['open'])
  exit_idx = entry_idx + expiry_candles
  exit_price = float(df.iloc[exit_idx]['close'])
  ```
  *Direct Observation*: When `expiry_candles = 1`, `create_labels` sets `exit_prices = df['close'].shift(-2)` and `run_backtest_comparison.py` sets `exit_idx = entry_idx + 2`. In contrast, `BinarySimulator.run` sets `exit_idx = entry_idx + 1` (`df.iloc[entry_idx + 1]['close']`). Thus, ML models are trained on 2-candle expiry outcomes while evaluated in simulation on 1-candle expiry outcomes.

### Feature 8: Feature Scaling & Quantile / Threshold Leakage
- **`strategies/volatility_squeeze_ml.py` (lines 108–112)**:
  ```python
  # Clip extremes to prevent outlier-driven predictions
  for col in features.columns:
      q01 = features[col].quantile(0.01)
      q99 = features[col].quantile(0.99)
      features[col] = features[col].clip(q01, q99)
  ```
- **`engine/ml_engine/meta_filter.py` (lines 68–86)**:
  ```python
  if has_natr:
      ...
      target_idx = active_indices[-1] if len(active_indices) > 0 else ...
      if target_idx is not None and target_idx in natr_series.index:
          c_natr = natr_series.loc[target_idx]
          m_natr = natr_median_series.loc[target_idx]
          ...
          self.probability_threshold = ...
  ```
- **`engine/auto_tuner.py` (lines 188–189)**:
  ```python
  current_atr = atr_14.iloc[-1]
  hist_atr_median = atr_14.median()
  ```
  *Direct Observation*: Global `quantile(0.01)` and `quantile(0.99)` in `prepare_data` use future dataset observations to constrain early feature values. `BinaryMLMetaFilter.filter_signals` uses `iloc[-1]` (last element of test set) and full-sample median to set `self.probability_threshold` globally for all trades. `DynamicRegimeAdapter.detect_regime` uses global `atr_14.median()` and end-of-series `iloc[-1]`.

### Feature 9: HMM Viterbi Look-Ahead Sequence Decoding
- **`engine/ml_engine/regime_detector.py` (lines 88 & 133)**:
  ```python
  states = self.model.predict(obs)
  ```
- **`optimizer_grid_search.py` (line 123)**:
  ```python
  states_test = regime.model.predict(obs_test)
  ```
  *Direct Observation*: `GaussianHMM.predict(obs)` executes Viterbi decoding over the full observation array `obs`. Viterbi decoding is a global backward-pass algorithm that uses future observations $x_{t+1}, \dots, x_N$ to determine state classification at step $t$.

### Feature 10: Non-Integration of `PurgedGroupTimeSeriesSplit`
- **`engine/ml_engine/purged_cv.py` (lines 4–43)**:
  ```python
  class PurgedGroupTimeSeriesSplit:
      def __init__(self, n_splits: int = 5, expiry_candles: int = 1, embargo_pct: float = 0.01):
  ```
- **`optimizer_grid_search.py` (lines 83–88)** & **`run_backtest_comparison.py` (lines 65–70)**:
  Simple static percentage splits (`iloc[:split]`, `iloc[split:]`) are used without importing or invoking `PurgedGroupTimeSeriesSplit` or applying an embargo.

### Feature 11: Retroactive Capital State Pollution Across Splits
- **`engine/optimizer.py` (lines 561–580)**:
  ```python
  sim_res = sim.run_multi_asset(
      universe_data=universe_data,
      signals_by_pair=signals_by_pair,
      ...
  )
  trades = sim_res.get('trades', [])
  trades_is = [t for t in trades if t['time'] < split_time]
  trades_oos = [t for t in trades if t['time'] >= split_time]
  ```
  *Direct Observation*: `sim.run_multi_asset` runs continuously across the full timeline. In `BARBELL` mode, `safe_core` and `bullets` accumulate equity during the IS window. When `trades_oos` start, capital is NOT reset to `initial_capital` (1000.0). OOS trade sizing and PnL retroactively depend on IS trade outcomes.

---

## 2. Logic Chain

1. **Target Label Expiry Mismatch**:
   - *From Observation 1 (Feature 7)*: `create_labels` uses `shift(-(1 + expiry_candles))` which equals `shift(-2)` for `expiry_candles=1`.
   - `BinarySimulator.run` calculates `exit_idx = entry_idx + 1` for `expiry_candles=1`.
   - *Logic*: ML meta-models learn patterns predicting 2-candle price direction but are evaluated on 1-candle trade executions, creating a structural target definition error.

2. **Feature & Threshold Data Leakage**:
   - *From Observation 2 (Feature 8)*: `quantile(0.01/0.99)` in `prepare_data` operates on full `df`. `meta_filter.py` uses `iloc[-1]` and full-sample `median()`. `auto_tuner.py` uses `atr_14.median()`.
   - *Logic*: Future test observations influence feature scaling and threshold cutoffs during training and early test trade evaluation, violating temporal causality.

3. **HMM Look-Ahead Sequence Decoding**:
   - *From Observation 3 (Feature 9)*: `GaussianHMM.predict(obs)` uses Viterbi decoding over full `obs`.
   - *Logic*: The Viterbi algorithm conditions step $t$'s state prediction on $x_{t+1 \dots N}$. Replacing `predict` with forward-only probability state estimation ($\alpha_t = P(S_t \mid x_0 \dots x_t)$) ensures strictly causal regime gating.

4. **Absence of Purged Cross-Validation**:
   - *From Observation 4 (Feature 10)*: `PurgedGroupTimeSeriesSplit` is defined in `purged_cv.py` but unused in search and backtest routines.
   - *Logic*: Without purging and embargo (López de Prado AFML Ch. 7), labels overlapping across split boundaries cause training data leakage into test sets.

5. **Capital State Pollution Across Splits**:
   - *From Observation 5 (Feature 11)*: `optimizer.py` executes `run_multi_asset` over full data and retroactively splits trade list by `split_time`.
   - *Logic*: In `BARBELL` mode, OOS position sizing inherits `safe_core` accumulated during IS. Slicing data into `universe_data_is` and `universe_data_oos` before running simulation isolates capital tracking, forcing OOS to start independently with `initial_capital=1000.0`.

---

## 3. Caveats

1. **Read-Only Scope**: No production code files in `engine/`, `strategies/`, or root were modified during this investigation. All changes are documented below for implementation.
2. **Third-Party HMM Library**: `hmmlearn` native `predict_proba` executes Forward-Backward smoothing over input arrays. The implementation recommendation includes an explicit Forward-Only algorithm ($\alpha_t$) implementation to guarantee zero look-ahead.
3. **Multi-Asset Data Alignment**: Slicing `universe_data` into IS and OOS requires slice boundaries aligned on timestamp to avoid timestamp mismatches across pairs.

---

## 4. Conclusion & Concrete Recommendations

### Feature 7: Target Expiry Label Alignment
- **Files to Modify**: `optimizer_grid_search.py` (lines 47–50), `run_backtest_comparison.py` (lines 16–29 & 123–125), `strategies/volatility_squeeze_ml.py` (lines 186–190).
- **Exact Code Change**:
  In `optimizer_grid_search.py`:
  ```python
  def create_labels(df, signals, expiry_candles=1):
      entry_prices = df['open'].shift(-1)
      exit_prices = df['close'].shift(-expiry_candles)  # Fixed: shift(-expiry_candles)
      
      labels = pd.Series(index=signals.index, dtype=float)
      calls = signals == 'CALL'
      puts = signals == 'PUT'
      
      labels[calls & (exit_prices > entry_prices)] = 1.0
      labels[calls & (exit_prices <= entry_prices)] = 0.0
      labels[puts & (exit_prices < entry_prices)] = 1.0
      labels[puts & (exit_prices >= entry_prices)] = 0.0
      
      return labels.dropna()
  ```
  In `run_backtest_comparison.py`:
  ```python
  def create_labels(df, signals, expiry_candles=1):
      labels = pd.Series(index=signals.index, dtype=float)
      for idx in signals.dropna().index:
          entry_idx = df.index.get_loc(idx)
          if entry_idx + expiry_candles >= len(df):
              continue
          entry_price = float(df.iloc[entry_idx + 1]['open'])
          exit_idx = entry_idx + expiry_candles  # Fixed: entry_idx + expiry_candles
          exit_price = float(df.iloc[exit_idx]['close'])
          signal = signals.loc[idx]
          if signal == 'CALL':
              labels.loc[idx] = 1 if exit_price > entry_price else 0
          elif signal == 'PUT':
              labels.loc[idx] = 1 if exit_price < entry_price else 0
      return labels.dropna()
  ```

### Feature 8: Feature Scaling & Quantile Leakage Elimination
- **Files to Modify**: `strategies/volatility_squeeze_ml.py` (lines 108–112), `engine/ml_engine/meta_filter.py` (lines 68–86), `engine/auto_tuner.py` (lines 188–189).
- **Exact Code Change**:
  In `strategies/volatility_squeeze_ml.py`:
  ```python
  # Rolling quantile clipping (strictly historical window)
  for col in features.columns:
      q01 = features[col].rolling(200, min_periods=20).quantile(0.01).fillna(features[col])
      q99 = features[col].rolling(200, min_periods=20).quantile(0.99).fillna(features[col])
      features[col] = features[col].clip(q01, q99)
  ```
  In `engine/ml_engine/meta_filter.py`:
  Remove lines 68–86 which set `self.probability_threshold` globally using `iloc[-1]`. Keep per-index threshold evaluation inside `filter_signals` (lines 102–115) using rolling medians: `natr_median_series = natr_series.rolling(100, min_periods=1).median()`.
  In `engine/auto_tuner.py`:
  ```python
  @staticmethod
  def detect_regime(df: pd.DataFrame, at_index: int = -1) -> dict:
      if df is None or len(df) < 50:
          return {"regime": "NORMAL", "volatility_quantile": 0.5, "trend_direction": "NEUTRAL"}
      
      df_sub = df.iloc[:at_index+1] if at_index != -1 else df
      ...
      hist_atr_median = atr_14.iloc[:len(df_sub)].rolling(100, min_periods=1).median().iloc[-1]
      current_atr = atr_14.iloc[len(df_sub)-1]
      vol_q = current_atr / hist_atr_median if hist_atr_median > 0 else 1.0
  ```

### Feature 9: HMM Forward-Only Probability State Estimation
- **File to Modify**: `engine/ml_engine/regime_detector.py` (lines 88, 124–135).
- **Exact Code Change**:
  Add `predict_proba_forward` method to `RegimeDetector`:
  ```python
  def predict_proba_forward(self, obs: np.ndarray) -> np.ndarray:
      """
      Computes forward-only state probabilities P(S_t = k | x_0 ... x_t)
      using the HMM Forward algorithm without backward smoothing or Viterbi look-ahead.
      """
      if not self.is_fitted or self.model is None or len(obs) == 0:
          return np.full((len(obs), self.n_states), 1.0 / self.n_states)

      n_samples = len(obs)
      n_components = self.n_states
      alpha = np.zeros((n_samples, n_components))

      log_frameprob = self.model._compute_log_likelihood(obs)
      frameprob = np.exp(log_frameprob)

      # Initialization t = 0
      alpha[0] = self.model.startprob_ * frameprob[0]
      sum_a0 = alpha[0].sum()
      if sum_a0 > 0:
          alpha[0] /= sum_a0
      else:
          alpha[0] = 1.0 / n_components

      # Induction t = 1 ... N-1
      transmat = self.model.transmat_
      for t in range(1, n_samples):
          alpha[t] = np.dot(alpha[t-1], transmat) * frameprob[t]
          sum_at = alpha[t].sum()
          if sum_at > 0:
              alpha[t] /= sum_at
          else:
              alpha[t] = 1.0 / n_components

      return alpha

  def predict_forward(self, obs: np.ndarray) -> np.ndarray:
      """Returns state sequence derived strictly from forward-only probabilities."""
      probs = self.predict_proba_forward(obs)
      return np.argmax(probs, axis=1)

  def get_current_state(self, df: pd.DataFrame) -> int:
      if not self.is_fitted or self.model is None:
          return -1
      obs = self._prepare_observations(df)
      if len(obs) == 0:
          return -1
      states = self.predict_forward(obs)
      return int(states[-1])
  ```

### Feature 10: Purged CV Integration
- **Files to Modify**: `optimizer_grid_search.py` (lines 83–95), `engine/auto_tuner.py` (`WalkForwardEngine`), `run_backtest_comparison.py`.
- **Exact Code Change**:
  In `optimizer_grid_search.py`:
  ```python
  from engine.ml_engine.purged_cv import PurgedGroupTimeSeriesSplit

  cv = PurgedGroupTimeSeriesSplit(n_splits=5, expiry_candles=expiry, embargo_pct=0.01)
  for train_idx, test_idx in cv.split(df):
      df_train, df_test = df.iloc[train_idx], df.iloc[test_idx]
      signals_train, signals_test = signals.iloc[train_idx], signals.iloc[test_idx]
      ...
  ```
  In `engine/auto_tuner.py` (`WalkForwardEngine.run_wfa`):
  Apply `expiry_candles` purge at boundary `split_idx` (`df_is = df_sub.iloc[:split_idx - expiry_candles]`, `df_oos = df_sub.iloc[split_idx + embargo_offset:]`).

### Feature 11: Capital State Split Isolation
- **Files to Modify**: `engine/optimizer.py` (lines 560–580), `engine/simulator.py`.
- **Exact Code Change**:
  In `engine/optimizer.py`:
  ```python
  # Split universe data chronologically BEFORE running simulation
  universe_data_is = {}
  universe_data_oos = {}

  for sym, df_sym in universe_data.items():
      split_idx = int(len(df_sym) * 0.7)
      universe_data_is[sym] = df_sym.iloc[:split_idx].reset_index(drop=True)
      universe_data_oos[sym] = df_sym.iloc[split_idx:].reset_index(drop=True)

  # Run IS simulation with fresh initial capital
  sim_is = sim.run_multi_asset(
      universe_data=universe_data_is,
      signals_by_pair=signals_by_pair_is,
      expiry_candles=2, payout=payout, mode='BARBELL', initial_capital=1000.0
  )

  # Run OOS simulation independently with fresh initial capital
  sim_oos = sim.run_multi_asset(
      universe_data=universe_data_oos,
      signals_by_pair=signals_by_pair_oos,
      expiry_candles=2, payout=payout, mode='BARBELL', initial_capital=1000.0
  )
  ```

---

## 5. Verification Method

To independently verify that all recommendations solve the look-ahead bias and data leakage issues:

1. **Feature 7 Verification**:
   Execute:
   ```powershell
   python -c "
   import pandas as pd
   from optimizer_grid_search import create_labels
   df = pd.DataFrame({'open': [100, 101, 102, 103], 'close': [100.5, 101.5, 102.5, 103.5]})
   signals = pd.Series(['CALL', None, None, None])
   labels = create_labels(df, signals, expiry_candles=1)
   print('Label for candle 0:', labels.iloc[0]) # Must evaluate candle 1 close (101.5) vs candle 1 open (101) = 1.0 (WIN)
   "
   ```

2. **Feature 8 Verification**:
   Verify that `prepare_data` does not invoke global `df.quantile()` or global `df.median()`.

3. **Feature 9 Verification**:
   Verify that `RegimeDetector.get_current_state` invokes `predict_forward(obs)` and produces identical state classifications for `obs[:t]` regardless of future rows `obs[t+1:]`.

4. **Feature 10 Verification**:
   Run `PurgedGroupTimeSeriesSplit` split generator and verify that no index in `train_indices` falls within `[test_start - expiry_candles, test_end + embargo_offset]`.

5. **Feature 11 Verification**:
   Verify that `sim_oos['summary']['net_pnl']` and `initial_capital` start at exactly 1000.0 regardless of whether IS was winning or losing.

6. **Unit Test Harness Execution**:
   Run tests:
   ```powershell
   pytest tests/test_tier1_feature_coverage.py -k "Feature 7 or Feature 8 or Feature 9 or Feature 10 or Feature 11" -v
   ```
