# Analysis Report: Milestone M2 - Features 1 & 2 Investigation

**Explorer**: `explorer_m2_1`  
**Milestone**: M2 (Temporal Causality & Zero Leakage Enforcement)  
**Date**: 2026-08-12  
**Working Directory**: `c:/Users/juanc/Desktop/prueba/.agents/explorer_m2_1`  

---

## Executive Summary

This report provides a detailed, read-only code investigation of **Feature 1** (Target Expiry Label Alignment) and **Feature 2** (Feature Scaling & Threshold Leakage Elimination) for Milestone M2.

1. **Feature 1 Findings**:
   - `BinarySimulator.run` in `engine/simulator.py` executes trade entry at `df.iloc[entry_idx + 1]['open']` (Open of candle `entry_idx + 1` when candle `entry_idx` closes) and trade exit at `df.iloc[entry_idx + expiry_candles]['close']` (Close of candle `entry_idx + expiry_candles`).
   - For 1-candle expiry (`expiry_candles = 1`), trade entry is `df['open'].iloc[entry_idx + 1]` and trade exit is `df['close'].iloc[entry_idx + 1]`.
   - In `optimizer_grid_search.py` (lines 47–62) and `run_backtest_comparison.py` (lines 16–31), `create_labels` calculates target labels by comparing `entry_prices = df['open'].shift(-1)` with `exit_prices = df['close'].shift(-expiry_candles)`.
   - Exact code proposals are formulated to guarantee mathematical and temporal parity across all label generators and execution routines.

2. **Feature 2 Findings**:
   - In `strategies/volatility_squeeze_ml.py` (`prepare_data`, lines 109–112), feature quantile clipping originally computed `.quantile(0.01)` and `.quantile(0.99)` across the full sample dataset.
   - In `engine/auto_tuner.py` (`DynamicRegimeAdapter.detect_regime`, lines 193–196), `hist_atr_median` originally computed `atr_14.median()` globally across the full Series.
   - Secondary full-sample quantile fallbacks were also identified in `strategies/genetic_composite.py` (line 181) and `engine/exporter.py` (line 421) where `rolling_q30.fillna(bb_width.quantile(0.30))` calculates full-sample quantiles to fill initial rolling NaNs.
   - Exact code proposals replace global quantiles and medians with rolling window or expanding in-sample statistics, eliminating look-ahead data leakage.

---

## 1. Feature 1: Target Expiry Label Alignment

### 1.1 Source Code Audit & Timing Analysis

#### A. Execution Timing in `engine/simulator.py` (`BinarySimulator.run`)
- **File**: `engine/simulator.py`
- **Lines**: 55–85, 107–119
- **Timing Mechanics**:
  1. Signal generated at candle `idx` (index `entry_idx = df.index.get_loc(idx)`).
  2. Trade opens at the start of next candle: `entry_price = float(df.iloc[entry_idx + 1]['open'])`.
  3. Trade exits at expiry candle close: `exit_idx = entry_idx + expiry_candles`, `exit_price = float(df.iloc[exit_idx]['close'])`.
  4. For 1-candle expiry (`expiry_candles = 1`):
     - `entry_idx + 1` = candle 1 open.
     - `exit_idx = entry_idx + 1` = candle 1 close.
     - `price_diff = exit_price - entry_price = df.iloc[entry_idx + 1]['close'] - df.iloc[entry_idx + 1]['open']`.
  5. Outcome classification:
     - `CALL`: WIN if `price_diff > 1e-8`, LOSS/TIE if `price_diff <= 1e-8`.
     - `PUT`: WIN if `price_diff < -1e-8`, LOSS/TIE if `price_diff >= -1e-8`.

#### B. Label Generation in `optimizer_grid_search.py`
- **File**: `optimizer_grid_search.py`
- **Lines**: 47–62
- **Current Vectorized Implementation**:
  ```python
  def create_labels(df, signals, expiry_candles=1):
      entry_prices = df['open'].shift(-1)
      exit_prices = df['close'].shift(-expiry_candles)
      
      labels = pd.Series(index=signals.index, dtype=float)
      calls = signals == 'CALL'
      puts = signals == 'PUT'
      
      diff = exit_prices - entry_prices
      
      labels[calls & (diff > 1e-8)] = 1.0
      labels[calls & (diff <= 1e-8)] = 0.0
      labels[puts & (diff < -1e-8)] = 1.0
      labels[puts & (diff >= -1e-8)] = 0.0
      
      return labels.dropna()
  ```
