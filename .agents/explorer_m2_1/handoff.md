# Handoff Report: Milestone M2 Features 1 & 2 Exploration

**Explorer**: `explorer_m2_1`  
**Working Directory**: `c:/Users/juanc/Desktop/prueba/.agents/explorer_m2_1`  
**Date**: 2026-08-12  
**Milestone**: M2 (Temporal Causality & Zero Leakage Enforcement)  

---

## 1. Observation

Direct code examination of `optimizer_grid_search.py`, `run_backtest_comparison.py`, `engine/simulator.py`, `strategies/volatility_squeeze_ml.py`, `engine/auto_tuner.py`, `strategies/genetic_composite.py`, and `engine/exporter.py` yielded exact file paths, line numbers, and verbatim code references for Features 1 and 2:

### Feature 1: Target Expiry Label Alignment
- **`engine/simulator.py` (lines 69, 76–85)**: `BinarySimulator.run` calculates trade timing as:
  ```python
  entry_price_raw = float(df.iloc[entry_idx + 1]['open'])
  exit_idx = entry_idx + expiry_candles
  exit_price = float(df.iloc[exit_idx]['close'])
  ```
  For 1-candle expiry (`expiry_candles = 1`), trade entry is at `entry_idx + 1` Open price and trade exit is at `entry_idx + 1` Close price.
- **`optimizer_grid_search.py` (lines 47–62)**: `create_labels` defines label generation via vectorized Series shifts:
  ```python
  entry_prices = df['open'].shift(-1)
  exit_prices = df['close'].shift(-expiry_candles)
  diff = exit_prices - entry_prices
  ```
  At index `i`, `entry_prices` is `df['open'].iloc[i + 1]` and `exit_prices` is `df['close'].iloc[i + expiry_candles]`. For `expiry_candles = 1`, `diff` is `df['close'].iloc[i + 1] - df['open'].iloc[i + 1]`, matching `BinarySimulator.run` timing exactly.
- **`run_backtest_comparison.py` (lines 16–31)**: `create_labels` defines iterative label generation:
  ```python
  entry_price = float(df.iloc[entry_idx + 1]['open'])
  exit_price = float(df.iloc[exit_idx]['close'])
  ```
- **`strategies/volatility_squeeze_ml.py` (lines 188–189)**: `exit_prices[valid_mask] = df['close'].values[locs_valid + 1]` hardcodes 1-candle exit, requiring parameterization for multi-candle expiration.

### Feature 2: Feature Scaling & Threshold Leakage Elimination
- **`strategies/volatility_squeeze_ml.py` (lines 109–112)**: `prepare_data` calculates outlier bounds:
  ```python
  q01 = features[col].rolling(200, min_periods=20).quantile(0.01).fillna(features[col])
  q99 = features[col].rolling(200, min_periods=20).quantile(0.99).fillna(features[col])
  features[col] = features[col].clip(q01, q99)
  ```
  This rolling formulation replaces full-sample `features[col].quantile(0.01)` and `.quantile(0.99)` calls, enforcing strict temporal causality.
- **`engine/auto_tuner.py` (lines 193–196)**: `DynamicRegimeAdapter.detect_regime` computes historical median ATR:
  ```python
  current_atr = atr_14.iloc[-1]
  hist_atr_median = atr_14.rolling(100, min_periods=1).median().iloc[-1]
  ```
  This rolling 100-candle formulation replaces the previous full-sample `atr_14.median()`, eliminating look-ahead bias.
- **`strategies/genetic_composite.py` (line 181) & `engine/exporter.py` (line 421)**: Secondary full-sample quantile fallback identified:
  ```python
  squeeze_active = bb_width <= rolling_q30.fillna(bb_width.quantile(0.30))
  ```
  Here `bb_width.quantile(0.30)` calculates a full-sample quantile across the whole dataset to fill initial rolling NaNs.

---

## 2. Logic Chain

1. **Target Expiry Alignment Logic**:
   - *Observation*: `BinarySimulator.run` enters a trade at `entry_idx + 1` Open and exits at `entry_idx + expiry_candles` Close.
   - *Reasoning*: For 1-candle expiry, `entry_idx + 1` Open and `entry_idx + 1` Close define the price movement. In `optimizer_grid_search.py`, `entry_prices = df['open'].shift(-1)` evaluates to `df['open'].iloc[i + 1]` and `exit_prices = df['close'].shift(-expiry_candles)` evaluates to `df['close'].iloc[i + expiry_candles]`.
   - *Deduction*: Vectorized label generation in `optimizer_grid_search.py` is mathematically equivalent to `BinarySimulator.run` execution timing. Parameterizing `volatility_squeeze_ml.py` line 189 (`locs_valid + expiry_candles`) guarantees multi-candle expiry alignment.

2. **Feature Scaling & Threshold Leakage Elimination Logic**:
   - *Observation*: Full-sample quantile calls (`.quantile(0.01)`, `.quantile(0.99)`, `atr_14.median()`, `bb_width.quantile(0.30)`) compute statistics over all rows $0 \dots T-1$.
   - *Reasoning*: Computing quantiles or medians using rows $t+1 \dots T$ leaks future market conditions into past feature values or regime classifications at bar $t$.
   - *Deduction*: Replacing full-sample calls with rolling window statistics (`rolling(200).quantile()`, `rolling(100).median()`) or expanding in-sample statistics (`expanding().quantile()`) restricts calculations strictly to observations $0 \dots t$, satisfying zero-leakage enforcement.

---

## 3. Caveats

- **Read-Only Constraint**: No source code files in `engine/` or `strategies/` were modified during this investigation. Code change proposals are provided in `analysis.md` for implementation agents.
- **Expiry Parameterization Scope**: `optimizer_grid_search.py` tests expirations 1 and 2 (`EXPIRY_CANDLES = [1, 2]`). For `expiry_candles > 1`, label generators must maintain matching shift logic (`shift(-expiry_candles)`).

---

## 4. Conclusion

Features 1 and 2 of Milestone M2 are thoroughly audited, verified, and mapped to exact line numbers and code proposals:
1. Target label shift logic in `optimizer_grid_search.py` and `run_backtest_comparison.py` correctly aligns with `BinarySimulator.run` 1-candle expiry. `strategies/volatility_squeeze_ml.py` requires parameterization for `expiry_candles > 1`.
2. Global feature quantile clipping and global ATR median calculations have been converted to rolling windows (`rolling(200)` and `rolling(100)`). Secondary quantile fallbacks in `genetic_composite.py` and `exporter.py` should be updated to expanding quantiles to achieve complete zero-leakage compliance.

---

## 5. Verification Method

To independently verify these findings and validate code proposals once implemented:

### Command Line Execution
Run unit tests for Features 7 & 8:
```bash
pytest tests/test_tier1_feature_coverage.py -k "TestFeature07_TargetExpiryLabelAlignment" -v
pytest tests/test_tier1_feature_coverage.py -k "TestFeature08_FeatureScalingThresholdLeakage" -v
pytest tests/test_high_winrate_mechanisms.py -v
```

### Inspection Locations
- `optimizer_grid_search.py` (lines 47–62): Check `create_labels` shift logic.
- `strategies/volatility_squeeze_ml.py` (lines 109–112, 188–189): Check rolling quantile clipping and expiry indexing.
- `engine/auto_tuner.py` (lines 193–196): Check rolling ATR median calculation.
- `strategies/genetic_composite.py` (line 181) & `engine/exporter.py` (line 421): Check initial NaN fill logic.
