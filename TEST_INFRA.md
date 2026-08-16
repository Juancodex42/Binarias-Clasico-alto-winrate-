# Test Infrastructure Specification — Binary Options Quantitative Strategy Simulator & Optimization Engine

## 1. Project Overview & Opaque-Box Testing Philosophy

### 1.1 Project Title
**Binary Options Quantitative Strategy Simulator & Optimization Engine**

### 1.2 Opaque-Box Testing Philosophy
The E2E testing framework follows a strict **opaque-box (black-box) testing methodology**. Tests are constructed entirely from specification contracts (`PROJECT.md`, module signatures, and expected mathematical/financial invariants) without relying on internal implementation private details. 

Key principles of our opaque-box methodology:
- **Specification-Driven Validation**: Inputs and expected outputs are specified based on public interface contracts (`run`, `run_multi_asset`, `extract_features`, `filter_signals`, `run_verification`).
- **Temporal Causality & Zero-Leakage Guarantee**: Verification guarantees that no future information leaks into indicator calculations, regime states, meta-filter thresholds, or cross-validation splits.
- **Invariant Enforcement**: System invariants (e.g., non-negative capital, exact win-rate calculations, trade timestamp ordering, tie-rule execution) are strictly asserted across all tiers.

### 1.3 Test Runner Framework
- **Test Runner**: `pytest` (v7.4+)
- **Configuration File**: `pytest.ini`
- **Execution Scopes**: Automated unit, integration, and E2E test discovery in `tests/` and `test_high_winrate_mechanisms.py`.
- **Exclusion Paths**: `scratch/`, `.agents/`, `data/`.

---

## 2. Four-Tier Testing Methodology

The testing architecture is organized into four complementary test tiers:

### Tier 1: Category-Partition Methodology
- **Description**: Systematic partitioning of input parameter domains into discrete categories and equivalence classes (e.g. signal types `['CALL', 'PUT', 'HOLD']`, tie rules `['RETURN_STAKE', 'LOSS']`, capital modes `['SIMPLE', 'REINVESTMENT', 'BARBELL']`).
- **Threshold**: Minimum of **5 test cases per feature**.

### Tier 2: Boundary Value Analysis (BVA) Methodology
- **Description**: Focused testing at domain boundaries, edge cases, and extreme inputs (e.g. empty DataFrames, single-row data, zero volume, zero returns, price ties, extreme slippage, NaN values, exact probability threshold limits).
- **Threshold**: Minimum of **5 boundary test conditions per feature**.

### Tier 3: Pairwise Testing Methodology
- **Description**: Combinatorial testing using pairwise (2-wise) orthogonal matrices to cover multi-parameter interaction spaces (e.g., combining timeframes × expiry candles × meta-filter thresholds × capital allocation modes).
- **Threshold**: Complete pairwise interaction coverage across all strategy, simulator, and optimization parameters.

### Tier 4: Real-World Workload Testing Methodology
- **Description**: End-to-end integration scenarios simulating realistic trading environments, multi-asset portfolios, regime switches, hyperparameter tuning runs, and walk-forward evaluations under real market dynamics.
- **Threshold**: Minimum of **9 end-to-end workload application scenarios**.

---

## 3. Full Feature Inventory & Four-Tier Mapping

The table below maps all 18 core features from `PROJECT.md` across Tiers 1, 2, 3, and 4.

