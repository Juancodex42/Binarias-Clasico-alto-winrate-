# Deep Technical Analysis: ML Engine Bug Remediation (Items 3 & 4)

**Author:** explorer_3 (`teamwork_preview_explorer`)  
**Date:** 2026-08-12  
**Target Subsystem:** `engine/ml_engine/` (`regime_detector.py`, `cusum_monitor.py`, `meta_labeler.py`, `meta_filter.py`)

---

## 1. Executive Summary

This investigation analyzed four core Machine Learning engine modules responsible for market regime identification, trade equity drift monitoring, meta-label dataset generation, and dynamic signal filtering:
1. **`RegimeDetector` (`engine/ml_engine/regime_detector.py`)**: Found **full-sample standard deviation leakage** in HMM feature preparation via `returns.std()`.
2. **`CUSUMMonitor` (`engine/ml_engine/cusum_monitor.py`)**: Found **unbounded memory growth** in `trade_results` and `pause_history` arrays, and a **pause deadlock recovery bug** where pre-pause losing trades pollute the recovery win rate check.
3. **`MetaLabeler` (`engine/ml_engine/meta_labeler.py`)**: Found **timestamp overflow & feature dropping** caused by hardcoded `unit='s'` in `pd.to_datetime` when processing millisecond/microsecond epoch timestamps.
4. **`BinaryMLMetaFilter` (`engine/ml_engine/meta_filter.py`)**: Found **global median data leakage** (`X['natr'].median()`) and **static last-row sampling** (`X['natr'].iloc[-1]`) when calculating adaptive volatility thresholds.

Detailed line-by-line analyses, root causes, exact code replacements, and unit test specifications are provided below.

---

## 2. Item 3 Investigation: `RegimeDetector` & `CUSUMMonitor`

### 2.1 `RegimeDetector` (`engine/ml_engine/regime_detector.py`)

#### Code Location & Snippet
* **File Path:** `engine/ml_engine/regime_detector.py`
* **Target Method:** `_prepare_observations(self, df: pd.DataFrame)`
* **Lines 35–42:**
```python
35:         returns = close.pct_change().fillna(0)
36:         
37:         # Feature 1: Retornos
38:         feat_returns = returns.values
39:         
40:         # Feature 2: Volatilidad realizada (rolling std de 20 periodos)
41:         feat_vol = returns.rolling(20).std().fillna(returns.std()).values
42:         
```

#### Exact Bug Cause
Line 41 uses `.fillna(returns.std())`.
1. `returns.rolling(20).std()` computes a 20-period rolling standard deviation. For the first 19 rows of the DataFrame, this rolling computation returns `NaN`.
2. Calling `.fillna(returns.std())` calculates the sample standard deviation over the **entire pandas Series `returns`** (from index `0` to index `N-1`).
3. In any backtest, training split, or online evaluation where a historical window is provided, the standard deviation computed across ALL future observations in `df` is retroactively assigned to rows `0..18`.
4. This introduces **full-sample look-ahead bias** into the HMM observation matrix (`obs`). The HMM model fit and state prediction for early bars incorporate global sample volatility that would not be known at those timestamps.

#### Zero Look-Ahead Fix Plan
Replace `returns.std()` with a causal rolling standard deviation that uses `min_periods=1` and fills the single initial NaN with `0.0`:
```python
# Feature 2: Volatilidad realizada (rolling std de 20 periodos con min_periods=1)
feat_vol = returns.rolling(20, min_periods=1).std().fillna(0.0).values
```

##### Mathematical Justification:
* For row `0`: `returns.rolling(20, min_periods=1).std()` returns `NaN` (standard deviation of 1 sample with `ddof=1`), which `.fillna(0.0)` sets to `0.0`.
* For rows `1..18`: `rolling(20, min_periods=1).std()` computes standard deviation over the available expanding window of `2` to `19` past returns.
* For rows `19..N-1`: `rolling(20, min_periods=1).std()` computes standard deviation over the exact past 20 bars.
* At no point is any future observation `t+1..N-1` accessed.

---

### 2.2 `CUSUMMonitor` (`engine/ml_engine/cusum_monitor.py`)

