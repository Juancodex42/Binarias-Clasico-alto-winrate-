# Project: Binary Options Quantitative Strategy Simulator & Optimization Engine

## Architecture
The system is a quantitative binary options backtesting, strategy simulation, and hyperparameter optimization platform.
Major layers and data flow:
1. **Data Ingestion & Feature Engineering**: OHLCV market data feeds into `BinaryFeatureExtractor` (calculating indicators, López de Prado FFD, Hurst exponent, NATR, volatility squeeze) respecting strict temporal causality.
2. **Strategy Signal Generation**: Strategy modules (`strategies/`) generate base entry signals (`CALL`/`PUT`) using indicator logic.
3. **Regime & Meta-Filtering**: `RegimeDetector` (HMM/volatility), `CUSUMMonitor` (drift detection), and `MetaLabeler` / `BinaryMLMetaFilter` apply ML probabilistic filtering and regime gating to filter out low-probability trade setups.
4. **Execution Simulation**: `BinarySimulator` simulates binary option trade execution, payoff calculations, expiry handling, and multi-asset capital management (`BARBELL` / `CORE` allocation).
5. **Optimization Engine**: Hyperparameter exploration framework (Grid Search, Optuna TPE/Bayesian optimization, Walk-Forward Engine, Purged Cross-Validation) exploring multi-dimensional parameter spaces to discover configurations with Out-Of-Sample (OOS) Win Rate > 65% and positive Expected Value (EV).
6. **Testing & Verification Harness**: Unit test suite (`tests/`) and reproducible verification script (`verify_high_winrate_oos.py`).

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | BinarySimulator Tie Rule Consistency | Support `tie_rule` ('RETURN_STAKE' / 'LOSS') in `run_multi_asset` and align with single-asset `run` | M1 | Survey 1 |
| 2 | Multi-Asset Barbell State Tracking | Fix bullet state corruption upon streak reset during multi-asset trade evaluation | M1 | Survey 1 |
| 3 | FracDiff FFT Acceleration | Vectorize `frac_diff_fixed` in `BinaryFeatureExtractor` using `scipy.signal.fftconvolve` | M1 | Survey 1 |
| 4 | RegimeDetector & CUSUM Memory/Pause Fix | Remove full-sample `returns.std()` leakage in HMM and fix unbounded memory & pause deadlock in CUSUM | M1 | Survey 1 |
| 5 | MetaLabeler Timestamp & Leakage Fix | Fix millisecond timestamp overflow (`unit='s'`) and replace global `median()` with rolling median | M1 | Survey 1 |
| 6 | Walk-Forward Efficiency Metric Fix | Correct false stability counting for zero OOS trade windows in `WalkForwardEngine` | M1 | Survey 1 |
| 7 | Target Expiry Label Alignment | Align `create_labels` shift logic in optimization scripts with `BinarySimulator` 1-candle expiry | M2 | Survey 2 |
| 8 | Feature Scaling & Threshold Leakage Elimination | Remove global quantile clipping in `volatility_squeeze_ml` and global medians in dynamic regime adapters | M2 | Survey 2 |
| 9 | HMM Forward-Only Probability State Estimation | Replace Viterbi `predict()` sequence decoding with forward-only filtered state probabilities | M2 | Survey 2 |
| 10 | Purged CV Integration | Integrate `PurgedGroupTimeSeriesSplit` with embargo into all optimization and split routines | M2 | Survey 2 |
| 11 | Capital State Split Isolation | Ensure multi-asset simulation splits capital tracking independently between IS and OOS periods | M2 | Survey 2 |
| 12 | Optuna Framework Integration | Implement Optuna (TPE sampler, Bayesian optimization, pruning) for hyperparameter search | M3 | Survey 2 / R2 |
| 13 | Multi-Dimensional Search Space Design | Expand parameter grid across timeframes, expirations (1–12), session hours, indicator periods, and meta-filters | M3 | Survey 2 / R2 |
| 14 | True Walk-Forward Optimization Engine | Upgrade `WalkForwardEngine` to perform rolling In-Sample optimization and OOS evaluation | M3 | Survey 2 / R2 |
| 15 | Backtest Engine Parallel Vectorization | Accelerate backtest simulation loops for high-throughput hyperparameter search | M3 | Survey 2 |
| 16 | Formal `tests/` Directory & `pytest.ini` Setup | Isolate test discovery to `tests/` and `test_high_winrate_mechanisms.py`, ignoring `scratch/` | M4 | Survey 3 |
| 17 | Integrity & Causality Test Suite Expansion | Consolidate scratch verification scripts into formal unit tests (`test_causality_zero_cheating.py`, etc.) | M4 | Survey 3 / Criteria |
| 18 | Executable Backtest Verification Script | Build `verify_high_winrate_oos.py` proving empirical reproducible OOS Win Rate > 65% and Positive EV | M4 | Survey 3 / Criteria |
| 19 | E2E Opaque-Box Test Suite | Requirements-driven multi-tier E2E test suite covering engine workflows (`TEST_READY.md`) | E2E-Track | Dual Track |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Engine Bug Remediation & Core Fixes | `BinarySimulator`, `BinaryFeatureExtractor`, `RegimeDetector`, `CUSUMMonitor`, `MetaLabeler`, `WalkForwardEngine` bug fixes | None | DONE |
| M2 | Temporal Causality & Zero Leakage Enforcement | Expiry label alignment, OOS feature scaling isolation, HMM forward-only probabilities, Purged CV integration, Capital split isolation | M1 | DONE |
| M3 | Optuna & Systematic Search Space Exploration | Optuna integration (TPE/Bayesian), multi-dimensional search space, True Walk-Forward Optimization, vectorization | M1, M2 | DONE |
| M4 | Test Suite Expansion & Reproducible Backtest Verification | Clean `tests/` harness, `pytest.ini`, 0 failures/warnings on unit tests, executable `verify_high_winrate_oos.py` (Win Rate > 65%, EV+) | M1, M2, M3 | DONE |
| E2E | E2E Testing Track | Requirement-driven opaque-box test suite creation (Tiers 1-4) publishing `TEST_READY.md` | None | DONE |

