## 2026-08-12T19:18:03Z
You are teamwork_preview_worker (Milestone 3 Implementation & Search Space Exploration).

Your Working Directory: c:\Users\juanc\Desktop\prueba\.agents\worker_m3
Project Workspace: c:\Users\juanc\Desktop\prueba
Original Request File: c:\Users\juanc\Desktop\prueba\.agents\ORIGINAL_REQUEST.md
Scope Document: c:\Users\juanc\Desktop\prueba\PROJECT.md
Explorer 1 Blueprint: c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_explorer_m3_1\handoff.md
Explorer 2 Blueprint: c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_explorer_m3_2\handoff.md

Task:
Implement Milestone 3 Features 12–15 and execute systematic Optuna Search Space Exploration targeting Out-Of-Sample (OOS) Win Rate > 65% and Positive Expected Value (EV > 0.0 per trade).

Features to Implement & Optimize:
1. Feature 12 (Optuna Framework Integration):
   - Implement `OptunaOptimizer` in `engine/optuna_tuner.py` or `engine/optimizer.py` using `TPESampler(multivariate=True)` and `MedianPruner`.
   - Integrate `PurgedGroupTimeSeriesSplit` for leakage-free cross-validation.
   - Compute parameter importances and prune trials where IS Win Rate < 54.05% or trade count < 30.
2. Feature 13 (Multi-Dimensional Search Space Design):
   - Expand parameter grid across 5 dimensions:
     a. Timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 1d datasets.
     b. Expirations: 1 to 12 candles.
     c. Market sessions: ALL (24h), ASIAN (0-8 UTC), LONDON (8-16 UTC), NEW_YORK (13-21 UTC), OVERLAP_LDN_NY (13-16 UTC), Weekday/Weekend filters.
     d. Indicator periods: RSI (2–30, oversold 15–35, overbought 65–85), Bollinger Bands (10–50, std 1.5–3.5, wick ratio 0.1–0.6, vol_mult 0.5–2.5), NATR (7–28), EMA fast/slow (5–100).
     e. Meta-filters & Regimes: `MetaLabeler` threshold (0.50–0.90), `RegimeDetector` breakeven (0.45–0.60).
3. Feature 14 (True Walk-Forward Optimization Engine):
   - Upgrade `WalkForwardEngine` in `engine/auto_tuner.py` to perform rolling In-Sample Optuna optimization and Out-Of-Sample evaluation with expiry purging and embargo offset.
4. Feature 15 (Backtest Engine Parallel Vectorization):
   - Accelerate backtest simulation loops in `engine/simulator.py` and `engine/optimizer.py` using vectorization / NumPy operations or parallel processing (`ProcessPoolExecutor` / `joblib`).

Execution & Search Goal:
- Run the Optuna exploration script across the historical datasets (`BTCUSDT_30m.csv`, `BTCUSDT_4h.csv`, `ETHUSDT_4h.csv`, etc.).
- Discover configurations achieving Out-Of-Sample Win Rate > 65% and EV > 0.0 per trade with statistical confidence (Wilson 95% CI lower bound > 54.05%).
- Save the winning configurations and full trial results in `data/` or `scratch/optuna_results.json` for M4 verification.
- Run unit tests to verify zero regressions.
