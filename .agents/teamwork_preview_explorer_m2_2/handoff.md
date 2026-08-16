# Handoff Report — Explorer 2 (Milestone 2: Feature 7 & Feature 10)

## Executive Summary
This report presents a thorough investigation of **Feature 7** (Target Expiry Label Alignment) and **Feature 10** (`PurgedGroupTimeSeriesSplit` integration with embargo in `auto_tuner.py`, `optimizer.py`, and `purged_cv.py`), alongside a comprehensive **Zero Look-Ahead Bias Audit** across the binary options quantitative engine.

---

## 1. Observation

### Feature 7: Target Expiry Label Alignment Flaw
1. **`optimizer_grid_search.py` (lines 47–60)**:
   ```python
   def create_labels(df, signals, expiry_candles=1):
       entry_prices = df['open'].shift(-1)
       exit_prices = df['close'].shift(-(1 + expiry_candles)) # <-- Shift logic flaw
   ```
2. **`run_backtest_comparison.py` (lines 16–32)**:
   ```python
   def create_labels(df, signals, expiry_candles=1):
       ...
       entry_price = float(df.iloc[entry_idx + 1]['open'])
       exit_idx = entry_idx + 1 + expiry_candles             # <-- Index logic flaw
       exit_price = float(df.iloc[exit_idx]['close'])
   ```
3. **`engine/simulator.py` (lines 69, 76, 85)**:
   ```python
   entry_price_raw = float(df.iloc[entry_idx + 1]['open'])
   exit_idx = entry_idx + expiry_candles                      # <-- Ground truth simulator logic
   exit_price = float(df.iloc[exit_idx]['close'])
   ```

### Feature 10: `PurgedGroupTimeSeriesSplit` Integration Gaps
1. **`engine/ml_engine/purged_cv.py` (lines 4–43)**:
   - `PurgedGroupTimeSeriesSplit` is implemented with purge (`test_start - expiry_candles` to `test_start`) and embargo (`test_end` to `test_end + embargo_offset`).
2. **`engine/auto_tuner.py` (`WalkForwardEngine` lines 34–38)**:
   ```python
   df_sub = df.iloc[start_idx:end_idx].copy().reset_index(drop=True)
   split_idx = int(len(df_sub) * self.train_ratio)
   df_is = df_sub.iloc[:split_idx].copy().reset_index(drop=True)     # <-- No purging of last expiry candles
   df_oos = df_sub.iloc[split_idx:].copy().reset_index(drop=True)    # <-- No embargo gap applied
   ```
3. **`engine/optimizer.py` (`optimize_daily_confluence_stream` lines 561–589)**:
   ```python
   sim_res = sim.run_multi_asset(universe_data=universe_data, ...)  # <-- Full dataset run before split
   ...
   trades_is = [t for t in trades if t['time'] < split_time]        # <-- Post-hoc trade filtering, no purge/embargo
   trades_oos = [t for t in trades if t['time'] >= split_time]
   ```

### Causality & Zero Look-Ahead Bias Audit Findings
1. **`engine/ml_engine/feature_extractor.py`**: All rolling windows (`rolling(14)`, `rolling(20)`, `rolling(30)`) and FFT fractional differentiation (`frac_diff_fixed`) use backward-looking arrays terminating at bar $t$.
2. **`strategies/daily_confluence.py`**: Higher-timeframe (weekly) merge via `pd.merge_asof` uses `completion_time = open_time + 7_days` and `direction='backward'`, guaranteeing unclosed weekly candles do not leak into daily execution.
3. **`strategies/volatility_squeeze_ml.py`**: `bb_pctl` computes local rolling percentiles (`rolling(100).min()`, `rolling(100).max()`) without global dataset min/max leakage.
4. **`engine/simulator.py`**: Signals generated at close of candle $t$ execute entry at Open of candle $t+1$, strictly preventing same-bar entry price cheating.

---

## 2. Logic Chain

### Logic Chain for Feature 7
1. *Observation*: For a signal generated at candle $t$, `BinarySimulator` enters at `Open(t+1)` and exits at `Close(t+expiry_candles)`. When `expiry_candles = 1`, `exit_idx = t + 1`, comparing `Close(t+1)` vs `Open(t+1)`.
2. *Observation*: `optimizer_grid_search.py` used `df['close'].shift(-(1 + expiry_candles))`, which for `expiry_candles = 1` evaluated `df['close'].shift(-2)`, comparing `Open(t+1)` with `Close(t+2)` (a 2-candle trade duration). `run_backtest_comparison.py` similarly set `exit_idx = entry_idx + 1 + 1 = entry_idx + 2`.
3. *Deduction*: MetaLabeler training targets created by `create_labels` represented 2-candle trade outcomes, whereas backtest evaluation simulated 1-candle trade outcomes.
4. *Conclusion*: Aligning `create_labels` exit shift to `df['close'].shift(-expiry_candles)` and `exit_idx = entry_idx + expiry_candles` fixes this 1-candle mismatch, harmonizing label generation with `BinarySimulator`.

### Logic Chain for Feature 10
1. *Observation*: `PurgedGroupTimeSeriesSplit` properly purges `expiry_candles` prior to test fold start and embargoes `embargo_pct` after test fold end.
2. *Observation*: `WalkForwardEngine` in `auto_tuner.py` partitioned rolling windows strictly at `split_idx` without purging the last `expiry` candles from `df_is` or delaying `df_oos` start by an embargo offset. Trades opened at `split_idx - 1` with multi-candle expiry spilled into `df_oos`.
3. *Observation*: `optimizer.py` ran `sim.run_multi_asset` over the entire dataset upfront, splitting trade records post-simulation at `split_time`. This leaked multi-asset capital state between IS and OOS and failed to apply purging/embargo.
4. *Conclusion*: Integrating `PurgedGroupTimeSeriesSplit` / purged-embargo partitioning into `WalkForwardEngine` and `CapitalOptimizer` guarantees strict sample isolation without boundary leakage.