## Interface Contracts

### BinarySimulator Signature Contract
`run(df: pd.DataFrame, signals: pd.Series, expiry_candles: int = 1, payout: float = 0.85, bet_amount: float = 10.0, tie_rule: str = 'RETURN_STAKE') -> dict`
`run_multi_asset(universe_data: dict, signals_by_pair: dict, expiry_candles: int = 1, payout: float = 0.85, mode: str = 'BARBELL', bet_fraction: float = 0.166, tie_rule: str = 'RETURN_STAKE') -> dict`

### BinaryFeatureExtractor Signature Contract
`extract_features(df: pd.DataFrame) -> pd.DataFrame`
`frac_diff_fixed(series: pd.Series, d: float, threshold: float = 1e-4) -> pd.Series`

### MetaLabeler / MetaFilter Signature Contract
`filter_signals(df: pd.DataFrame, base_signals: pd.Series, probability_threshold: float = 0.65) -> pd.Series`

### Optimization Output Contract (`verify_high_winrate_oos.py`)
`run_verification() -> dict`: Returns summary containing strategy configuration, asset universe results, Out-Of-Sample Win Rate (> 0.65), Expected Value per trade (> 0.0), Wilson 95% lower bound, and zero causality violation attestation.

## Code Layout
```
c:\Users\juanc\Desktop\prueba\
├── engine/
│   ├── simulator.py                   # BinarySimulator trade execution & multi-asset capital management
│   ├── auto_tuner.py                   # WalkForwardEngine & DynamicRegimeAdapter
│   ├── optimizer.py                    # Grid search & strategy optimization routines
│   └── ml_engine/
│       ├── feature_extractor.py       # Indicator computation, FFD, Hurst exponent
│       ├── regime_detector.py         # GaussianHMM regime classification
│       ├── cusum_monitor.py           # CUSUM drift detection
│       ├── meta_labeler.py            # Secondary ML label generation & dataset building
│       ├── meta_filter.py             # BinaryMLMetaFilter adaptive threshold signal filtering
│       └── purged_cv.py               # PurgedGroupTimeSeriesSplit cross-validation
├── strategies/                        # Base strategy implementations
│   ├── daily_confluence.py
│   ├── volatility_squeeze_ml.py
│   └── genetic_composite.py
├── tests/                             # Clean unit & integration test suite
│   ├── test_high_winrate_mechanisms.py
│   ├── test_causality_zero_cheating.py
│   ├── test_simulator_integrity.py
│   ├── test_strategies.py
│   └── test_statistics_optimizer.py
├── scratch/                           # Ad-hoc audit scripts (excluded from pytest)
├── pytest.ini                         # Test runner configuration
├── verify_high_winrate_oos.py         # Executable empirical verification script
└── ORIGINAL_REQUEST.md                # Verbatim user requirements
```
