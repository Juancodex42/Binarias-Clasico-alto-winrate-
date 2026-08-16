# Scope: Milestone M2 — Temporal Causality & Zero Leakage Enforcement

## Architecture
Milestone M2 focuses on eliminating data leakage, look-ahead bias, target/expiry mismatches, and capital state cross-contamination across optimization, strategy, regime detection, and backtesting components.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Target Expiry Alignment | Align `create_labels` target shift logic with `BinarySimulator` 1-candle expiry in `optimizer_grid_search.py` | M2 | survey 3 |
| 2 | Rolling Quantiles / Scaling | Eliminate global quantile clipping in `strategies/volatility_squeeze_ml.py` and global ATR medians in `engine/auto_tuner.py` | M2 | survey 1, 3 |
| 3 | Forward-Only HMM | Replace Viterbi `predict()` sequence decoding in `engine/ml_engine/regime_detector.py` with forward-only state probabilities | M2 | survey 1, 3 |
| 4 | Purged CV Integration | Integrate `PurgedGroupTimeSeriesSplit` into all optimization routines (`optimizer_grid_search.py`, `engine/optimizer.py`, etc.) | M2 | survey 3 |
| 5 | IS/OOS Capital Isolation | Isolate multi-asset capital state tracking between IS and OOS periods in `engine/optimizer.py` | M2 | survey 1, 3 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M2 | Temporal Causality & Zero Leakage Enforcement | Features 1-5 | M1 | IN_PROGRESS |

## Interface Contracts
- `create_labels(df, expiry_candles)`: `entry_prices = df['open'].shift(-1)`, `exit_prices = df['close'].shift(-expiry_candles)` (or entry/exit shift matching 1-candle expiry where exit is close of candle entry_idx + expiry_candles - 1 or open of entry_idx+1 to close of entry_idx+expiry_candles).
- `prepare_data(df)`: fit quantile/scalers expanding or rolling over past windows only, without full-sample quantile call.
- `detect_regime(df)`: rolling ATR median `atr_14.rolling(window, min_periods=1).median()`.
- `RegimeDetector.get_current_state(obs)`: uses `model.predict_proba` or forward probabilities on observations up to current bar $t$.
- `PurgedGroupTimeSeriesSplit`: used in optimization splitting without overlapping trade windows.
- `optimize_daily_confluence_stream`: run simulation separately for IS period and reset capital/state before running OOS period.
