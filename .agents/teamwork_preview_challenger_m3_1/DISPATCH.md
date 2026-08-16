# Task Assignment — Challenger 1 (Milestone 3 Empirical Stress Verification)

## Objective
Empirically challenge and stress-test Milestone 3 features (Optuna optimization, search space sampling, Walk-Forward Engine, vectorization parity, and discovered high-winrate configurations).

## Reference Files
- Original Request: c:\Users\juanc\Desktop\prueba\ORIGINAL_REQUEST.md
- Scope Document: c:\Users\juanc\Desktop\prueba\PROJECT.md
- Worker Handoff: c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_worker_m3_impl\handoff.md

## Stress-Testing Mandate
1. Verify vectorization parity between `VectorizedBinarySimulator.run_fast` and `BinarySimulator.run` across synthetic edge case DataFrames (gaps, zero volume, high volatility, consecutive losses triggering ruin).
2. Stress-test `TrueWalkForwardEngine` for edge cases: empty datasets, zero signal windows, single-candle folds, extreme parameter values.
3. Validate discovered top configurations in `data/optuna_results.json` by re-evaluating trades independently using `BinarySimulator.run` to confirm OOS Win Rate > 65% and EV > 0.
4. Report findings and verdict (`PASS` or `FAIL`) in `handoff.md` in your working directory `c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_challenger_m3_1`.
