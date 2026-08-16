# Handoff Report — Reviewer 3 (Milestone M1)

## 1. Observation

### Code Review Findings in `engine/simulator.py`
In `engine/simulator.py` (lines 609-625 and lines 651-660):
```python
609: if bullet['consecutive_wins'] >= n_consecutive:
610:     # 1. Sumar todo el capital acumulado por la bala victoriosa al safe_core permanente
611:     safe_core += bullet['capital']
612:     
613:     # 2. Recalcular el nuevo presupuesto de riesgo para la siguiente campaña (20% de la nueva base)
614:     risk_cap = safe_core * risk_ratio
615:     bet_per_attempt = risk_cap / attempts
616:     
617:     # 3. Reiniciar in-place las balas para la nueva campaña sin corromper trades en vuelo
618:     for b in bullets:
619:         if b['active_trade_id'] is None:
620:             b['capital'] = bet_per_attempt
621:             b['consecutive_wins'] = 0
622:             b['pending_reset'] = False
623:         else:
624:             b['pending_reset'] = True
625:             b['next_capital'] = bet_per_attempt
...
651: if bullet.get('pending_reset'):
652:     if is_win:
653:         safe_core += pnl
654:     bullet['capital'] = bullet.pop('next_capital', bet_per_attempt)
655:     bullet['consecutive_wins'] = 0
656:     bullet['pending_reset'] = False
657: 
658: # Actualizar equidad actual
659: active_bullets_cap = sum(b['capital'] for b in bullets if not b.get('pending_reset'))
660: current_equity = safe_core + active_bullets_cap
```

### Code Review Findings in `tests/test_simulator_integrity.py`
In `tests/test_simulator_integrity.py` (lines 153-159):
```python
153: btc_trade = next(t for t in trades if t['pair'] == 'BTCUSDT')
154: eq_day5 = equity_curve[-2]['equity']
155: eq_day6 = equity_curve[-1]['equity']
156: next_cap = 114.225
157: in_flight_pnl_captured = (eq_day6 - eq_day5) - next_cap
158: 
159: self.assertAlmostEqual(in_flight_pnl_captured, btc_trade['pnl'], places=4)
```

### Empirical Verification Test Results
1. **Unit test execution**:
   - `python -m unittest tests/test_simulator_integrity.py`: 11 tests executed, 11 passed (OK).
   - `pytest test_high_winrate_mechanisms.py`: 5 tests executed, 5 passed (100%).
2. **Empirical stress test (near-zero payout = 0.0001)**:
   - Command: Synthetic dataset with 10 winning trades across 5 campaign resets, `initial_capital = 1000.0`, `payout = 0.0001`, `n_consecutive = 2`, `risk_ratio = 0.20`.
   - Total trade PnL accumulated: ~0.05.
   - Initial equity: 1000.0.
   - Final reported equity: **1581.38** (+58.1% phantom profit manufactured without trading gains).

---

## 2. Logic Chain

1. **Initialization state**:
   At simulation start (lines 467-470), `safe_core = initial_capital * (1.0 - risk_ratio)` (e.g. 800 for 1000 initial capital with 20% risk ratio). Active bullets total `risk_cap` (200). `current_equity = safe_core + sum(bullets)` = 800 + 200 = 1000. Here `safe_core` represents ONLY the safe (80%) un-risked portion of equity.

2. **Campaign completion reset flaw**:
   When a bullet completes a winning streak (`bullet['consecutive_wins'] >= n_consecutive`), line 611 executes `safe_core += bullet['capital']`.
   If Bullet 0 accumulated 342.25, `safe_core` becomes 800 + 342.25 = 1142.25.
   Notice that 1142.25 is now the **TOTAL 100% account equity base**.
   Line 614 calculates `risk_cap = safe_core * risk_ratio` = 1142.25 * 0.20 = 228.45 (114.225 per bullet).
   However, `safe_core` is **NEVER adjusted** to deduct `risk_cap` (it is not reset to `1142.25 * (1.0 - risk_ratio) = 913.80`).

3. **Double-counting on equity calculation**:
   Line 660 calculates `current_equity = safe_core + active_bullets_cap`.
   `safe_core` contains 100% of account equity (1142.25), and `active_bullets_cap` contains 20% of account equity (228.45).
   `current_equity` becomes 1142.25 + 228.45 = **1370.70**.
   The 20% risk cap (228.45) is counted **TWICE**: once inside `safe_core` and once inside `active_bullets_cap`.
   Consequently, every single Barbell campaign reset spontaneously inflates account equity by 20%.

