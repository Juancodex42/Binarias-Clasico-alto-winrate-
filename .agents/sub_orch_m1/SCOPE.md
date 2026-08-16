# Scope: Milestone M1 — Engine Bug Remediation & Core Fixes

## Architecture
Fixes software bugs and logic flaws across quantitative engine components (`BinarySimulator`, `BinaryFeatureExtractor`, `RegimeDetector`, `CUSUMMonitor`, `MetaLabeler`, `WalkForwardEngine`).

## Assigned Features
| # | Feature | Description | File(s) | Source |
|---|---------|-------------|---------|--------|
| 1 | BinarySimulator Tie Rule Consistency | Support `tie_rule` ('RETURN_STAKE' / 'LOSS') in `run_multi_asset` and align with single-asset `run` | `engine/simulator.py` | Survey 1 |
| 2 | Multi-Asset Barbell State Tracking | Fix bullet state corruption upon streak reset during multi-asset trade evaluation | `engine/simulator.py` | Survey 1 |
| 3 | FracDiff FFT Acceleration | Vectorize `frac_diff_fixed` in `BinaryFeatureExtractor` using `scipy.signal.fftconvolve` | `engine/ml_engine/feature_extractor.py` | Survey 1 |
| 4 | RegimeDetector & CUSUM Memory/Pause Fix | Remove full-sample `returns.std()` leakage in HMM and fix unbounded memory & pause deadlock in CUSUM | `engine/ml_engine/regime_detector.py`, `cusum_monitor.py` | Survey 1 |
| 5 | MetaLabeler Timestamp & Leakage Fix | Fix millisecond timestamp overflow (`unit='s'`) and replace global `median()` with rolling median | `engine/ml_engine/meta_labeler.py` | Survey 1 |
| 6 | Walk-Forward Efficiency Metric Fix | Correct false stability counting for zero OOS trade windows in `WalkForwardEngine` | `engine/auto_tuner.py` | Survey 1 |

## Interface Contracts
- `BinarySimulator.run(df, signals, expiry_candles=1, payout=0.85, bet_amount=10.0, tie_rule='RETURN_STAKE') -> dict`
- `BinarySimulator.run_multi_asset(universe_data, signals_by_pair, expiry_candles=1, payout=0.85, mode='BARBELL', bet_fraction=0.166, tie_rule='RETURN_STAKE') -> dict`
- `BinaryFeatureExtractor.frac_diff_fixed(series, d, threshold=1e-4) -> pd.Series`

## Execution Loop Instructions
Apply Project Pattern iteration loop:
Explorer (3) -> Worker (1) -> Reviewer (2) -> Challenger (2) -> Auditor (1) -> Gate.
Require Worker handoff to verify `pytest tests/` and `pytest test_high_winrate_mechanisms.py` pass cleanly without errors.
Audit is BINARY VETO (CLEAN required).
