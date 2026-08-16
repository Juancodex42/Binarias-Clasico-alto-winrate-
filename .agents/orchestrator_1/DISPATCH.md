## 2026-08-12T14:15:59Z
You are the Project Orchestrator for this project.

The user request is located at: `c:/Users/juanc/Desktop/prueba/.agents/ORIGINAL_REQUEST.md`
Project Working Directory: `c:/Users/juanc/Desktop/prueba`
Your metadata directory: `c:/Users/juanc/Desktop/prueba/.agents/orchestrator_1`

## User Goal
Search space exploration and software bug fixing in the binary options quantitative strategy simulator and optimization engine to achieve higher Win Rate (>65%) and positive Out-Of-Sample Expected Value (EV).

## Requirements Summary
1. R1: Software Bug Detection & Correction in the quantitative engine (`BinarySimulator`, `BinaryFeatureExtractor`, `RegimeDetector` / `CUSUMMonitor`, `MetaLabeler`, `engine/`, `strategies/`).
2. R2: Exhaustive Search Space Exploration (grid search, genetic algorithms, Optuna) across hyperparameters, timeframes, market regimes, and meta-filters to maximize OOS Win Rate (>65%) and EV per trade.
3. R3: Robustness Verification & Bias Prevention (ensuring temporal causality, no look-ahead bias, no data leakage in train/test splits and backtest execution).

## Acceptance Criteria
- Unit test suite (`test_high_winrate_mechanisms.py` and new integrity tests) runs without failures or critical warnings.
- Execution errors and bottlenecks in optimization & simulation engine are resolved.
- Optimal parameter configurations and quantitative filters maximizing OOS Win Rate (>65%) and EV are found and reported.
- An executable verification/backtesting script demonstrating empirical and reproducible performance is provided.

Please initialize your briefing (`BRIEFING.md`), master plan (`plan.md`), and progress log (`progress.md`) in `c:/Users/juanc/Desktop/prueba/.agents/orchestrator_1/`, break down the task into milestones, and dispatch subagents (e.g. specialists/workers) to execute the work. Update `progress.md` regularly as work progresses. When all milestones are complete and verified, notify me (the Sentinel).
