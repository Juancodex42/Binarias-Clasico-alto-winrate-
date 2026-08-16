# Test Suite & Verification Infrastructure Survey Report

**Agent**: `teamwork_preview_explorer_survey_3`  
**Date**: 2026-08-12  
**Target Workspace**: `c:\Users\juanc\Desktop\prueba`  

---

## Executive Summary
This survey provides a comprehensive audit of the test suite, test execution harness, dependency environment, coverage gaps, and verification requirements for the Binary Options Quantitative Strategy Simulator and Optimization Engine.

Key Findings:
1. **Existing Unit Test Suite**: `test_high_winrate_mechanisms.py` exists at project root and passes 5/5 unit tests (`python -m unittest test_high_winrate_mechanisms.py` completes in 0.041s).
2. **Test Harness & Pytest Discovery Conflict**: Executing `pytest` without parameters causes pytest to automatically discover ad-hoc scratch scripts under `scratch/` (such as `scratch/test_flask_routes.py`, `scratch/test_stream.py`, and `scratch/test_stuck.py`). These scripts contain interactive server requests, heavy grid searches, and Monte Carlo runs, causing unconfigured `pytest` runs to hang or fail.
3. **Scatter of Scratch Verification Scripts**: Significant verification and audit logic is present across ~18 scratch scripts in `scratch/` (e.g. `audit_zero_cheating.py`, `test_fixes.py`, `verify_all_audit_fixes.py`, `test_high_winrate_suite.py`, `test_strategy_export.py`).
4. **Coverage Gaps & Requirements**: A formal `tests/` directory is missing. Verification of key requirements R1 (bug fixes in quantitative engine), R2 (exploration of high win-rate >65% and positive EV configurations), and R3 (strict causality, zero look-ahead bias, Wilson score bounds, tie handling) needs to be consolidated into a clean, reproducible test and verification suite.

---

## 1. Observation

### 1.1 Complete Inventory of Test & Verification Files

#### Primary Unit Test File (Root)
- `c:\Users\juanc\Desktop\prueba\test_high_winrate_mechanisms.py` (75 lines)

#### Scratch Test & Audit Files (`c:\Users\juanc\Desktop\prueba\scratch\`)
- `scratch/test_high_winrate_suite.py` (130 lines): Tests simulator overlapping, ML meta filter (Purged CV), and regime gating.
- `scratch/test_fixes.py` (62 lines): Tests BARBELL TIE release and Wilson score lower-bound adjustment in `CapitalOptimizer`.
- `scratch/test_flask_routes.py` (51 lines): Integration test for Flask endpoints (`/api/strategies`, `/api/backtest`, `/api/smart-optimize`).
- `scratch/test_ml_threshold_curve.py` (97 lines): Tests ML probability thresholds (0.55 to 0.85) on top CSV datasets.
- `scratch/test_squeeze.py` (39 lines): Tests Bollinger squeeze expansion signals across 5 crypto/forex pairs.
- `scratch/test_strategy_export.py` (128 lines): Audits exporter outputs (JSON schema, standalone Python code parity, PineScript v5).
- `scratch/test_stream.py` (27 lines): Script testing HTTP streaming endpoint `http://127.0.0.1:5001/api/smart-optimize-v2-stream`.
- `scratch/test_stuck.py` (104 lines): Performance test running 11-asset data loading, daily confluence stream, and 5000-run Monte Carlo.
- `scratch/test_ui_fix.py` (27 lines): Verification script for `ISLG_RS` and `ClimaxReversal` strategy effective win rates.
- `scratch/test_verification.py` (42 lines): Verification script testing 5 genetic strategy profiles across multi-asset universe.
- `scratch/verify_all_audit_fixes.py` (91 lines): Verification of strategy signatures, `prepare_data` dict outputs, 0-volume Forex fallback, and float epsilon TIE rules.
- `scratch/verify_fixes.py` (36 lines): Verification of `CapitalOptimizer` target achievable flag, `StatisticsEngine` empty input handling, and strategy parameter schemas.
- `scratch/audit_zero_cheating.py` (72 lines): Verifies timestamp monotonicity and confirms trade entries execute strictly on `Open[i+1]` following signal candle `i` (Zero Lookahead Bias).
- `scratch/audit_strategies.py` (94 lines): Batch audit testing default strategy parameters across 8 raw datasets.
- `scratch/audit_full_ui_pipeline.py` (51 lines): End-to-end audit calling `/api/smart-optimize-v2` via Flask test client.
- `scratch/run_full_backtest_audit.py` (166 lines): Comprehensive multi-asset and single-asset backtest runner exporting results to `scratch/backtest_results.json`.
- `scratch/fast_robust_backtest.py` & `scratch/robust_backtest_runner.py`: Additional backtest automation utilities.

