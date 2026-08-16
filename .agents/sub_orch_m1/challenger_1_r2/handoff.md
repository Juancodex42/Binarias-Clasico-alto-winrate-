# Handoff Report — challenger_1_r2

## 1. Observation

Empirical stress tests were written and executed against `engine/simulator.py` and `engine/ml_engine/feature_extractor.py`.

### Test 2a: `BinarySimulator.run_multi_asset` Tie Handling (`test_2a_tie_rule.py`)
- **File inspected**: `engine/simulator.py` (lines 306-329, 471-494)
- **Execution Command**: `python c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/challenger_1_r2/test_2a_tie_rule.py`
- **Verbatim Output**:
```
=== TEST 2A: BinarySimulator.run_multi_asset tie_rule Handling ===

--- Test Case A1: tie_rule = 'RETURN_STAKE' ---
Total trades: 1
Wins: 0, Losses: 0, Ties: 1
Net PnL: 0.0
Final Equity: 1000.0
Trade result: TIE, PnL: 0.0, Bet Size: 100.0

--- Test Case A2: tie_rule = 'LOSS' ---
Total trades: 1
Wins: 0, Losses: 1, Ties: 0
Net PnL: -100.0
Final Equity: 900.0
Trade result: LOSS, PnL: -100.0, Bet Size: 100.0

[PASS] Test 2A passed all assertions successfully!
```

### Test 2b: Multi-Asset Barbell Campaign Reset with Active Trades in Flight (`test_2b_barbell_reset_scenario.py`)
- **File inspected**: `engine/simulator.py` (lines 500-556)
- **Execution Command**: `python c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/challenger_1_r2/test_2b_barbell_reset_scenario.py`
- **Verbatim Output**:
```
=== TEST 2B: Barbell Campaign Reset with Active In-Flight Trade ===

--- Trades Chronological Order ---
Trade 1: Pair=EURUSD, Entry=1767348000, Exit=1767434400, Result=WIN, Bet=100.0, PnL=85.0
Trade 2: Pair=EURUSD, Entry=1767520800, Exit=1767607200, Result=WIN, Bet=185.0, PnL=157.25
Trade 3: Pair=BTCUSDT, Entry=1767348000, Exit=1767693600, Result=WIN, Bet=100.0, PnL=85.0

--- Equity Curve ---
Time=1767348000, Equity=1000.0
Time=1767434400, Equity=1085.0
Time=1767607200, Equity=1256.475
Time=1767693600, Equity=1370.7

--- Summary ---
Total trades: 3
Wins: 3, Losses: 0, Net PnL: 327.25
Final Equity: 1370.7

EURUSD Trade 1 (Exit Day 3): Bet=100.0, PnL=85.0
EURUSD Trade 2 (Exit Day 5 - Reset Trigger): Bet=185.0, PnL=157.25
BTCUSDT Trade (Exit Day 6 - In Flight): Bet=100.0, PnL=85.0

Sum of all trade PnLs: 327.2500
Equity gain (Final Equity - 1000.0): 370.7000
Accounting Discrepancy (Sum of PnLs vs Equity Gain): -43.4500

[FAIL] Discrepancy detected! In-flight trade PnL was wiped out during campaign reset.
```

- **Code snippet in `engine/simulator.py` lines 549-556**:
```python
if bullet.get('pending_reset'):
    bullet['capital'] = bullet.pop('next_capital', bet_per_attempt)
    bullet['consecutive_wins'] = 0
    bullet['pending_reset'] = False

# Actualizar equidad actual
active_bullets_cap = sum(b['capital'] for b in bullets if not b.get('pending_reset'))
current_equity = safe_core + active_bullets_cap
```

### Test 2c: `BinaryFeatureExtractor.frac_diff_fixed` FFT vs Loop (`test_2c_frac_diff.py`)
- **File inspected**: `engine/ml_engine/feature_extractor.py` (lines 6-42)
- **Execution Command**: `python c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/challenger_1_r2/test_2c_frac_diff.py`
- **Verbatim Output**:
```
=== TEST 2C: BinaryFeatureExtractor.frac_diff_fixed (FFT vs Loop) ===
d=0.2: Max Delta between FFT and Loop = 8.527e-14
d=0.4: Max Delta between FFT and Loop = 8.260e-14
d=0.6: Max Delta between FFT and Loop = 8.804e-14

[PASS] All max deltas are < 1e-10 (Overall Max Delta: 8.804e-14)

Running benchmark: 5 iterations on N=10000 samples (d=0.4)...
Loop implementation total time: 0.9541 seconds (190.83 ms/iter)
FFT implementation total time:  0.0212 seconds (4.23 ms/iter)
Speedup Factor: 45.10x
```

---

## 2. Logic Chain

1. **Tie Rule Handling Logic Chain**:
   - `engine/simulator.py` lines 306-318 classify trades based on price diff relative to `_PRICE_EPS` (1e-8).
   - For `tie_rule='RETURN_STAKE'`: When `abs(exit_price - entry_price) <= _PRICE_EPS`, `is_tie` is set to `True` and `is_win` is set to `False`. At exit processing (lines 471-494), `pnl` is set to `0.0`, `result` is `'TIE'`, and equity remains unchanged. Test 2a confirms `summary['ties'] == 1`, `pnl == 0.0`, `equity == 1000.0`.
   - For `tie_rule='LOSS'`: When `abs(exit_price - entry_price) <= _PRICE_EPS`, lines 310-312 override `is_tie = False` and `is_win = False`. At exit processing, the code falls into the loss branch, setting `pnl = -bet_size`, `result = 'LOSS'`. Test 2a confirms `summary['losses'] == 1`, `pnl == -100.0`, `equity == 900.0`.
   - **Conclusion**: `run_multi_asset` correctly handles tie rules.

