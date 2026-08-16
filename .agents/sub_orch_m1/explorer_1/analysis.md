# BinarySimulator Deep Technical Analysis & Bug Remediation Plan

## Executive Summary
This report presents a line-by-line audit of `BinarySimulator` in `engine/simulator.py`. Three critical issues were identified:
1. **`tie_rule` Parameter Omission in Multi-Asset Simulation**: `run_multi_asset()` lacks the `tie_rule` parameter in its function signature and fails to handle `tie_rule == 'LOSS'` during discrete event trade classification.
2. **Bullet State Corruption in Barbell Streak Reset**: Re-creating the `bullets` list upon campaign reset (win target reached or all bullets ruined) overwrites `active_trade_id` to `None` across all bullet indices. When other assets have trades in flight, their bullet state is corrupted, causing double trade assignment and cross-campaign capital leakage.
3. **Dead / Unreachable Code**: Redundant entry price `else` branches (which can never execute due to loop boundary guards) and duplicate trade status checks.

---

## 1. Issue 1: `tie_rule` Propagation & Handling in `run_multi_asset()`

### Exact Location & Snippets
- **File**: `engine/simulator.py`
- **Line 244 (Signature)**:
```python
def run_multi_asset(self, universe_data: dict, signals_by_pair: dict, expiry_candles: int = 2, payout: float = 0.85, initial_capital: float = 1000.0, mode: str = 'SIMPLE', n_consecutive: int = 3, bet_fraction: float = 0.166, risk_ratio: float = 0.20, target_ratio: float = 5.0, slippage_pct: float = 0.0):
```
- **Lines 314–335 (Trade Classification)**:
```python
# --- Clasificación WIN / TIE / LOSS con tolerancia épsilon ---
price_diff = exit_price - entry_price
is_tie = abs(price_diff) <= _PRICE_EPS
is_win = False
if not is_tie:
    if direction == 'CALL' and price_diff > 0:
        is_win = True
    elif direction == 'PUT' and price_diff < 0:
        is_win = True

raw_trades.append({
    'pair': symbol,
    'direction': direction,
    'entry_time': entry_time,
    'exit_time': exit_time,
    'entry_price': entry_price,
    'exit_price': exit_price,
    'result': 'WIN' if is_win else ('TIE' if is_tie else 'LOSS'),
    'is_win': is_win,
    'is_tie': is_tie,
    'index': entry_idx
})
```

### Rationale
Single-asset `run()` (line 8) accepts `tie_rule: str = 'RETURN_STAKE'`. When `tie_rule == 'LOSS'`, single-asset `run()` converts ties (`abs(price_diff) <= _PRICE_EPS`) into `is_win = False` and `is_tie = False` (result = `'LOSS'`), which deducts the stake (`pnl = -bet_size`).
In `run_multi_asset()`:
1. `tie_rule` is missing from the function signature.
2. Even if price equality occurs within `_PRICE_EPS`, `run_multi_asset()` hardcodes `is_tie = True`, returning stake (`pnl = 0.0`) regardless of whether the user or broker rule dictates ties count as loss (e.g., Deriv platform rules).

### Recommended Fix Code
1. Update `run_multi_asset()` signature to accept `tie_rule: str = 'RETURN_STAKE'`:
```python
def run_multi_asset(self, universe_data: dict, signals_by_pair: dict, expiry_candles: int = 2, payout: float = 0.85, initial_capital: float = 1000.0, mode: str = 'SIMPLE', n_consecutive: int = 3, bet_fraction: float = 0.166, risk_ratio: float = 0.20, target_ratio: float = 5.0, slippage_pct: float = 0.0, tie_rule: str = 'RETURN_STAKE'):
```
2. Update raw trade classification logic (lines 314–335):
```python
# --- Clasificación WIN / TIE / LOSS con tolerancia épsilon y tie_rule ---
price_diff = exit_price - entry_price
is_tie = abs(price_diff) <= _PRICE_EPS
is_win = False

if is_tie and tie_rule == 'LOSS':
    is_win = False
    is_tie = False  # Deriv counts tie as LOSS
elif not is_tie:
    if direction == 'CALL' and price_diff > 0:
        is_win = True
    elif direction == 'PUT' and price_diff < 0:
        is_win = True

raw_trades.append({
    'pair': symbol,
    'direction': direction,
    'entry_time': entry_time,
    'exit_time': exit_time,
    'entry_price': entry_price,
    'exit_price': exit_price,
    'result': 'WIN' if is_win else ('TIE' if is_tie else 'LOSS'),
    'is_win': is_win,
    'is_tie': is_tie,
    'index': entry_idx
})
```