| Feature # | Feature Name | Tier 1 (Category-Partition) | Tier 2 (Boundary Value Analysis) | Tier 3 (Pairwise Testing) | Tier 4 (Real-World Workloads) |
|---|---|---|---|---|---|
| 1 | BinarySimulator Tie Rule Consistency | Categories: `RETURN_STAKE` vs `LOSS`, single vs multi-asset | Price delta == 0.0, floating point epsilon boundaries (`1e-8`) | Tie rules × Expiry candles × Asset count | Real-world Quote/Deriv broker payout simulation |
| 2 | Multi-Asset Barbell State Tracking | Modes: `BARBELL` vs `SIMPLE`, streak reset triggers | 100% drawdown of bullet, zero remaining bullets, max target reached | Barbell risk ratio × Target ratio × Bet fraction | Multi-asset Barbell campaign cycle simulation |
| 3 | FracDiff FFT Acceleration | Differencing parameters `d` in `[0.0, 1.0]`, window sizes | Single row, zero variance, NaN values, threshold boundaries | Differentiation `d` × Series length × FFT window | High-frequency 500k-row indicator generation |
| 4 | RegimeDetector & CUSUM Memory/Pause Fix | Regime states `[0, 1]`, CUSUM status `['ACTIVE', 'PAUSE']` | Zero volatility series, constant loss streak, window overflow | Expected WR × Payout × CUSUM window | Dynamic market regime shift & drawdown pause |
| 5 | MetaLabeler Timestamp & Leakage Fix | Timestamp types (unix s vs ms), label threshold partitions | Single timestamp, overflow ms timestamps, rolling window boundary | Timestamp format × Rolling window × Threshold | Multi-year high-precision timestamp dataset |
| 6 | Walk-Forward Efficiency Metric Fix | IS vs OOS window ratios, trade counts (`N=0` vs `N>0`) | 0 OOS trades, 1 OOS trade, negative efficiency ratios | Window sizes × Embargo periods × Fold counts | Rolling walk-forward efficiency validation |
| 7 | Target Expiry Label Alignment | Expiration offsets (1 to 12 candles), call/put shifts | Index boundaries at end of DataFrame, 1-candle expiry | Expiry candles × Strategy signals × Shift logic | Full-horizon label alignment verification |
| 8 | Feature Scaling & Threshold Leakage Elimination | Rolling vs global feature scalers, dynamic quantile thresholds | Single-window data, extreme outliers, zero variance features | Scaling method × Rolling window × Quantile | In-sample only feature scaling & transform |
| 9 | HMM Forward-Only Probability State Estimation | Forward filter probabilities vs Viterbi sequence decoding | Transition matrix degeneracies, zero initial probability | HMM components × Covariance type × Sequence len | Real-time online forward regime classification |
| 10 | Purged CV Integration | PurgedGroupTimeSeriesSplit fold splits, embargo lengths | Zero embargo, overlap larger than train window | Group size × Purge window × Embargo ratio | Cross-validation with temporal embargo |
| 11 | Capital State Split Isolation | IS vs OOS equity tracking, independent state reset | Zero IS capital, balance reset across fold boundaries | Capital mode × Fold count × Split ratio | Multi-period isolated backtest simulation |
| 12 | Optuna Framework Integration | TPE sampler vs Random sampler, hyperparameter search spaces | Trial pruner triggers, 0 valid trials, trial budget limits | Sampler type × Pruner × Trial count | Automated hyperparameter tuning pipeline |
| 13 | Multi-Dimensional Search Space Design | Search parameters: timeframes, expirations, indicators | Parameter upper/lower bounds, step size boundaries | Timeframe × Expiry × Indicator range | Complex parameter grid exploration |
| 14 | True Walk-Forward Optimization Engine | Rolling IS training vs OOS testing cycles | Single-fold data, non-overlapping windows, fold boundaries | IS window size × OOS window size × Step size | Multi-year walk-forward strategy evaluation |
| 15 | Backtest Engine Parallel Vectorization | Serial vs vectorized execution modes | Single-thread fallback, batch size boundaries | Vectorization mode × Thread count × Batch size | High-throughput parallel backtesting |
| 16 | Formal `tests/` Directory & `pytest.ini` Setup | Test discovery patterns, path exclusions (`scratch/`) | Empty test modules, syntax edge cases in conftest | Test scope × Config flags × Python versions | Full test suite execution harness |
| 17 | Integrity & Causality Test Suite Expansion | Look-ahead cheating assertions, future leakage tests | Shift -1 look-ahead detection, unshifted indicator usage | Test category × Signal generator × Data source | Zero-cheating verification audit suite |
| 18 | Executable Backtest Verification Script | Output schema assertions: Win Rate > 65%, EV > 0.0 | Boundary win rate (65.0%), Wilson lower bound checks | Strategy config × Asset universe × Seed | Full end-to-end empirical verification script |