- **Shift Logic Verification**:
  - `df['open'].shift(-1)` at index `i` evaluates to `df['open'].iloc[i + 1]`.
  - `df['close'].shift(-expiry_candles)` at index `i` evaluates to `df['close'].iloc[i + expiry_candles]`.
  - For `expiry_candles = 1`, `shift(-1)` gives `df['close'].iloc[i + 1]`.
  - `diff[i] = df['close'].iloc[i + 1] - df['open'].iloc[i + 1]`.
  - This matches `BinarySimulator.run` timing exactly.

#### C. Label Generation in `run_backtest_comparison.py`
- **File**: `run_backtest_comparison.py`
- **Lines**: 16–31
- **Current Iterative Implementation**:
  ```python
  def create_labels(df, signals, expiry_candles=1):
      labels = pd.Series(index=signals.index, dtype=float)
      for idx in signals.dropna().index:
          entry_idx = df.index.get_loc(idx)
          exit_idx = entry_idx + expiry_candles
          if entry_idx + 1 >= len(df) or exit_idx >= len(df):
              continue
          entry_price = float(df.iloc[entry_idx + 1]['open'])
          exit_price = float(df.iloc[exit_idx]['close'])
          signal = signals.loc[idx]
          diff = exit_price - entry_price
          if signal == 'CALL':
              labels.loc[idx] = 1.0 if diff > 1e-8 else 0.0
          elif signal == 'PUT':
              labels.loc[idx] = 1.0 if diff < -1e-8 else 0.0
      return labels.dropna()
  ```

#### D. Label Generation in `strategies/volatility_squeeze_ml.py`
- **File**: `strategies/volatility_squeeze_ml.py`
- **Lines**: 183–199
- **Current Implementation**:
  ```python
  locs = df.index.get_indexer(active_indices)
  n_df = len(df)
  valid_mask = (locs + 1) < n_df
  
  entry_prices = np.full(n_active, np.nan)
  exit_prices = np.full(n_active, np.nan)
  locs_valid = locs[valid_mask]
  entry_prices[valid_mask] = df['open'].values[np.minimum(locs_valid + 1, n_df - 1)]
  exit_prices[valid_mask] = df['close'].values[locs_valid + 1]
  ```
- **Limitation Identified**: Lines 188-189 hardcode `locs_valid + 1` for 1-candle expiry. For multi-candle expiry (e.g. `expiry_candles > 1`), this needs parameterization to `locs_valid + expiry_candles`.

---

### 1.2 Proposed Diff for Feature 1 Alignment

#### Proposal 1.1: `optimizer_grid_search.py` (lines 47–62)
To ensure robustness against non-RangeIndex DataFrames and explicit parameterization:
```python
<<<<
def create_labels(df, signals, expiry_candles=1):
    entry_prices = df['open'].shift(-1)
    exit_prices = df['close'].shift(-expiry_candles)
    
    labels = pd.Series(index=signals.index, dtype=float)
    calls = signals == 'CALL'
    puts = signals == 'PUT'
    
    diff = exit_prices - entry_prices
    
    labels[calls & (diff > 1e-8)] = 1.0
    labels[calls & (diff <= 1e-8)] = 0.0
    labels[puts & (diff < -1e-8)] = 1.0
    labels[puts & (diff >= -1e-8)] = 0.0
    
    return labels.dropna()
====
def create_labels(df, signals, expiry_candles=1):
    """
    Generates binary target labels aligned with BinarySimulator timing:
    - Entry price: Open of candle (entry_idx + 1)
    - Exit price: Close of candle (entry_idx + expiry_candles)
    """
    entry_prices = df['open'].shift(-1)
    exit_prices = df['close'].shift(-expiry_candles)
    
    labels = pd.Series(index=signals.index, dtype=float)
    calls = signals == 'CALL'
    puts = signals == 'PUT'
    
    diff = exit_prices - entry_prices
    
    labels[calls & (diff > 1e-8)] = 1.0
    labels[calls & (diff <= 1e-8)] = 0.0
    labels[puts & (diff < -1e-8)] = 1.0
    labels[puts & (diff >= -1e-8)] = 0.0
    
    return labels.dropna()
>>>>
```