2. **Barbell Pending Reset Logic Chain**:
   - In `engine/simulator.py`, when a bullet completes a campaign (`bullet['consecutive_wins'] >= n_consecutive`), a campaign reset is performed (lines 508-524).
   - `safe_core` is incremented by the winning bullet's capital. New `risk_cap` and `bet_per_attempt` are computed.
   - For any other bullet with an active trade in flight (`b['active_trade_id'] is not None`), `b['pending_reset'] = True` and `b['next_capital'] = bet_per_attempt` are set.
   - When that in-flight trade later completes (lines 496-504):
     - The trade result is evaluated: if `is_win`, `bullet['capital'] += pnl` and `bullet['consecutive_wins'] += 1`.
     - BUT IMMEDIATELY AFTER, lines 549-552 run:
       ```python
       if bullet.get('pending_reset'):
           bullet['capital'] = bullet.pop('next_capital', bet_per_attempt)
           bullet['consecutive_wins'] = 0
           bullet['pending_reset'] = False
       ```
     - This OVERWRITES `bullet['capital']` with `next_capital` (wiping out the PnL earned by the in-flight trade) and resets `consecutive_wins` to `0`!
     - Because `safe_core` was consolidated at the reset timestamp (before the in-flight trade exited), the PnL of the in-flight trade is NEVER added to `safe_core` AND is wiped from the bullet's capital.
     - Furthermore, assigning `next_capital` (drawn from the new campaign risk cap) to the bullet while its PnL was erased causes portfolio equity (`safe_core + active_bullets_cap`) to diverge from cumulative trade PnL (`summary['net_pnl']`), creating a -43.45 accounting discrepancy in Test 2b.
   - **Conclusion**: The implementation fails to preserve PnL and win streaks for in-flight trades during a Barbell campaign reset.

3. **FFT Fractional Differentiation Logic Chain**:
   - `engine/ml_engine/feature_extractor.py` lines 6-42 implement FFD using `scipy.signal.fftconvolve(vals, w_arr, mode='valid')`.
   - `fftconvolve` mode `'valid'` computes $\sum_{k=0}^{W-1} w_k \cdot x_{t-k}$ for $t \ge W-1$, which is mathematically identical to the sliding window dot product with reversed weights used in López de Prado's original FFD loop algorithm.
   - Empirical evaluation across $d \in \{0.2, 0.4, 0.6\}$ on 10,000 observations yields a maximum absolute difference of `8.804e-14`, satisfying the required tolerance of `< 1e-10`.
   - Benchmarking 10,000 samples over 5 iterations yields an execution time of 190.83 ms/iter for the loop vs 4.23 ms/iter for FFT, demonstrating a **45.10x speedup**.
   - **Conclusion**: `frac_diff_fixed` is mathematically equivalent and delivers superior performance.

---

## 3. Caveats

- **No code modification**: Per challenger role constraints, no changes were made to `engine/simulator.py` or `engine/ml_engine/feature_extractor.py`.
- **Inter-class correlation filter**: In `BinarySimulator.run_multi_asset`, trades are filtered by asset class (`CorrelationEngine.get_asset_class(pair)`), permitting only 1 trade per asset class per day. Test 2b correctly utilized pairs from distinct asset classes (`EURUSD` [Forex] and `BTCUSDT` [Crypto]) across daily timestamps to construct valid multi-asset concurrent trade scenarios.

---

## 4. Conclusion & Explicit Verdict

| Objective | Description | Verdict | Key Evidence |
|-----------|-------------|---------|--------------|
| **2a** | `run_multi_asset` `tie_rule='RETURN_STAKE'` and `'LOSS'` | **PASS** | RETURN_STAKE: PnL 0.0, 'TIE'. LOSS: PnL -100.0, 'LOSS'. |
| **2b** | Multi-asset Barbell campaign reset with active in-flight trades (`pending_reset = True`) | **FAIL** | Bug confirmed: line 549 overwrites in-flight bullet capital and win streak, corrupting equity accounting (-43.45 discrepancy). |
| **2c** | `frac_diff_fixed` using `fftconvolve` equivalence & speedup | **PASS** | Max delta = $8.804 \times 10^{-14} < 10^{-10}$. Speedup = 45.10x. |

---

## 5. Verification Method

To independently verify these empirical results:

1. **Run Test 2a (Tie Rule)**:
   ```pwsh
   python c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/challenger_1_r2/test_2a_tie_rule.py
   ```
   *Expected output*: `[PASS] Test 2A passed all assertions successfully!`

2. **Run Test 2b (Barbell Pending Reset)**:
   ```pwsh
   python c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/challenger_1_r2/test_2b_barbell_reset_scenario.py
   ```
   *Expected output*: `[FAIL] Discrepancy detected! In-flight trade PnL was wiped out during campaign reset.`

3. **Run Test 2c (Frac Diff FFT vs Loop)**:
   ```pwsh
   python c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/challenger_1_r2/test_2c_frac_diff.py
   ```
   *Expected output*: `[PASS] All max deltas are < 1e-10 (Overall Max Delta: 8.804e-14)` and `Speedup Factor: 45.10x`.

4. **Run Complete Suite**:
   ```pwsh
   python c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/challenger_1_r2/run_all_tests.py
   ```