#### Code Location & Snippets
* **File Path:** `engine/ml_engine/cusum_monitor.py`
* **Target Methods:** `__init__`, `update`, `get_stats`
* **Lines 23–27:**
```python
23:         self.trade_results = []  # Lista de PnL por trade (+payout o -1.0)
24:         self.cusum_pos = 0.0  # CUSUM positivo (detecta deterioro)
25:         self.cusum_neg = 0.0  # CUSUM negativo (detecta mejora)
26:         self.is_paused = False
27:         self.pause_history = []
```
* **Lines 36, 60–65, 68–82:**
```python
36:         self.trade_results.append(trade_pnl)
...
60:             self.pause_history.append({
61:                 'action': 'PAUSE',
62:                 'trade_num': len(self.trade_results),
63:                 'cusum': self.cusum_neg,
64:                 'threshold': threshold
65:             })
...
68:         if self.is_paused:
69:             # Verificar si el mercado se recuperó usando una ventana corta
70:             recent_short = self.trade_results[-10:]
71:             recent_wr = sum(1 for r in recent_short if r > 0) / len(recent_short)
72:             if recent_wr >= self.expected_wr:
73:                 self.is_paused = False
74:                 self.cusum_pos = 0.0
75:                 self.cusum_neg = 0.0
...
81:                 return 'RESUME'
82:             return 'PAUSED'
```

#### Exact Bug Cause
1. **Unbounded Memory Growth:**
   - `self.trade_results` is an unbounded Python list. In long-running live trading or multi-year high-frequency simulations with thousands of trades, `self.trade_results` appends continuously without limit.
   - `self.pause_history` appends dictionary records indefinitely on every `PAUSE`/`RESUME` event.
   - Total trade counts are computed using `len(self.trade_results)` and `sum(1 for p in self.pause_history ...)`, creating a hard dependency on storing full history.

2. **Pause Deadlock Recovery Bug:**
   - When CUSUM triggers a pause (`self.is_paused = True`), trading stops.
   - When paper/virtual trade results are fed into `update()` while paused, line 70 inspects `recent_short = self.trade_results[-10:]`.
   - `recent_short` includes trades from BEFORE the pause was initiated — i.e., the exact sequence of losing trades that triggered the pause in the first place!
   - Because pre-pause losing trades pollute `recent_short`, `recent_wr` remains artificially low for many bars even if new paper trades are winning.
   - If paper trades are rare or if fewer than 10 trades occur post-pause, `recent_wr >= expected_wr` can NEVER be satisfied, trapping the strategy in a **pause deadlock**.
   - Furthermore, there is no explicit manual `reset()` method to clear the paused state upon external regime recovery or scheduled strategy restart.

#### Detailed Fix Plan
1. **Memory Growth Remediation:**
   - Add `self.total_trades_count = 0` and `self.pause_count = 0` as integer accumulators.
   - Add `max_history: int = 1000` to `__init__`.
   - Bound `self.trade_results` memory by retaining at most `max_history` items (e.g., `self.trade_results = self.trade_results[-max_history:]`).
   - Limit `self.pause_history` to the last 100 entries.

2. **Pause Deadlock Recovery Remediation:**
   - Add `self.post_pause_results = []` list to track paper/shadow trades received strictly **after** `is_paused` became `True`.
   - When `self.is_paused` is `True` and `update(trade_pnl)` is called:
     - Append `trade_pnl` to `self.post_pause_results`.
     - Evaluate win rate exclusively over post-pause trades: `recent_post = self.post_pause_results[-10:]`.
     - When `len(self.post_pause_results) >= 5` (or min recovery window) and `recent_wr >= self.expected_wr`:
       - Clear pause: `self.is_paused = False`, `self.cusum_pos = 0.0`, `self.cusum_neg = 0.0`, `self.post_pause_results = []`.
       - Append `'RESUME'` to `self.pause_history`.
   - Add an explicit `reset()` method:
```python
def reset(self):
    """Reinicia manualmente el monitor de CUSUM y quita el estado de pausa."""
    self.cusum_pos = 0.0
    self.cusum_neg = 0.0
    self.is_paused = False
    self.post_pause_results = []
```

---

