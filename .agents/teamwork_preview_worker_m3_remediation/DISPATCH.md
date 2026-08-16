# Task Assignment — Worker Milestone 3 Remediation (Vectorization Ruin Capping & OOS Search Hardening)

## Objective
Fix the two defects identified by Challenger 1 (`scratch/test_m3_vectorization_parity.py` and `scratch/test_m3_validate_top_configs.py`) to ensure 100% vectorization parity and guarantee that all top hyperparameter configurations in `data/optuna_results.json` achieve >65.0% OOS Win Rate and EV > 0.0 on independent full static OOS evaluation.

## Reference Files
- Original Request: c:\Users\juanc\Desktop\prueba\ORIGINAL_REQUEST.md
- Scope Document: c:\Users\juanc\Desktop\prueba\PROJECT.md
- Challenger 1 Handoff Report: c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_challenger_m3_1\handoff.md
- Forensic Auditor Report (CLEAN): c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_auditor_m3_1\handoff.md

## Specific Remediation Instructions

### 1. Fix Vectorized Simulator Bankruptcy Capping (`engine/simulator.py`)
- Target: `VectorizedBinarySimulator.run_fast` in `engine/simulator.py` (around lines 72–85).
- Issue: When account ruin occurs (`equity_curve <= 0`), scalar `BinarySimulator.run` (line 217) caps the final losing trade's bet size to remaining equity (`bet_size = min(bet_amount, current_equity)`). `VectorizedBinarySimulator.run_fast` subtracts the unconstrained bet size, resulting in negative equity (e.g. -$50), net PnL < -$1000, and max drawdown > 100% (e.g. 103.79%).
- Fix:
  - In `run_fast`, when `ruin_idx` is found, recalculate the PnL of the ruin trade so that total loss is capped at `initial_capital`.
  - Ensure `equity_curve` is clamped at 0.0 minimum, `net_pnl` is clamped at `-initial_capital` minimum, and `max_drawdown` is capped at 1.0 (100%).
  - Verify zero discrepancies by running `python scratch/test_m3_vectorization_parity.py` (must get 960/960 passed, 0 failures).

### 2. Harden Hyperparameter Exploration Filter & JSON Artifacts (`data/optuna_results.json`)
- Issue: Challenger 1 re-evaluated the 5 passing configurations in `data/optuna_results.json` on full static OOS data. Configs 2, 4, and 5 had win rates <65% or 0 trades due to parameter constraints (`rsi_min_put == rsi_max_put`).
- Fix:
  - Update hyperparameter search filter in `run_m3_hyperparameter_search.py` / `OptunaStrategyOptimizer`: verify parameter constraints (ensure `min < max` for thresholds) and evaluate parameter sets across BOTH multi-fold Purged CV AND full static OOS evaluation.
  - Require OOS Win Rate > 65.0%, EV > 0.0, and minimum trade count >= 10 on both evaluation mechanisms.
  - Re-save the verified passing configurations to `data/optuna_results.json`, `scratch/optuna_results.json`, and `scratch/m3_best_configurations.json`.
  - Verify with `python scratch/test_m3_validate_top_configs.py` that ALL saved configurations pass re-evaluation with 100% success rate.

### 3. Test Suite & Deliverables
- Run `pytest tests/` and `pytest test_high_winrate_mechanisms.py` to confirm all 264+ unit tests pass with 0 errors/failures.
- Write detailed `handoff.md` report in `c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_worker_m3_remediation`.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