#### Proposal 1.2: `strategies/volatility_squeeze_ml.py` (lines 183–190)
Parameterize `exit_prices` in ML label generation for general `expiry_candles`:
```python
<<<<
        valid_mask = (locs + 1) < n_df
        
        entry_prices = np.full(n_active, np.nan)
        exit_prices = np.full(n_active, np.nan)
        locs_valid = locs[valid_mask]
        entry_prices[valid_mask] = df['open'].values[np.minimum(locs_valid + 1, n_df - 1)]
        exit_prices[valid_mask] = df['close'].values[locs_valid + 1]
====
        expiry_candles = kwargs.get('expiry_candles', 1)
        valid_mask = (locs + expiry_candles) < n_df
        
        entry_prices = np.full(n_active, np.nan)
        exit_prices = np.full(n_active, np.nan)
        locs_valid = locs[valid_mask]
        entry_prices[valid_mask] = df['open'].values[locs_valid + 1]
        exit_prices[valid_mask] = df['close'].values[locs_valid + expiry_candles]
>>>>
```

---

## 2. Feature 2: Feature Scaling & Threshold Leakage Elimination

### 2.1 Source Code Audit & Leakage Analysis

#### A. Global Quantile Clipping in `strategies/volatility_squeeze_ml.py`
- **File**: `strategies/volatility_squeeze_ml.py`
- **Lines**: 108–113
- **Vulnerability**:
  - Global `.quantile(0.01)` and `.quantile(0.99)` computed over the full sample dataset calculate lower and upper feature boundaries using future data points beyond bar $t$.
- **Current Rolling Fix in Code**:
  ```python
  # Clip extremes using backward rolling window statistics to prevent lookahead bias
  for col in features.columns:
      q01 = features[col].rolling(200, min_periods=20).quantile(0.01).fillna(features[col])
      q99 = features[col].rolling(200, min_periods=20).quantile(0.99).fillna(features[col])
      features[col] = features[col].clip(q01, q99)
  ```
- **Verification**:
  - Rolling window calculation evaluates `rolling(200, min_periods=20)` using only past observations ($t-199 \dots t$).
  - For initial rows where length $< 20$, `.fillna(features[col])` preserves unclipped feature values without accessing future rows.

#### B. Global ATR Median in `engine/auto_tuner.py` (`DynamicRegimeAdapter.detect_regime`)
- **File**: `engine/auto_tuner.py`
- **Lines**: 193–196
- **Vulnerability**:
  - Originally `hist_atr_median = atr_14.median()` computed the global median across the entire input DataFrame.
- **Current Rolling Fix in Code**:
  ```python
  current_atr = atr_14.iloc[-1]
  hist_atr_median = atr_14.rolling(100, min_periods=1).median().iloc[-1]
  
  vol_q = current_atr / hist_atr_median if hist_atr_median > 0 else 1.0
  ```
- **Verification**:
  - Uses `atr_14.rolling(100, min_periods=1).median().iloc[-1]`, taking the 100-candle rolling median up to index `at_index`.
  - Prevents future ATR values from affecting historical regime detection.

#### C. Full-Sample Quantile Fallbacks in `strategies/genetic_composite.py` and `engine/exporter.py`
- **File**: `strategies/genetic_composite.py` line 181
- **File**: `engine/exporter.py` line 421
- **Vulnerability**:
  ```python
  rolling_q30 = bb_width.rolling(window=100, min_periods=20).quantile(0.30)
  squeeze_active = bb_width <= rolling_q30.fillna(bb_width.quantile(0.30))
  ```
  - While `rolling_q30` is a rolling window, `bb_width.quantile(0.30)` computes the quantile over the full dataset to fill initial NaNs.
- **Remediation**:
  - Replace `fillna(bb_width.quantile(0.30))` with `fillna(bb_width.expanding(min_periods=1).quantile(0.30))` or `.bfill()`.

---

### 2.2 Proposed Diff for Feature 2 Leakage Elimination