---

## 2. Issue 2: Bullet State Corruption in Barbell Streak Reset

### Exact Location & Snippets
- **File**: `engine/simulator.py`
- **Lines 517–521 (Win Streak Target Reached Campaign Reset)**:
```python
# 3. Reiniciar todas las balas para la nueva campaña con la nueva base incrementada
bullets = [{
    'capital': bet_per_attempt,
    'consecutive_wins': 0,
    'active_trade_id': None
} for _ in range(attempts)]
```
- **Lines 538–542 (All Bullets Ruined Campaign Reset)**:
```python
# Iniciar una nueva campaña reabastecida por arbitraje externo
bullets = [{
    'capital': bet_per_attempt,
    'consecutive_wins': 0,
    'active_trade_id': None
} for _ in range(attempts)]
```

### Rationale
In multi-asset simulation, multiple symbols can have overlapping trades running concurrently.
Suppose Bullet 1 (assigned to Pair A trade T1) reaches `consecutive_wins >= n_consecutive` at timestamp `t=25`, while Bullet 0 is currently executing Pair B trade T2 (which started at `t=15` and exits at `t=30`).
When trade T1 completes the win streak:
1. `safe_core` is incremented by Bullet 1's accumulated capital.
2. Lines 517–521 construct a brand new `bullets` list where **every** bullet has `active_trade_id = None`.
3. **Corruption Step 1**: Bullet 0's active trade reference `active_trade_id = T2` is wiped out. To the simulator, Bullet 0 now appears completely free!
4. **Corruption Step 2**: If a new signal T3 arrives at `t=27`, `available_bullets` will select Bullet 0 (because `active_trade_id is None`). Bullet 0 is now assigned trade T3, while trade T2 is still running on it!
5. **Corruption Step 3**: When trade T2 exits at `t=30`, it accesses `bullets[0]` (the new campaign's bullet object), updates its capital with old campaign PnL, and sets `active_trade_id = None`—clearing trade T3's active status prematurely while T3 is still running.

### Recommended Fix Code
Mutate bullet dictionaries in-place and use a `pending_reset` flag for bullets with active trades in flight during a campaign reset:

1. **Initialization (lines 376–380)**:
```python
bullets = [{
    'capital': bet_per_attempt,
    'consecutive_wins': 0,
    'active_trade_id': None,
    'pending_reset': False
} for _ in range(attempts)]
```

2. **Campaign Reset on Win Streak (lines 508–522)**:
```python
if bullet['consecutive_wins'] >= n_consecutive:
    safe_core += bullet['capital']
    risk_cap = safe_core * risk_ratio
    bet_per_attempt = risk_cap / attempts
    
    # Actualizar estado de las balas in-situ sin huérfanos ni corrupción
    for b in bullets:
        if b['active_trade_id'] is None:
            b['capital'] = bet_per_attempt
            b['consecutive_wins'] = 0
            b['pending_reset'] = False
        else:
            b['pending_reset'] = True
```

3. **Campaign Reset on All Ruined (lines 530–543)**:
```python
all_ruined = all(b['capital'] <= 0.0001 and b['active_trade_id'] is None for b in bullets)
if all_ruined:
    if safe_core < initial_capital * (1.0 - risk_ratio):
        safe_core = initial_capital * (1.0 - risk_ratio)
    
    risk_cap = initial_capital * risk_ratio
    bet_per_attempt = risk_cap / attempts
    
    for b in bullets:
        b['capital'] = bet_per_attempt
        b['consecutive_wins'] = 0
        b['active_trade_id'] = None
        b['pending_reset'] = False
```

4. **Exit Event Handler for Bullet (lines 497–506 and ties)**:
When an exit event occurs on a bullet:
```python
bullet_idx = t.get('assigned_bullet_idx')
bullet = bullets[bullet_idx]

if bullet.get('pending_reset', False):
    bullet['capital'] = bet_per_attempt
    bullet['consecutive_wins'] = 0
    bullet['active_trade_id'] = None
    bullet['pending_reset'] = False
else:
    if is_win:
        pnl = bet_size * payout
        bullet['capital'] += pnl
        bullet['consecutive_wins'] += 1
        bullet['active_trade_id'] = None
        ...
    else:
        pnl = -bet_size
        bullet['capital'] = 0
        bullet['consecutive_wins'] = 0
        bullet['active_trade_id'] = None
        ...
```
Similarly, for `is_tie` in BARBELL (lines 477–480):
```python
if is_tie:
    if mode == 'BARBELL':
        bullet_idx = t.get('assigned_bullet_idx')
        if bullet_idx is not None and 0 <= bullet_idx < len(bullets):
            bullet = bullets[bullet_idx]
            bullet['active_trade_id'] = None
            if bullet.get('pending_reset', False):
                bullet['capital'] = bet_per_attempt
                bullet['consecutive_wins'] = 0
                bullet['pending_reset'] = False
```

---

## 3. Issue 3: Dead / Unreachable Code Cleanup

### Exact Location & Snippets

1. **Unreachable `else` in `run()` (lines 76–81)**:
```python
if entry_idx + 1 < len(df):
    entry_price_raw = float(df.iloc[entry_idx + 1]['open'])
    entry_time = int(df.iloc[entry_idx + 1]['open_time'])
else:
    entry_price_raw = float(df.iloc[entry_idx]['close'])
    entry_time = int(df.iloc[entry_idx]['open_time']) + candle_duration
```
- **Rationale**: Line 71 guards `if exit_idx >= len(df): break`. Because `expiry_candles >= 1`, `exit_idx = entry_idx + expiry_candles >= entry_idx + 1`. If `exit_idx < len(df)`, then `entry_idx + 1 < len(df)` is **always** True. The `else:` block is dead/unreachable code.
- **Cleanup**: Remove `if entry_idx + 1 < len(df):` guard and `else:` block; execute entry extraction directly:
```python
entry_price_raw = float(df.iloc[entry_idx + 1]['open'])
entry_time = int(df.iloc[entry_idx + 1]['open_time'])
```

2. **Unreachable `else` in `run_multi_asset()` (lines 290–295)**:
```python
if entry_idx + 1 < n_df:
    entry_price_raw = float(df_open[entry_idx + 1])
    entry_time = int(df_open_time[entry_idx + 1])
else:
    entry_price_raw = float(df_close[entry_idx])
    entry_time = int(df_open_time[entry_idx]) + candle_duration
```
- **Rationale**: Line 285 guards `if exit_idx >= n_df: continue`. Since `exit_idx >= entry_idx + 1`, `entry_idx + 1 < n_df` is **always** True. The `else:` block is dead/unreachable code.
- **Cleanup**: Simplify to:
```python
entry_price_raw = float(df_open[entry_idx + 1])
entry_time = int(df_open_time[entry_idx + 1])
```

3. **Redundant `is_active` checks in `run_multi_asset()` (lines 549 & 567)**:
```python
elif mode == 'REINVESTMENT':
    if not t.get('is_active'):
        continue
...
else: # SIMPLE
    if not t.get('is_active'):
        continue
```
- **Rationale**: Line 467 already executes `if mode != 'BARBELL' and not t.get('is_active', False): continue` at the start of exit event processing. Therefore, `t.get('is_active')` is guaranteed True inside REINVESTMENT and SIMPLE branches.
- **Cleanup**: Remove duplicate `if not t.get('is_active'): continue` lines.

4. **Module Top-Level Import Refactoring**:
- Move `from engine.correlation import CorrelationEngine` from line 363 to top-level imports of `engine/simulator.py`.

---

## 4. Recommended Unit Test Cases

The following test suite should be placed in `tests/test_simulator_integrity.py`:

```python
import unittest
import pandas as pd
import numpy as np
from engine.simulator import BinarySimulator

class TestSimulatorIntegrity(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)
        n = 100
        times = np.arange(n) * 300  # 5-min candles in seconds
        self.df_eurusd = pd.DataFrame({
            'open_time': times,
            'open': np.full(n, 1.1000),
            'high': np.full(n, 1.1050),
            'low': np.full(n, 1.0950),
            'close': np.full(n, 1.1000),
            'volume': np.full(n, 1000)
        })
        self.df_gbpusd = pd.DataFrame({
            'open_time': times,
            'open': np.full(n, 1.2500),
            'high': np.full(n, 1.2550),
            'low': np.full(n, 1.2450),
            'close': np.full(n, 1.2500),
            'volume': np.full(n, 1000)
        })

    def test_multi_asset_tie_rule_propagation(self):
        sim = BinarySimulator()
        universe = {'EURUSD': self.df_eurusd}
        signals = {'EURUSD': [{'time': 300, 'direction': 'CALL'}]}

        # Default / RETURN_STAKE tie rule
        res_return = sim.run_multi_asset(universe, signals, expiry_candles=1, tie_rule='RETURN_STAKE')
        self.assertEqual(len(res_return['trades']), 1)
        self.assertEqual(res_return['trades'][0]['result'], 'TIE')
        self.assertEqual(res_return['trades'][0]['pnl'], 0.0)

        # LOSS tie rule
        res_loss = sim.run_multi_asset(universe, signals, expiry_candles=1, tie_rule='LOSS')
        self.assertEqual(len(res_loss['trades']), 1)
        self.assertEqual(res_loss['trades'][0]['result'], 'LOSS')
        self.assertLess(res_loss['trades'][0]['pnl'], 0.0)

    def test_multi_asset_barbell_streak_reset_no_corruption(self):
        sim = BinarySimulator()
        
        # Asset A price movement: Win on trade at index 1
        df_a = self.df_eurusd.copy()
        df_a.loc[3, 'close'] = 1.1100  # Win for CALL at index 1 (exit at index 2 or 3)
        
        # Asset B price movement: Long trade starting at index 1
        df_b = self.df_gbpusd.copy()
        df_b.loc[10, 'close'] = 1.2600  # Long duration trade
        
        universe = {'EURUSD': df_a, 'GBPUSD': df_b}
        signals = {
            'EURUSD': [{'time': 300, 'direction': 'CALL'}],    # Entry index 1, exit 2
            'GBPUSD': [{'time': 600, 'direction': 'CALL'}]     # Entry index 2, exit 10
        }
        
        res = sim.run_multi_asset(
            universe, signals, expiry_candles=1, mode='BARBELL',
            bet_fraction=0.5, n_consecutive=1
        )
        
        # Both trades should execute cleanly without bullet corruption or orphaned state
        self.assertEqual(len(res['trades']), 2)
        self.assertTrue(all(t['result'] in ['WIN', 'LOSS', 'TIE'] for t in res['trades']))
        self.assertGreater(res['summary']['net_pnl'], 0)

if __name__ == '__main__':
    unittest.main()
```