---

### 1.2 Dissection of `test_high_winrate_mechanisms.py`

File Path: `c:\Users\juanc\Desktop\prueba\test_high_winrate_mechanisms.py`

- **Line 1-12**: Imports `unittest`, `pandas`, `numpy`, and engine components (`BinaryFeatureExtractor`, `CUSUMMonitor`, `MetaLabeler`, `RegimeDetector`, `BinaryMLMetaFilter`, `frac_diff_fixed`).
- **Line 14-30 (`setUp`)**: Generates 200 bars of synthetic 5-minute OHLCV data using `np.random.seed(42)`.
- **Line 32-35 (`test_frac_diff_fixed`)**: Checks fractional differentiation output length equals input length and is not all NaN.
- **Line 37-48 (`test_cusum_monitor`)**: Simulates 15 consecutive negative returns (`update(-1.0)`). Asserts monitor status is `'PAUSE'` or `'PAUSED'`, `should_trade()` returns `False`, and `is_paused` is `True`.
- **Line 50-54 (`test_meta_labeler_instantiation`)**: Checks presence of `fit` and `filter` methods on `MetaLabeler`, and verifies `is_fitted` starts as `False`.
- **Line 56-60 (`test_regime_detector_instantiation`)**: Checks presence of `fit`, `get_current_state`, and `should_trade` methods on `RegimeDetector`.
- **Line 62-71 (`test_meta_filter_adaptive`)**: Instantiates `BinaryMLMetaFilter(probability_threshold=0.65, adaptive_threshold=True)`, passes synthetic NATR feature data, calls `filter_signals`, and asserts `probability_threshold > 0.65`.

**Execution Result**:
```
python -m unittest test_high_winrate_mechanisms.py
.....
----------------------------------------------------------------------
Ran 5 tests in 0.041s
OK
```

---

### 1.3 Test Execution Environment & Dependencies

- **Python Version**: Python 3.11 (bytecode compiled with `cpython-311`).
- **Test Frameworks**:
  - `pytest` (7.4.3 installed)
  - `pytest-cov` (4.1.0 installed)
  - `pytest-asyncio` (0.21.1 installed)
  - `unittest` (Standard Library)
- **Key Installed Packages**:
  - `pandas` (2.0.3)
  - `numpy` (1.26.4)
  - `scipy` (1.11.4)
  - `scikit-learn` (1.3.2)
  - `Flask` (3.1.2), `Werkzeug` (3.1.4)
  - `statsmodels` (0.14.6)
  - `hmmlearn` (0.3.3)

#### Why Default `pytest` Fails/Hangs
When `pytest` is invoked without restricting paths (e.g., `python -m pytest`), pytest scans the root and `scratch/` directory. It discovers all files matching `test_*.py`:
1. `scratch/test_stream.py`: Tries to connect to `http://127.0.0.1:5001/api/smart-optimize-v2-stream`. Fails with `URLError: connection refused` if server is not running.
2. `scratch/test_flask_routes.py` & `scratch/audit_full_ui_pipeline.py`: Post to `/api/smart-optimize`, launching GA multi-generation optimization runs.
3. `scratch/test_stuck.py`: Loads 11 datasets, computes correlation matrix, generates signals, runs multi-asset simulation, and performs a 5,000-run Monte Carlo campaign.

**Root Cause**: Absence of a `pytest.ini` configuration file defining `testpaths = tests` and ignoring `scratch/`.

---

## 2. Logic Chain

1. **Observation**: `test_high_winrate_mechanisms.py` passes 5 unit tests in 0.041s, but only performs basic method existence and smoke checks for ML engine components.
   - **Inference**: While `test_high_winrate_mechanisms.py` satisfies basic sanity checks, it does not verify mathematical accuracy, Out-Of-Sample (OOS) Win Rate > 65%, Positive Expected Value (EV), or zero look-ahead bias.

2. **Observation**: Key verification logic is currently scattered across ad-hoc scratch files in `scratch/`:
   - Zero look-ahead bias execution timing is verified in `scratch/audit_zero_cheating.py` (lines 43-68: trade entry is at `Open[i+1]` after signal at candle `i`).
   - Price TIE float epsilon handling is verified in `scratch/verify_all_audit_fixes.py` (lines 59-75) and `scratch/test_fixes.py` (lines 15-48).
   - Wilson score 95% lower bound adjustment is verified in `scratch/test_fixes.py` (lines 50-57).
   - Standalone Python code generation and parity are verified in `scratch/test_strategy_export.py` (lines 78-108).
   - Multi-asset strategy evaluation is in `scratch/run_full_backtest_audit.py` and `scratch/test_verification.py`.