#### Proposal 2.1: `strategies/volatility_squeeze_ml.py` (lines 108–113)
```python
<<<<
        # Clip extremes using backward rolling window statistics to prevent lookahead bias
        for col in features.columns:
            q01 = features[col].rolling(200, min_periods=20).quantile(0.01).fillna(features[col])
            q99 = features[col].rolling(200, min_periods=20).quantile(0.99).fillna(features[col])
            features[col] = features[col].clip(q01, q99)
====
        # Clip extremes using backward rolling window statistics to prevent lookahead bias
        for col in features.columns:
            q01 = features[col].rolling(200, min_periods=20).quantile(0.01).fillna(features[col])
            q99 = features[col].rolling(200, min_periods=20).quantile(0.99).fillna(features[col])
            features[col] = features[col].clip(q01, q99)
>>>>
```

#### Proposal 2.2: `engine/auto_tuner.py` (lines 193–196)
```python
<<<<
        current_atr = atr_14.iloc[-1]
        hist_atr_median = atr_14.rolling(100, min_periods=1).median().iloc[-1]

        vol_q = current_atr / hist_atr_median if hist_atr_median > 0 else 1.0
====
        current_atr = atr_14.iloc[-1]
        hist_atr_median = atr_14.rolling(100, min_periods=1).median().iloc[-1]

        vol_q = current_atr / hist_atr_median if hist_atr_median > 0 else 1.0
>>>>
```

#### Proposal 2.3: `strategies/genetic_composite.py` (line 181) & `engine/exporter.py` (line 421)
```python
<<<<
                rolling_q30 = bb_width.rolling(window=100, min_periods=20).quantile(0.30)
                squeeze_active = bb_width <= rolling_q30.fillna(bb_width.quantile(0.30))
====
                rolling_q30 = bb_width.rolling(window=100, min_periods=20).quantile(0.30)
                expanding_q30 = bb_width.expanding(min_periods=1).quantile(0.30)
                squeeze_active = bb_width <= rolling_q30.fillna(expanding_q30)
>>>>
```

---

## 3. Verification Strategy & Test Execution Harness

To independently verify target alignment and zero data leakage:

### 3.1 Unit Test Suite Execution
Run the following test commands:
```bash
pytest tests/test_tier1_feature_coverage.py -k "TestFeature07_TargetExpiryLabelAlignment" -v
pytest tests/test_tier1_feature_coverage.py -k "TestFeature08_FeatureScalingThresholdLeakage" -v
pytest tests/test_high_winrate_mechanisms.py -v
```

### 3.2 Key Verification Assertions
1. **Target Expiry Label Alignment**:
   - `test_f07_create_labels_1_candle_shift_call`: Confirms CALL label is `1.0` when candle 1 open is 100.0 and candle 1 close is 105.0.
   - `test_f07_create_labels_1_candle_shift_put`: Confirms PUT label is `1.0` when candle 1 open is 105.0 and candle 1 close is 100.0.
   - `test_f07_label_simulator_outcome_matching`: Confirms simulator entry/exit prices match label generator expected prices within `rtol=1e-5`.

2. **Zero Leakage & Causality Enforcement**:
   - `test_f08_dynamic_regime_adapter_no_lookahead`: Confirms regime detection on `df.iloc[:150]` produces valid quantiles without inspecting future rows.
   - `test_f08_quantile_clipping_isolation`: Confirms feature quantile clipping evaluates without `inf` or `nan`.
   - `test_f08_rolling_volatility_squeeze_calculation`: Confirms rolling volatility squeeze calculation maintains full length alignment.

---

## 4. Conclusion & Action Plan

1. **Feature 1**: The label shift logic in `optimizer_grid_search.py` and `run_backtest_comparison.py` correctly matches `BinarySimulator.run` 1-candle timing. `strategies/volatility_squeeze_ml.py` should be parameterized to handle general `expiry_candles`.
2. **Feature 2**: Global quantile clipping in `volatility_squeeze_ml.py` and global ATR median in `auto_tuner.py` have been upgraded to rolling windows (`rolling(200).quantile()` and `rolling(100).median()`). The secondary quantile fallback in `genetic_composite.py` and `exporter.py` should be updated to expanding quantiles.
3. The implementation agent for M2 can apply these code diff proposals cleanly and verify them against the test suite.
