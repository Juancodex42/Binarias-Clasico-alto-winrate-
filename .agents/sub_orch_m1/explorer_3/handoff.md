# Handoff Report — explorer_3 (ML Engine Bug Remediation Analysis)

**Task:** Item 3 (`RegimeDetector`, `CUSUMMonitor`) & Item 4 (`MetaLabeler`, `BinaryMLMetaFilter`) Investigation  
**Working Directory:** `c:\Users\juanc\Desktop\prueba\.agents\sub_orch_m1\explorer_3`  
**Target Code Files:**
- `engine/ml_engine/regime_detector.py`
- `engine/ml_engine/cusum_monitor.py`
- `engine/ml_engine/meta_labeler.py`
- `engine/ml_engine/meta_filter.py`

---

## 1. Observation

Direct code observations from inspecting the target files line-by-line:

### 1.1 `RegimeDetector` (`engine/ml_engine/regime_detector.py`)
- **Location:** Line 41 in `_prepare_observations`:
  ```python
  feat_vol = returns.rolling(20).std().fillna(returns.std()).values
  ```
- **Observed Behavior:** `.fillna(returns.std())` calculates standard deviation over the full sample series of `returns`, populating the first 19 observations of `feat_vol` with future sample statistics.

### 1.2 `CUSUMMonitor` (`engine/ml_engine/cusum_monitor.py`)
- **Location A:** Lines 23, 27, 36, 60–65 in `__init__` and `update`:
  ```python
  self.trade_results = []
  self.pause_history = []
  self.trade_results.append(trade_pnl)
  ```
  `self.trade_results` and `self.pause_history` are unbounded lists that append items on every trade/event without any size limit.
- **Location B:** Lines 68–82 in `update`:
  ```python
  if self.is_paused:
      recent_short = self.trade_results[-10:]
      recent_wr = sum(1 for r in recent_short if r > 0) / len(recent_short)
      if recent_wr >= self.expected_wr:
          ...
  ```
  When paused, `self.trade_results[-10:]` inspects trades that include the losing streak that triggered the pause. No separate post-pause trade tracking exists, causing recovery evaluation to lock up.

### 1.3 `MetaLabeler` (`engine/ml_engine/meta_labeler.py`)
- **Location:** Line 47 in `_extract_context_features`:
  ```python
  times = pd.to_datetime(df.loc[signal_indices, 'open_time'], unit='s', errors='coerce')
  ```
- **Observed Behavior:** Timestamp conversion hardcodes `unit='s'`. When passed epoch timestamps in milliseconds (e.g. `1672531200000`), `pd.to_datetime` overflows to year 54965 AD and `errors='coerce'` produces `NaT` for all rows. Line 48 (`if not times.isna().all()`) evaluates to `False`, silently dropping `hour_of_day`, `day_of_week`, and `is_session_overlap`.

### 1.4 `BinaryMLMetaFilter` (`engine/ml_engine/meta_filter.py`)
- **Location:** Lines 70–71 in `filter_signals`:
  ```python
  current_natr = X['natr'].iloc[-1] if len(X) > 0 else 0
  median_natr = X['natr'].median() if len(X) > 0 else 0
  ```
- **Observed Behavior:** `X['natr'].median()` calculates global median across the entire DataFrame `X`, introducing future data leakage into adaptive threshold calculations. `X['natr'].iloc[-1]` samples only the last row of `X` rather than NATR at each active signal index.

---

## 2. Logic Chain

1. **HMM Look-Ahead Leakage Reasoning:**
   - Observation: `returns.std()` computes full-sample variance across the entire DataFrame passed to `_prepare_observations`.
   - Step 1: In backtesting/walk-forward evaluation, the DataFrame contains historical bars up to time $T$.
   - Step 2: Filling NaNs at bars $0..18$ with full-sample std injects statistics from bars $19..T$ into bars $0..18$.
   - Conclusion: `returns.rolling(20, min_periods=1).std().fillna(0.0)` guarantees zero look-ahead bias by using only past returns at each bar $t$.