---

## 4. Test Architecture & Fixture Design

### 4.1 Test Runner Invocation
Tests are executed using `pytest` from the workspace root:
```bash
pytest
```
Specific test suites can be targeted:
```bash
pytest tests/
pytest test_high_winrate_mechanisms.py
```

### 4.2 Reusable Fixtures (`tests/conftest.py`)
The `tests/conftest.py` module exposes standard, deterministic fixtures and data generator helpers:

1. `synthetic_ohlcv_df`: Returns a deterministic 500-row pandas DataFrame containing realistic OHLCV prices (`open`, `high`, `low`, `close`, `volume`, `open_time`) and timestamp index.
2. `multi_asset_ohlcv_dict`: Returns a dictionary mapping asset symbols (`'EURUSD'`, `'GBPUSD'`, `'USDJPY'`) to synthetic OHLCV DataFrames.
3. `base_signals_series`: Returns a deterministic pandas Series of trading signals (`'CALL'`, `'PUT'`, `'HOLD'`) indexed by timestamp.

### 4.3 Boundary Data Generators (`tests/conftest.py`)
- `generate_custom_length_ohlcv(n_rows, seed)`: Generates custom length OHLCV DataFrames.
- `generate_zero_volume_ohlcv(n_rows, seed)`: Generates data with zero volume for liquidity boundary tests.
- `generate_flat_price_ohlcv(n_rows, start_price)`: Generates price series with zero volatility / flat prices.
- `generate_nan_ohlcv(n_rows, nan_ratio, cols)`: Generates data containing NaNs for missing data handling.

---

## 5. Tier 4 Real-World Application Scenarios

Below are 10 concrete real-world testing scenarios designed to evaluate end-to-end engine capabilities:

### Scenario 1: Single-Asset Standard Backtest with Tie Rule Evaluation
- **Context**: Evaluating strategy performance on EURUSD 1-minute data under Quotex (`RETURN_STAKE`, PnL=0) vs Deriv (`LOSS`, PnL=-bet) broker rules.
- **Workflow**: Generate signals -> Execute `BinarySimulator.run()` with `tie_rule='RETURN_STAKE'` and `tie_rule='LOSS'` -> Validate gross vs effective win rate, net PnL, and max drawdown.
- **Assertion**: Effective win rate excludes ties under `RETURN_STAKE`, whereas `LOSS` counts ties as losses.

### Scenario 2: Multi-Asset Barbell Capital Allocation & Campaign Reset
- **Context**: Simulating high-yield Barbell allocation across a 3-asset universe (`EURUSD`, `GBPUSD`, `USDJPY`).
- **Workflow**: Initialize $1,000 capital ($800 core, $200 risk budget split into 5 bullets) -> Run multi-asset simulation -> Trigger consecutive wins to reach target threshold ($1,000 risk cap) -> Consolidate profits into safe core -> Simulate loss streak to trigger bullet replenishment.
- **Assertion**: Core capital remains protected during drawdowns; consecutive win streaks trigger exact profit consolidation.

### Scenario 3: Multi-Asset Inter-Class Execution Filtering & Daily Duplicate Blocking
- **Context**: Preventing over-exposure by limiting trading execution to at most one trade per asset class per day.
- **Workflow**: Generate simultaneous `CALL` signals on forex pairs (`EURUSD`, `GBPUSD`) on the same day -> Execute `run_multi_asset()` -> Inspect trades list.
- **Assertion**: Only the first trade of the asset class is executed on any given day; subsequent same-class signals are blocked.

### Scenario 4: Dynamic Market Regime Gating (HMM + CUSUM Pause/Resume)
- **Context**: Gating trading signals when market regime switches to high-volatility or when CUSUM detects strategy performance degradation.
- **Workflow**: Pass OHLCV data through `RegimeDetector` -> Feed execution results to `CUSUMMonitor` -> Simulate 15 consecutive losses -> Observe status change to `PAUSE`.
- **Assertion**: Signals are suppressed when `should_trade()` returns False; CUSUM state transitions cleanly from `ACTIVE` to `PAUSE`.