4. **Test masking in `tests/test_simulator_integrity.py`**:
   The test `test_multi_asset_barbell_reset_in_flight_trade_accounting` hardcoded `next_cap = 114.225` and asserted `(eq_day6 - eq_day5) - next_cap == btc_trade['pnl']`.
   Because `eq_day5` (1256.475) and `eq_day6` (1455.70) were both corrupted by the double-counting bug, taking `(1455.70 - 1256.475) - 114.225` yielded `85.0`, which matched `btc_trade['pnl']`.
   The hardcoded offset subtraction masked the fact that absolute total account equity jumped from 1327.25 (actual correct equity) to 1455.70.

5. **In-flight pending reset drop**:
   Line 659 (`sum(b['capital'] for b in bullets if not b.get('pending_reset'))`) excludes bullets with `pending_reset = True` from `active_bullets_cap`.
   This causes active capital in-flight during a reset to completely vanish from reported equity curves until the trade exits, creating false equity drops followed by sudden equity spikes.

---

## 3. Caveats

No caveats. The mathematical accounting flaw and test-masking pattern are 100% deterministic and empirically reproduced.

---

## 4. Conclusion & Verdict

**Verdict**: **REQUEST_CHANGES**

### Critical Findings

#### Finding 1: [Critical / INTEGRITY VIOLATION & SOFTWARE BUG] Double-Counting of Risk Budget in `engine/simulator.py`
- **Location**: `engine/simulator.py`, lines 609–660
- **Description**: `safe_core` stores 100% of the total account equity pool upon campaign completion, but line 660 computes `current_equity = safe_core + active_bullets_cap` without deducting `risk_cap` from `safe_core`. This double-counts the 20% risk cap, creating phantom equity out of thin air on every campaign reset (demonstrated by a 58.1% artificial gain with payout = 0.0001).
- **Suggested Fix Direction**:
  Update campaign completion logic so that `safe_core` represents only the un-risked portion of equity:
  ```python
  total_account_equity = safe_core + bullet['capital']
  risk_cap = total_account_equity * risk_ratio
  safe_core = total_account_equity * (1.0 - risk_ratio)  # Or total_account_equity - risk_cap
  bet_per_attempt = risk_cap / attempts
  ```

#### Finding 2: [Major / TEST INTEGRITY] Masked Assertion in `test_multi_asset_barbell_reset_in_flight_trade_accounting`
- **Location**: `tests/test_simulator_integrity.py`, lines 156–159
- **Description**: The unit test uses a hardcoded offset subtraction (`(eq_day6 - eq_day5) - next_cap`) that masks absolute equity corruption in the simulator.
- **Suggested Fix Direction**:
  Assert strict conservation of total account equity (`res['equity_curve'][-1]['equity'] == initial_capital + sum(t['pnl'] for t in res['trades'])`).

---

## 5. Verification Method

1. Run the empirical stress test script with `payout = 0.0001` and 10 winning trades across 5 campaign resets:
   ```bash
   python -c "
   import pandas as pd
   from engine.simulator import BinarySimulator
   day = 86400; t1 = 1767261600; times = [t1 + i * day for i in range(20)]
   eur_df = pd.DataFrame({'open_time': times, 'open': [1.1]*20, 'high': [1.105]*20, 'low': [1.095]*20, 'close': [1.102]*20, 'volume': [1000]*20})
   signals = [{'time': times[i], 'direction': 'CALL'} for i in range(0, 20, 2)]
   sim = BinarySimulator()
   res = sim.run_multi_asset({'EURUSD': eur_df}, {'EURUSD': signals}, expiry_candles=1, payout=0.0001, initial_capital=1000.0, mode='BARBELL', n_consecutive=2, bet_fraction=0.5, risk_ratio=0.20)
   print('Final equity:', res['equity_curve'][-1]['equity'])
   "
   ```
   - **Invalidation Condition (Unfixed code)**: Final equity outputs ~1581.38.
   - **Pass Condition (Fixed code)**: Final equity outputs ~1000.0 (exact conservation of capital when payout is near zero).
