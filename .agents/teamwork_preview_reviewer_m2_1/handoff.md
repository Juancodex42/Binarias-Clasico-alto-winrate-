# Milestone 2 Review & Handoff Report — Reviewer 1

## 1. Observation

Direct code and test observations from Milestone 2 feature review:

- **Feature 7: Target Expiry Label Alignment**
  - Path: `optimizer_grid_search.py:47-62` and `run_backtest_comparison.py:16-31`
  - Observation: `create_labels` calculates `entry_prices = df['open'].shift(-1)` (or `open[i+1]`) and `exit_prices = df['close'].shift(-expiry_candles)` (or `close[i+expiry_candles]`), matching `BinarySimulator.run` (`engine/simulator.py:76, 85`).
  - **Defect / Side Effect**: Top-level code in `optimizer_grid_search.py:16-26` monkey-patches `BinaryFeatureExtractor.extract_features` with `cached_extract_features` at module load time:
    ```python
    orig_extract = BinaryFeatureExtractor.extract_features
    _feature_cache = {}

    def cached_extract_features(df):
        key = (len(df), df.iloc[0]['open'] if len(df) > 0 else 0)
        if key not in _feature_cache:
            _feature_cache[key] = orig_extract(df)
        return _feature_cache[key]

    BinaryFeatureExtractor.extract_features = staticmethod(cached_extract_features)
    ```
    When `test_tier1_feature_coverage.py:24` imports `from optimizer_grid_search import create_labels`, this global monkey patch is executed for the entire process.

- **Feature 8: Feature Scaling & Threshold Leakage Elimination**
  - Path: `strategies/volatility_squeeze_ml.py:109-112`, `engine/ml_engine/meta_filter.py:70-71`, `engine/auto_tuner.py:194`
  - Observation: Global quantile clipping was replaced with backward rolling quantiles (`rolling(200, min_periods=20).quantile(...)` in `volatility_squeeze_ml.py`). Dataset-wide median in `meta_filter.py` was replaced with rolling median (`natr_series.rolling(100, min_periods=1).median()`). `DynamicRegimeAdapter.detect_regime` computes rolling median on historical data up to `at_index`.

- **Feature 9: HMM Forward-Only Probability State Estimation**
  - Path: `engine/ml_engine/regime_detector.py:94-127`
  - Observation: Replaced Viterbi global decoding with `predict_forward_proba()` which computes $P(S_t = k | O_{1:t})$ using forward log-recursion $\alpha_t(j)$ and per-step log-sum-exp normalization without using future observations ($O_{t+1:T}$).

- **Feature 10: Purged CV Integration**
  - Path: `engine/ml_engine/purged_cv.py:15-27`, `engine/auto_tuner.py:35-38`, `optimizer_grid_search.py:86-89`, `run_backtest_comparison.py:64-67`
  - Observation: `PurgedGroupTimeSeriesSplit.purge_embargo_split()` purges trade overlap (`is_end = max(0, raw_split - expiry_candles)`) and applies embargo (`oos_start = min(n_samples, raw_split + embargo_offset)`).

- **Feature 11: Capital State Split Isolation**
  - Path: `engine/optimizer.py:528-605`
  - Observation: `optimize_daily_confluence_stream` splits universe data into `universe_is` and `universe_oos` via `purge_embargo_split` and invokes `sim.run_multi_asset` independently for IS and OOS with fresh `initial_capital=1000.0`, isolating capital tracking.

- **Test Suite Execution Results**:
  - `pytest tests/`: FAILS on `tests/test_tier1_feature_coverage.py::TestFeature05_MetaLabelerTimestampLeakage::test_f05_metalabeler_ms_timestamp_parsing`.
  - Isolated test run: `python -m pytest tests/test_tier1_feature_coverage.py -k test_f05_metalabeler_ms_timestamp_parsing` -> PASSED (1 passed in 44.82s).

## 2. Logic Chain

1. Features 7, 8, 9, 10, and 11 feature code implementations are mathematically sound and correctly satisfy temporal causality and zero leakage requirements.
2. However, `optimizer_grid_search.py` executes global monkey-patching of `BinaryFeatureExtractor.extract_features` at top-level module import.
3. The cache key `(len(df), df.iloc[0]['open'])` is non-unique and collides across different DataFrames with identical row count and initial open price.
4. When `test_tier1_feature_coverage.py` imports `create_labels` from `optimizer_grid_search.py`, `BinaryFeatureExtractor.extract_features` is globally corrupted.
5. In full test suite runs (`pytest tests/`), earlier tests populate the cache, causing `test_f05_metalabeler_ms_timestamp_parsing` to receive wrong cached features with mismatched index timestamps, triggering test failure.
6. Acceptance criteria require unit test suite (`pytest tests/` and `python -m unittest discover -s tests`) to execute with 0 failures and zero unintended side-effects.

## 3. Caveats

No caveats. All M2 features and test suites were fully inspected and verified.

## 4. Conclusion

**Verdict**: `REQUEST_CHANGES`

### Findings

#### [Major] Finding 1: Global Side-Effect & Test Failure in `optimizer_grid_search.py`
- **What**: Top-level code in `optimizer_grid_search.py:16-26` monkey-patches `BinaryFeatureExtractor.extract_features` globally with a non-unique cache key.
- **Where**: `optimizer_grid_search.py:16-26`
- **Why**: Importing `optimizer_grid_search` pollutes the process global state, breaking `test_f05_metalabeler_ms_timestamp_parsing` during full `pytest tests/` runs.
- **Suggestion**: Move the monkey-patching logic inside `if __name__ == '__main__':` or `main()` in `optimizer_grid_search.py`.

#### [Major] Finding 2: Full Unit Test Suite Failure
- **What**: `pytest tests/` fails when run across the entire suite due to Finding 1.
- **Where**: `tests/test_tier1_feature_coverage.py`
- **Why**: M1/M2 acceptance criteria require all unit tests to pass cleanly.
- **Suggestion**: Resolve Finding 1 and re-verify that `pytest tests/` passes with 0 failures.

## 5. Verification Method

- Run `pytest tests/` and verify 0 failures.
- Run `python -m unittest discover -s tests`.
- Inspect `optimizer_grid_search.py:16-26` to confirm monkey-patching is scoped inside `if __name__ == '__main__':`.