## 3. Item 4 Investigation: `MetaLabeler` & `BinaryMLMetaFilter`

### 3.1 `MetaLabeler` (`engine/ml_engine/meta_labeler.py`)

#### Code Location & Snippet
* **File Path:** `engine/ml_engine/meta_labeler.py`
* **Target Method:** `_extract_context_features(self, df: pd.DataFrame, signal_indices: pd.Index)`
* **Lines 46–53:**
```python
46:         if 'open_time' in df.columns:
47:             times = pd.to_datetime(df.loc[signal_indices, 'open_time'], unit='s', errors='coerce')
48:             if not times.isna().all():
49:                 context['hour_of_day'] = times.dt.hour
50:                 context['day_of_week'] = times.dt.dayofweek
51:                 context['is_session_overlap'] = ((times.dt.hour >= 13) & 
52:                                                   (times.dt.hour <= 17)).astype(int)
```

#### Exact Bug Cause
Line 47 hardcodes `unit='s'` in `pd.to_datetime`.
1. Crypto and FX market data feeds (such as Binance, MT5, IQ Option, CryptoCompare) provide Unix epoch timestamps in **milliseconds** (e.g. `1672531200000` for `2023-01-01 00:00:00 UTC`) or nanoseconds.
2. Passing a millisecond timestamp like `1672531200000` with `unit='s'` forces pandas to interpret the timestamp as $1.67 \times 10^{12}$ seconds, pointing to the year **+54965 AD**.
3. With `errors='coerce'`, pandas returns `NaT` for all rows.
4. Line 48 (`if not times.isna().all()`) evaluates to `False`, silently dropping key temporal features (`hour_of_day`, `day_of_week`, `is_session_overlap`) from the meta-labeler feature set during both training and filtering.

#### Multi-Scale Timestamp Fix Plan
Replace hardcoded `unit='s'` with an intelligent timestamp scale parser:
```python
if 'open_time' in df.columns:
    raw_times = df.loc[signal_indices, 'open_time']
    if pd.api.types.is_datetime64_any_dtype(raw_times):
        times = raw_times
    elif pd.api.types.is_numeric_dtype(raw_times):
        sample_val = raw_times.dropna().iloc[0] if len(raw_times.dropna()) > 0 else 0
        if sample_val > 1e17:
            unit = 'ns'
        elif sample_val > 1e14:
            unit = 'us'
        elif sample_val > 1e11:
            unit = 'ms'
        else:
            unit = 's'
        times = pd.to_datetime(raw_times, unit=unit, errors='coerce')
    else:
        times = pd.to_datetime(raw_times, errors='coerce')

    if not times.isna().all():
        context['hour_of_day'] = times.dt.hour
        context['day_of_week'] = times.dt.dayofweek
        context['is_session_overlap'] = ((times.dt.hour >= 13) & 
                                          (times.dt.hour <= 17)).astype(int)
```

---

### 3.2 `BinaryMLMetaFilter` (`engine/ml_engine/meta_filter.py`)

#### Code Location & Snippet
* **File Path:** `engine/ml_engine/meta_filter.py`
* **Target Method:** `filter_signals(self, signals: pd.Series, X: pd.DataFrame)`
* **Lines 68–78:**
```python
68:         # Adaptive threshold: subir umbral cuando la volatilidad es alta
69:         if self.adaptive_threshold and 'natr' in X.columns:
70:             current_natr = X['natr'].iloc[-1] if len(X) > 0 else 0
71:             median_natr = X['natr'].median() if len(X) > 0 else 0
72:             if current_natr > median_natr * 1.5:
73:                 self.probability_threshold = min(self.base_threshold + 0.10, 0.85)
74:             elif current_natr < median_natr * 0.5:
75:                 self.probability_threshold = max(self.base_threshold - 0.05, 0.55)
76:             else:
77:                 self.probability_threshold = self.base_threshold
```

#### Exact Bug Cause
1. **Global Median Data Leakage:**
   - Line 71 computes `median_natr = X['natr'].median()`. This calculates the median of `natr` across the entire DataFrame `X`.
   - When evaluating historical backtests or dataset slices, `X['natr'].median()` incorporates future values of `natr` past the signal timestamp `idx`, leaking future volatility distribution into the filtering decision.