2. **CUSUM Memory & Deadlock Reasoning:**
   - Observation: Memory arrays grow continuously while pause recovery evaluates `self.trade_results[-10:]`.
   - Step 1: Unbounded array appends in long-running processes cause memory degradation.
   - Step 2: During a pause, `self.trade_results[-10:]` retains pre-pause losing trades. As new paper trades are appended, pre-pause losses remain in the 10-trade window, preventing `recent_wr` from reaching `expected_wr`.
   - Conclusion: Track integer counters, cap array sizes (deque / slice max 1000), evaluate recovery strictly over `post_pause_results`, and provide a `reset()` method.

3. **Timestamp Overflow Reasoning:**
   - Observation: Millisecond timestamps ($> 10^{11}$) converted with `unit='s'` overflow to year > 50000 AD.
   - Step 1: `errors='coerce'` turns overflowed dates to `NaT`.
   - Step 2: `if not times.isna().all()` fails, skipping temporal feature calculation.
   - Conclusion: Dynamically detect timestamp units (`'s'`, `'ms'`, `'us'`, `'ns'`) based on numeric magnitude ($> 1e11 \to \text{ms}$, $> 1e14 \to \text{us}$, $> 1e17 \to \text{ns}$) or datetime dtype.

4. **Meta-Filter Leakage Reasoning:**
   - Observation: `X['natr'].median()` uses all rows of `X`, while `iloc[-1]` grabs the final bar NATR.
   - Step 1: Computing median across all rows leaks future NATR distribution into early trade filtering decisions.
   - Step 2: Using `.iloc[-1]` applies the last bar's NATR state to past signals.
   - Conclusion: Use a rolling backward window median `X['natr'].rolling(100, min_periods=1).median()` and evaluate `current_natr` at each signal's exact bar index `idx`.

---

## 3. Caveats

- **HMM Model Fit Dependency:** `RegimeDetector` requires `hmmlearn` installed. If missing, it gracefully falls back to passthrough mode.
- **CUSUM Paper Trading Input:** `CUSUMMonitor` pause recovery requires that strategy loops feed shadow/paper trade results into `update(trade_pnl)` while `is_paused` is `True`, or invoke `reset()` upon regime recovery.
- **NATR Feature Availability:** `BinaryMLMetaFilter` adaptive thresholding requires `'natr'` column present in feature DataFrame `X`. If missing, base threshold is maintained.

---

## 4. Conclusion

All 4 ML Engine modules have clear, deterministic fixes that eliminate look-ahead bias, memory leaks, pause deadlocks, timestamp overflows, and global median data leakage while preserving mathematical correctness and backward compatibility.

### Summary of Fix Specifications for Implementer:
1. `engine/ml_engine/regime_detector.py`: Replace `returns.rolling(20).std().fillna(returns.std()).values` with `returns.rolling(20, min_periods=1).std().fillna(0.0).values`.
2. `engine/ml_engine/cusum_monitor.py`: Bound `trade_results` (max 1000) and `pause_history` (max 100), maintain `total_trades_count` and `pause_count`, track `post_pause_results` for clean pause recovery, add explicit `reset()` method.
3. `engine/ml_engine/meta_labeler.py`: Add `parse_timestamps` helper to handle datetime dtypes and numeric timestamps across seconds, milliseconds, microseconds, and nanoseconds.
4. `engine/ml_engine/meta_filter.py`: Replace global median and `.iloc[-1]` with `rolling_median = X['natr'].rolling(100, min_periods=1).median()` and evaluate `current_natr` and `median_natr` per active signal index `idx`.

---

## 5. Verification Method

To verify the fixes independently:

1. **Run Unit Test Suite:**
   Execute command via shell:
   ```powershell
   python -m unittest test_high_winrate_mechanisms.py
   ```
2. **Execute CUSUM & HMM Integrity Test:**
   Inspect test output to ensure 0 failures and 0 errors.
3. **Invalidation Conditions:**
   - `test_regime_detector` producing `NaN` or accessing future timestamps.
   - `test_cusum_monitor` staying trapped in `PAUSED` state when fed winning paper trades post-pause.
   - `test_meta_labeler` returning `NaN` for `hour_of_day` when passed millisecond timestamp series.
   - `test_meta_filter` outputting different threshold values depending on future rows appended to `X`.
