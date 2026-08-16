# DISPATCH — 2026-08-12T14:41:30Z

## Target
`teamwork_preview_worker_m3_1`

## Task
Implement Milestone 3 (Optuna Framework Integration & Search Space Exploration):
1. **Feature 12 (Optuna Framework Integration)**: Create `engine/optimizer_optuna.py` implementing `OptunaStrategyOptimizer` with `TPESampler(multivariate=True)`, `MedianPruner`, `PurgedGroupTimeSeriesSplit` cross-validation, and trial parameter importance scoring.
2. **Feature 13 (Multi-Dimensional Search Space Design)**: Implement multi-dimensional parameter search space exploring timeframes, expirations (1–12), session hours, RSI/Bollinger/NATR indicator periods, and meta-labeler thresholds targeting Out-Of-Sample (OOS) Win Rate > 65% and positive Expected Value (EV > 0.0).
3. **Feature 14 (True Walk-Forward Optimization Engine)**: Upgrade `WalkForwardEngine` in `engine/auto_tuner.py` to run rolling In-Sample Optuna tuning and Out-Of-Sample evaluation using Purged CV embargo.
4. **Feature 15 (Backtest Engine Parallel Vectorization)**: Implement parallel backtest execution in `engine/optimizer_optuna.py` and `engine/simulator.py` using `joblib` for parallel trial evaluation.

Execute unit and integration tests (`pytest tests/`). Deliver `handoff.md`.
