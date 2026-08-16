# Execution Plan: Milestone M2 — Temporal Causality & Zero Leakage Enforcement

## Objective
Execute the full iteration loop (Explorers -> Worker -> Reviewers -> Challengers -> Forensic Auditor -> Gate) to implement and verify all 5 features in Milestone M2.

## Iteration Loop Plan
1. **Phase 1: Exploration & Fix Strategy Design**
   - Dispatch 3 Explorers (`teamwork_preview_explorer`) to inspect exact code locations, formulate precise fix proposals, and verify requirements for:
     - Target shift logic in `optimizer_grid_search.py` vs `BinarySimulator`.
     - Quantile clipping in `strategies/volatility_squeeze_ml.py` and ATR median in `engine/auto_tuner.py`.
     - Forward-only HMM state probabilities in `engine/ml_engine/regime_detector.py`.
     - `PurgedGroupTimeSeriesSplit` integration in optimization routines.
     - Capital state isolation in `engine/optimizer.py`.
   - Synthesize findings into unified fix strategy for Worker.

2. **Phase 2: Implementation**
   - Dispatch 1 Worker (`teamwork_preview_worker`) with Explorer findings, explicit file boundaries, and mandatory zero-cheating warning.
   - Worker implements fixes, runs `pytest tests/` and `pytest test_high_winrate_mechanisms.py`.

3. **Phase 3: Independent Verification & Review**
   - Dispatch 2 Reviewers (`teamwork_preview_reviewer`) to independently review code changes, correctness, zero-leakage, and test results.
   - Dispatch 2 Challengers (`teamwork_preview_challenger`) to stress test temporal causality and verify no regressions.
   - Dispatch 1 Forensic Auditor (`teamwork_preview_auditor`) for integrity audit (check for dummy code, hardcoded outputs, or cheating).

4. **Phase 4: Gate Evaluation & Completion**
   - Update `GATE_STATUS.md`. Verify ALL gate criteria: Auditor CLEAN, Reviewers APPROVE, Challengers confirm, tests pass.
   - Update `SCOPE.md`, `PROJECT.md`, `progress.md`, and `BRIEFING.md`.
   - Send completion message to parent orchestrator.