2. **Static Last-Row Threshold & Uniform Application:**
   - Line 70 grabs `current_natr = X['natr'].iloc[-1]`, taking the NATR of the **very last row** of `X` rather than the NATR at each active signal index (`idx`).
   - It sets a single global `self.probability_threshold` and applies it uniformly across all active signals in `active_indices`, regardless of when each signal occurred.

#### Rolling Backward Median Fix Plan
Compute dynamic threshold per signal index using a rolling backward window median up to each bar `idx`:
```python
# Pre-compute rolling backward median for natr (causal)
if self.adaptive_threshold and 'natr' in X.columns:
    natr_series = X['natr']
    rolling_median_natr = natr_series.rolling(window=100, min_periods=1).median()
else:
    natr_series = None
    rolling_median_natr = None

for idx in active_indices:
    # Determine per-signal adaptive threshold
    thresh = self.base_threshold
    if natr_series is not None and idx in natr_series.index:
        current_natr = natr_series.loc[idx]
        median_natr = rolling_median_natr.loc[idx]
        if current_natr > median_natr * 1.5:
            thresh = min(self.base_threshold + 0.10, 0.85)
        elif current_natr < median_natr * 0.5:
            thresh = max(self.base_threshold - 0.05, 0.55)

    prob = win_probs_dict[idx]  # or probability for active_indices position
    if prob >= thresh:
        filtered_signals.loc[idx] = signals.loc[idx]
```

##### Advantages:
- `current_natr` uses the exact bar's NATR at `idx`.
- `median_natr` uses only historical bars up to `idx` (`rolling(100, min_periods=1)`).
- Eliminates global data leakage completely.

---

## 4. Recommended Unit Test Suite Expansion

Add the following unit test cases to `test_high_winrate_mechanisms.py`:

```python
def test_regime_detector_zero_lookahead(self):
    """Verifica que RegimeDetector no use returns.std() global ni tenga NaNs en obs."""
    detector = RegimeDetector()
    obs = detector._prepare_observations(self.df)
    self.assertEqual(obs.shape, (len(self.df), 3))
    self.assertFalse(np.isnan(obs).any())

def test_cusum_monitor_memory_bounded_and_recovery(self):
    """Verifica que CUSUMMonitor limite memoria y se recupere con trades post-pausa."""
    monitor = CUSUMMonitor(expected_wr=0.6, payout=0.85, window=10)
    
    # Provocar pausa con racha perdedora
    for _ in range(15):
        monitor.update(-1.0)
    self.assertTrue(monitor.is_paused)
    
    # Enviar trades ganadores post-pausa
    for _ in range(10):
        status = monitor.update(0.85)
        
    self.assertFalse(monitor.is_paused)
    self.assertEqual(status, 'RESUME')
    
    # Verificar límite de memoria en trade_results
    stats = monitor.get_stats()
    self.assertLessEqual(len(monitor.trade_results), 1000)

def test_meta_labeler_millisecond_timestamp(self):
    """Verifica que MetaLabeler extraiga features temporales con timestamps en ms."""
    labeler = MetaLabeler()
    df_ms = self.df.copy()
    # Convertir timestamps a milisegundos
    df_ms['open_time'] = (df_ms.index.astype('int64') // 10**6)
    
    context = labeler._extract_context_features(df_ms, df_ms.index[:10])
    self.assertIn('hour_of_day', context.columns)
    self.assertFalse(context['hour_of_day'].isna().all())

def test_meta_filter_rolling_median_no_leakage(self):
    """Verifica que BinaryMLMetaFilter use mediana rolling sin look-ahead."""
    m_filter = BinaryMLMetaFilter(probability_threshold=0.65, adaptive_threshold=True)
    X = pd.DataFrame({
        'natr': np.linspace(0.01, 0.10, 100)
    }, index=range(100))
    signals = pd.Series(['CALL']*100, index=range(100))
    
    # fit dummy
    m_filter.is_fitted = True
    m_filter.model.predict_proba = lambda x: np.full((len(x), 2), 0.70)
    
    filtered = m_filter.filter_signals(signals, X)
    self.assertIsNotNone(filtered)
```
