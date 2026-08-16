# Plan — Project Orchestrator (Generation 3)

## Objective
Complete remaining milestones (M2 finalization, M3 Optuna Search Space Exploration targeting >65% OOS Win Rate & Positive EV, M4 Executable Backtest Verification Script & Test Harness Expansion) and submit Victory Report to parent (Sentinel).

## Phase 1: Milestone 2 Finalization
1. Dispatch Worker (`worker_m2_fix`) to encapsulate global monkey patching in `optimizer_grid_search.py` inside `if __name__ == '__main__':`.
2. Dispatch 2 Reviewers (`reviewer_m2_1`, `reviewer_m2_2`) to re-review M2 and confirm all M2 requirements (Features 7–11) pass cleanly.
3. Validate M2 Gate in `GATE_STATUS.md` (Forensic Auditor CLEAN, Challenger PASS, Reviewers APPROVE). Mark M2 as `DONE` in `PROJECT.md`.

## Phase 2: Milestone 3 — Optuna Framework & Search Space Exploration
1. Dispatch Worker (`worker_m3`) to implement Features 12–15:
   - Optuna integration (`engine/optuna_tuner.py` or `engine/optimizer.py`) with TPE sampler and Bayesian optimization.
   - Expanded multi-dimensional search space (timeframes 1m/5m/15m/30m/1h/4h, expirations 1–12, session filters, indicator parameters, HMM regimes, ML meta-filters).
   - True Walk-Forward Optimization engine integration with Purged CV.
   - Vectorization and parallel acceleration of simulation loops.
2. Execute hyperparameter search to identify configurations achieving Out-Of-Sample Win Rate > 65% and Positive EV per trade.
3. Dispatch 2 Reviewers, 2 Challengers, and 1 Forensic Auditor for M3 Gate Verification.

## Phase 3: Milestone 4 — Test Suite Expansion & Backtest Verification
1. Dispatch Worker (`worker_m4`) to build:
   - Formal test harness isolation in `tests/` with `pytest.ini`.
   - Integrity and causality unit test expansion (`test_causality_zero_cheating.py`, `test_high_winrate_mechanisms.py`).
   - Executable backtest verification script `verify_high_winrate_oos.py` demonstrating empirical reproducible OOS Win Rate > 65% and Positive EV per trade.
2. Dispatch 2 Reviewers, 2 Challengers, and 1 Forensic Auditor for M4 Gate Verification.

## Phase 4: Final Synthesis & Victory Report
1. Verify all milestones M1–M4 and Dual-Track E2E are DONE in `PROJECT.md`.
2. Ensure full test suite passes with 0 failures/warnings and Forensic Auditor attests zero cheating/leakage.
3. Submit victory report to Sentinel.
