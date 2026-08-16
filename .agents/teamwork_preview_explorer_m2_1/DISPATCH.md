# DISPATCH — 2026-08-12T14:18:00Z

## Target
`teamwork_preview_explorer_m2_1`

## Task
Investigate codebase for Milestone 2 (Temporal Causality & Zero Leakage Enforcement):
- Feature 7: Target expiry label alignment (`create_labels` in optimization scripts vs `BinarySimulator` 1-candle expiry)
- Feature 8: Feature scaling & quantile leakage elimination (rolling scalers, no global quantile clipping in `volatility_squeeze_ml.py`, no global medians)
- Feature 9: HMM forward-only probability state estimation in `regime_detector.py`
- Feature 10: Purged CV integration (`PurgedGroupTimeSeriesSplit` + embargo in tuning routines)
- Feature 11: Capital state split isolation in `simulator.py` (IS vs OOS capital tracking isolation)

Examine codebase files, identify exact lines to modify, and formulate an actionable implementation plan. Deliver `handoff.md`.
