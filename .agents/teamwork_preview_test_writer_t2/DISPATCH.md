## 2026-08-12T13:26:20Z
Task Objectives:
Write Tier 2 (Boundary & Corner Cases) test suite in `c:\Users\juanc\Desktop\prueba\tests\test_tier2_boundary_corner_cases.py`.

Requirements:
- Target: Write at least 90 test functions (at least 5 boundary, corner case, extreme value, empty input, zero volume, tie, or parameter limit tests per feature for all 18 features in `PROJECT.md § Feature Inventory`).
  - Feature 1: Tie Rule Boundaries (empty series, zero bet amount, 100% tie outcomes, invalid tie_rule parameter).
  - Feature 2: Barbell Boundaries (0 capital, single asset universe, empty universe, 100% loss streak).
  - Feature 3: FracDiff Boundaries (d=0.0, d=1.0, threshold extremes, empty series, constant price series, NaN inputs).
  - Feature 4: Regime & CUSUM Extremes (zero variance, infinite returns, max memory stress test, pause/resume state).
  - Feature 5: MetaLabeler Overflow & Boundaries (nansecond/microsecond timestamps, empty signals, extreme rolling windows).
  - Feature 6: Walk-Forward Zero Trade Windows (0 trade windows, 1 window, 100% loss windows, boundary stability ratio).
  - Feature 7: Expiry Label Boundaries (0 expiry candles, max expiry, boundary shift at end of series, missing values).
  - Feature 8: Feature Scaling Extremes (constant values, extreme outliers, zero volatility squeeze thresholding).
  - Feature 9: HMM Probabilities Boundaries (single state, uniform probabilities, zero transition matrix).
  - Feature 10: Purged CV Boundaries (samples < n_splits, embargo > test set, zero group overlap).
  - Feature 11: Capital Split Isolation Boundaries (0 IS capital, 0 OOS capital, negative returns split).
  - Feature 12: Optuna Extremes (1 trial study, invalid hyperparameter bounds, immediate pruning edge case).
  - Feature 13: Search Space Boundaries (single point search space, extreme expiration ranges 1-12, empty grid dicts).
  - Feature 14: Walk-Forward Boundaries (rolling window size > dataset length, step size = 0, single fold).
  - Feature 15: Vectorized Engine Extremes (empty dataframe, 1 row dataframe, all-NaN signal array).
  - Feature 16: Test Harness Boundaries (missing test files, empty test function execution).
  - Feature 17: Causality Audit Edge Cases (sub-second lookahead attempts, synthetic lookahead detection).
  - Feature 18: Verification Script Boundaries (missing inputs, exception handling, strict threshold edge conditions).
- Use fixtures and helper functions from `tests/conftest.py` so tests execute fast and deterministically.
- Run `pytest tests/test_tier2_boundary_corner_cases.py` using command line tool to verify 100% pass rate.
- Deliver handoff report in `c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_test_writer_t2\handoff.md` and send message to parent (`sub_orch_e2e`).