### Scenario 5: MetaLabeler Probability Gating & Volatility Squeeze Adaptive Filtering
- **Context**: Filtering raw strategy signals using secondary ML meta-labeling and NATR volatility squeeze adjustments.
- **Workflow**: Extract features with `BinaryFeatureExtractor` -> Fit `MetaLabeler` -> Apply `BinaryMLMetaFilter` with adaptive thresholding based on NATR -> Validate filtered signals.
- **Assertion**: Threshold dynamically increases during high NATR periods; low-probability setups are filtered out.

### Scenario 6: High-Throughput Optuna Hyperparameter Optimization
- **Context**: Tuning strategy parameters (RSI period, Bollinger std, NATR threshold) using Optuna TPE Bayesian optimization.
- **Workflow**: Define multi-dimensional search space -> Launch Optuna study -> Evaluate trials against OOS Win Rate and Expected Value metrics -> Assert pruner cuts unpromising trials.
- **Assertion**: Optuna completes requested trials, returns optimal parameter set with OOS Win Rate > 65%.

### Scenario 7: Purged Group Time Series Split Walk-Forward Optimization
- **Context**: Cross-validating strategy performance using `PurgedGroupTimeSeriesSplit` with temporal purging and embargo to eliminate overlap leakage.
- **Workflow**: Partition dataset into 5 groups -> Apply purge window equal to expiry candles and embargo window of 10 candles -> Perform rolling IS training and OOS testing -> Compute Walk-Forward Efficiency (WFE).
- **Assertion**: Zero temporal index overlap between train and test sets; WFE calculated accurately without division-by-zero errors.

### Scenario 8: Vectorized FracDiff Feature Extraction on High-Frequency Data
- **Context**: Calculating Lópes de Prado Fractional Differentiation (FFD) across multi-timeframe OHLCV datasets.
- **Workflow**: Extract stationary fractional series using `frac_diff_fixed` with `scipy.signal.fftconvolve` acceleration -> Check stationarity and memory retention.
- **Assertion**: Output series length matches input length; no NaNs beyond initial window; execution time scales linearly.

### Scenario 9: In-Sample vs. Out-Of-Sample Capital Isolation & Wilson Confidence Bound
- **Context**: Verifying that capital state and feature scalers do not leak from In-Sample (IS) training into Out-Of-Sample (OOS) testing periods.
- **Workflow**: Split data chronologically into IS (70%) and OOS (30%) -> Fit scalers on IS only -> Simulate trading on OOS with isolated capital state -> Calculate Wilson 95% lower confidence bound on OOS Win Rate.
- **Assertion**: OOS initial capital starts at specified base amount regardless of IS final equity; Wilson lower bound exceeds statistical chance (50%).

### Scenario 10: End-to-End Execution & Empirical OOS Win Rate Attestation
- **Context**: Running full backtest verification pipeline (`verify_high_winrate_oos.py`).
- **Workflow**: Execute end-to-end verification harness -> Run feature extraction, strategy signal generation, meta-filtering, backtest simulation, and statistical attestation.
- **Assertion**: Summary output validates OOS Win Rate > 0.65, Expected Value per trade > 0.0, zero causality violations, and 0 test failures/warnings.

---

## 6. Coverage Thresholds & Quality Criteria

| Tier | Methodology | Minimum Coverage Requirement | Verification Metric |
|---|---|---|---|
| **Tier 1** | Category-Partition | >= 5 test cases per feature | 100% feature coverage across parameter partitions |
| **Tier 2** | Boundary Value Analysis | >= 5 boundary tests per feature | Zero unhandled edge-case exceptions / NaNs / zero divisions |
| **Tier 3** | Pairwise Testing | Full orthogonal interaction matrix | 100% pairwise parameter combination coverage |
| **Tier 4** | Real-World Workloads | >= 9 end-to-end application scenarios | 10 Scenarios passing with Win Rate > 65% & EV > 0.0 |