3. **Observation**: Pytest discovery includes files in `scratch/` which contain non-standard test code (socket calls, long-running GA optimizations, streaming tests).
   - **Inference**: Running `pytest` across the repository requires a dedicated `tests/` directory and a `pytest.ini` config file to isolate true unit/integration tests from scratch audit scripts.

4. **Inference / Requirement for Task**:
   - To achieve the acceptance criteria set in `ORIGINAL_REQUEST.md`, a consolidated, formal test suite and executable verification/backtest script must be built.

---

## 3. Caveats

1. **Unstructured Scratch Tests**: High-value audit tests (such as zero look-ahead verification in `audit_zero_cheating.py`) exist only as standalone runnable scripts without standard `pytest` or `unittest` assertions.
2. **Data Dependencies**: Some scratch scripts depend on real CSV data files in `data/` and `data/raw/` (e.g. `BTCUSDT_1d.csv`, `EURUSD_1d.csv`), whereas unit tests in `test_high_winrate_mechanisms.py` use synthetic mock data (`np.random.seed(42)`). Formal unit tests should use mock data fixtures so they run fast and deterministically in any environment without external file dependencies.
3. **No Code Modifications Made**: Per agent constraints, no source code or non-metadata files were modified during this investigation.

---

## 4. Conclusion & Actionable Recommendations

### Conclusion
The project workspace contains a functional baseline unit test script (`test_high_winrate_mechanisms.py`) and a rich set of audit scripts in `scratch/`. However, the test infrastructure requires structure, path isolation, and expanded test assertions to fulfill all verification requirements.

### Actionable Blueprint for Implementing Agents

1. **Establish Formal Test Structure (`tests/`)**:
   Create a dedicated `tests/` directory containing modular test files:
   - `tests/test_high_winrate_mechanisms.py`: Expanded version of existing test file.
   - `tests/test_causality_zero_cheating.py`: Automated zero look-ahead bias and timestamp monotonicity tests (adapted from `scratch/audit_zero_cheating.py`).
   - `tests/test_simulator_integrity.py`: Price TIE epsilon handling, overlapping trade rules, multi-asset timestamp alignment (adapted from `scratch/test_fixes.py` and `scratch/verify_all_audit_fixes.py`).
   - `tests/test_strategies.py`: Signature compliance, `prepare_data` dict outputs, 0-volume Forex fallback, and exporter parity across all strategy classes.
   - `tests/test_statistics_optimizer.py`: Wilson 95% lower bound adjustments, CUSUM status, and streak plan calculations.

2. **Configure Pytest Harness (`pytest.ini`)**:
   Add `pytest.ini` at project root:
   ```ini
   [pytest]
   testpaths = tests test_high_winrate_mechanisms.py
   norecursedirs = scratch .agents data
   python_files = test_*.py
   ```

3. **Build Executable Verification & Backtest Script (`verify_high_winrate_oos.py`)**:
   Create a top-level verification script that:
   - Runs walk-forward backtests on recommended pairs (`NASDAQ`, `WTI`, `XAUUSD`, `GBPJPY`, `EURUSD`, `BTCUSDT`).
   - Measures Out-Of-Sample (OOS) Win Rate, effective Win Rate, Expected Value (EV) per trade, and Wilson 95% CI lower bound.
   - Asserts and reports configs meeting **OOS Win Rate > 65%** and **Positive EV per trade**.

---

## 5. Verification Method

To independently verify the observations in this report, execute the following commands in the workspace root (`c:\Users\juanc\Desktop\prueba`):

1. **Verify Existing Unit Test Suite**:
   ```powershell
   python -m unittest test_high_winrate_mechanisms.py
   ```
   *Expected Output*: 5 tests executed with `OK` in ~0.04 seconds.

2. **Verify Zero Lookahead Bias Audit Script**:
   ```powershell
   python scratch/audit_zero_cheating.py
   ```
   *Expected Output*: `[AUDIT 1] Integridad de Marcas de Tiempo: PASÓ` and `[RESULTADO AUDITORÍA] CERO TRAMPA CONFIRMADA 100%`.

3. **Verify BARBELL TIE & Wilson Lower Bound Tests**:
   ```powershell
   python scratch/test_fixes.py
   ```
   *Expected Output*: `SUCCESS: BARBELL TIE test passed cleanly!` and `ALL SYSTEM TESTS PASSED SUCCESSFULLY!`.

4. **Verify Strategy Signatures & Precomputed Dict Test**:
   ```powershell
   python scratch/verify_all_audit_fixes.py
   ```
   *Expected Output*: `ALL AUDIT VERIFICATIONS PASSED CLEANLY!`.