---

## 3. Caveats
- No caveats. All investigation paths were executed directly against source files and unit tests.

---

## 4. Conclusion & Actionable Fix Proposals

### Fix Proposal for Feature 7

#### Target File 1: `optimizer_grid_search.py` (Line 47)
```python
def create_labels(df, signals, expiry_candles=1):
    """
    Genera etiquetas ground truth (1.0 WIN / 0.0 LOSS) alineadas con BinarySimulator.
    Entrada: Open de candle (t + 1)
    Salida: Close de candle (t + expiry_candles)
    """
    entry_prices = df['open'].shift(-1)
    exit_prices = df['close'].shift(-expiry_candles)
    
    labels = pd.Series(index=signals.index, dtype=float)
    calls = signals == 'CALL'
    puts = signals == 'PUT'
    
    diff = exit_prices - entry_prices
    
    # Usar tolerancia épsilon 1e-8 idéntica a BinarySimulator
    labels[calls & (diff > 1e-8)] = 1.0
    labels[calls & (diff <= 1e-8)] = 0.0
    labels[puts & (diff < -1e-8)] = 1.0
    labels[puts & (diff >= -1e-8)] = 0.0
    
    return labels.dropna()
```

#### Target File 2: `run_backtest_comparison.py` (Line 16)
```python
def create_labels(df, signals, expiry_candles=1):
    labels = pd.Series(index=signals.index, dtype=float)
    for idx in signals.dropna().index:
        entry_idx = df.index.get_loc(idx)
        exit_idx = entry_idx + expiry_candles
        if entry_idx + 1 >= len(df) or exit_idx >= len(df):
            continue
        entry_price = float(df.iloc[entry_idx + 1]['open'])
        exit_price = float(df.iloc[exit_idx]['close'])
        signal = signals.loc[idx]
        diff = exit_price - entry_price
        if signal == 'CALL':
            labels.loc[idx] = 1.0 if diff > 1e-8 else 0.0
        elif signal == 'PUT':
            labels.loc[idx] = 1.0 if diff < -1e-8 else 0.0
    return labels.dropna()
```

---

### Fix Proposal for Feature 10

#### Target File 1: `engine/ml_engine/purged_cv.py` (Add helper method)
Add `purge_embargo_split` helper method to `PurgedGroupTimeSeriesSplit`:
```python
    @staticmethod
    def purge_embargo_split(n_samples: int, train_ratio: float = 0.60, expiry_candles: int = 1, embargo_pct: float = 0.01):
        """
        Retorna (is_end_idx, oos_start_idx) con purga de expiración y embargo temporal.
        - IS finaliza en (raw_split - expiry_candles)
        - OOS inicia en (raw_split + embargo_offset)
        """
        raw_split = int(n_samples * train_ratio)
        embargo_offset = max(1, int(n_samples * embargo_pct))
        
        is_end = max(0, raw_split - expiry_candles)
        oos_start = min(n_samples, raw_split + embargo_offset)
        
        return is_end, oos_start
```

#### Target File 2: `engine/auto_tuner.py` (`WalkForwardEngine.run_wfa`)
Update window split logic in `WalkForwardEngine.run_wfa`:
```python
            n_sub = len(df_sub)
            raw_split = int(n_sub * self.train_ratio)
            embargo_offset = max(1, int(n_sub * 0.01))
            
            is_end = max(0, raw_split - expiry)
            oos_start = min(n_sub, raw_split + embargo_offset)

            df_is = df_sub.iloc[:is_end].copy().reset_index(drop=True)
            df_oos = df_sub.iloc[oos_start:].copy().reset_index(drop=True)
```

#### Target File 3: `engine/optimizer.py` (`optimize_daily_confluence_stream`)
Partition universe data prior to simulation run:
```python
        # Division Purged CV & Embargo por activo
        universe_is = {}
        universe_oos = {}
        for sym, df in universe_data.items():
            n_sym = len(df)
            raw_split = int(n_sym * 0.70)
            embargo_offset = max(1, int(n_sym * 0.01))
            is_end = max(0, raw_split - 2) # expiry_candles = 2
            oos_start = min(n_sym, raw_split + embargo_offset)
            
            universe_is[sym] = df.iloc[:is_end].copy()
            universe_oos[sym] = df.iloc[oos_start:].copy()

        # Ejecución independiente en In-Sample
        sim_is = sim.run_multi_asset(universe_data=universe_is, signals_by_pair=signals_is, expiry_candles=2, payout=payout)
        # Ejecución independiente en Out-Of-Sample
        sim_oos = sim.run_multi_asset(universe_data=universe_oos, signals_by_pair=signals_oos, expiry_candles=2, payout=payout)
```

---

## 5. Verification Method

### Test Commands to Verify
Run the formal test suite to verify Feature 7 and Feature 10 compliance:
```bash
pytest tests/test_tier1_feature_coverage.py -k "TestFeature07 or TestFeature10" -v
pytest tests/test_high_winrate_mechanisms.py -v
```

### Invalidation Conditions
- Any test failure where `create_labels` with `expiry_candles=1` differs from `BinarySimulator` win/loss outcome.
- Any overlap between In-Sample trade expiry timestamp and Out-Of-Sample evaluation start timestamp during walk-forward cross-validation.
