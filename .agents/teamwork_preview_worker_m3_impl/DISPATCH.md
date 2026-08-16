# Task Assignment — Worker Milestone 3 Implementation (Features 12–15)

## Objective
Implement Features 12–15 (Optuna integration, multi-dimensional search space, True Walk-Forward Optimization, vectorization acceleration) and execute hyperparameter exploration to discover strategy configurations achieving >65% Out-Of-Sample (OOS) Win Rate and positive Expected Value (EV) per trade.

## Reference Files
- Original Request: c:\Users\juanc\Desktop\prueba\ORIGINAL_REQUEST.md
- Scope Document: c:\Users\juanc\Desktop\prueba\PROJECT.md
- M3 Explorer Blueprints:
  - c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_explorer_m3_1\handoff.md
  - c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_explorer_m3_2\handoff.md

## Scope & Implementation Requirements

### 1. Feature 12: Optuna Framework Integration
- Implement Optuna optimization framework (`engine/optimizer.py` or new `engine/optuna_tuner.py`).
- Support TPE (Tree-structured Parzen Estimator) sampler, Bayesian optimization, parameter trial pruning, and customizable objective functions (maximizing OOS Win Rate, Expected Value per trade, Sharpe ratio, or Calmar ratio).
- Support constraints: minimum trade count (e.g. >= 30 trades OOS), maximum drawdown, and EV > 0.

### 2. Feature 13: Multi-Dimensional Search Space Design
- Expand hyperparameter grid across:
  - Base strategy parameters (RSI periods, Bollinger multipliers, volatility squeeze lookbacks, support/resistance thresholds, SMA/EMA periods).
  - Timeframes (`30m`, `1h`, `4h`) and expiry durations (`1` to `12` candles).
  - Session filtering (e.g. trading hours, Asian/London/NY sessions).
  - Regime gating (`RegimeDetector` HMM thresholds, NATR volatility filters, CUSUM drift limits).
  - Secondary ML meta-labeling probability thresholds ($0.50$ to $0.75$).

### 3. Feature 14: True Walk-Forward Optimization Engine
- Upgrade `WalkForwardEngine` in `engine/auto_tuner.py` / `engine/optimizer.py`.
- Perform rolling In-Sample parameter optimization (via Optuna or grid) and evaluate on non-overlapping Out-Of-Sample windows with `PurgedGroupTimeSeriesSplit` (purging trade expiration overlaps and applying embargo).
- Calculate global OOS aggregated metrics: total trades, total OOS win rate, overall EV per trade, stability index, and Wilson 95% confidence interval lower bound.

### 4. Feature 15: Backtest Engine Parallel Vectorization
- Accelerate feature extraction and simulation loops using `ProcessPoolExecutor` / vectorized NumPy/Pandas operations to enable rapid scanning of thousands of parameter trials.

### 5. Hyperparameter Exploration Execution
- Run hyperparameter search across datasets (`BTCUSDT_30m`, `BTCUSDT_4h`, `ETHUSDT_4h`, etc.).
- Identify configurations achieving >65% OOS Win Rate and EV > 0 with statistically significant trade counts.
- Save best configuration parameters and results for verification in Milestone 4.

## File Ownership
- Target Files: `engine/optimizer.py`, `engine/auto_tuner.py`, `strategies/`, `optimizer_optuna.py` (or `engine/optuna_tuner.py`).

## Deliverables
1. Code changes for Features 12–15.
2. Unit tests covering Optuna optimization, search space generation, and Walk-Forward Engine.
3. Execution output / summary of best hyperparameter configurations demonstrating >65% OOS Win Rate and EV > 0.
4. Detailed `handoff.md` in your working directory `c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_worker_m3_impl`.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
