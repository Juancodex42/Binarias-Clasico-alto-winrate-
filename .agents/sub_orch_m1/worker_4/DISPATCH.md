## 2026-08-12T17:54:29Z
You are worker_4 for Milestone M1 (Engine Bug Remediation & Core Fixes).
Your working directory is: c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/worker_4
Master project specification: c:/Users/juanc/Desktop/prueba/PROJECT.md
Original user request: c:/Users/juanc/Desktop/prueba/.agents/ORIGINAL_REQUEST.md

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Task Objective:
Fix the Barbell mode risk budget double-counting bug in `engine/simulator.py` and update unit test assertions in `tests/test_simulator_integrity.py` as detailed in Reviewer 3's handoff report (`c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/reviewer_3/handoff.md`).

Context & Flaw Explanation:
In `engine/simulator.py`, when a campaign reset occurs, `safe_core += bullet['capital']` accumulates 100% of the total account equity pool into `safe_core`. Then `risk_cap` (20% of account equity) is calculated and assigned to bullets, but `safe_core` is NEVER reduced by `risk_cap` (it is not set to `total_account_equity * (1.0 - risk_ratio)`). When `current_equity = safe_core + active_bullets_cap` is computed, the 20% risk budget is counted TWICE (once in `safe_core` and once in `active_bullets_cap`), inflating account equity spontaneously on every campaign reset.

Required Code Changes:
1. In `engine/simulator.py` (Barbell campaign completion reset block):
   ```python
   # 1. Total account equity prior to reallocation includes safe_core + all bullet capitals
   total_account_equity = safe_core + sum(b['capital'] for b in bullets)
   
   # 2. Recalculate risk cap and safe core (un-risked portion)
   risk_cap = total_account_equity * risk_ratio
   safe_core = total_account_equity * (1.0 - risk_ratio)
   bet_per_attempt = risk_cap / attempts
   
   # 3. Reset idle bullets immediately; stage pending_reset for active bullets
   for b in bullets:
       if b['active_trade_id'] is None:
           b['capital'] = bet_per_attempt
           b['consecutive_wins'] = 0
           b['pending_reset'] = False
       else:
           b['pending_reset'] = True
           b['next_capital'] = bet_per_attempt
   ```
2. In `engine/simulator.py` (Barbell ruined campaign reset block):
   ```python
   total_account_equity = max(safe_core, initial_capital * (1.0 - risk_ratio))
   risk_cap = total_account_equity * risk_ratio
   safe_core = total_account_equity * (1.0 - risk_ratio)
   bet_per_attempt = risk_cap / attempts
   for b in bullets:
       if b['active_trade_id'] is None:
           b['capital'] = bet_per_attempt
           b['consecutive_wins'] = 0
           b['pending_reset'] = False
       else:
           b['pending_reset'] = True
           b['next_capital'] = bet_per_attempt
   ```
3. In `engine/simulator.py` (active bullets exit handling when `bullet.get('pending_reset')` is True):
   ```python
   if bullet.get('pending_reset'):
       if is_win:
           safe_core += pnl
       bullet['capital'] = bullet.pop('next_capital', bet_per_attempt)
       bullet['consecutive_wins'] = 0
       bullet['pending_reset'] = False
   ```
4. In `engine/simulator.py` (equity curve reporting):
   ```python
   active_bullets_cap = sum(b['capital'] for b in bullets)
   current_equity = safe_core + active_bullets_cap
   ```
5. In `tests/test_simulator_integrity.py`:
   Update `test_multi_asset_barbell_reset_in_flight_trade_accounting` to assert absolute equity conservation:
   `self.assertAlmostEqual(res['equity_curve'][-1]['equity'], initial_capital + sum(t['pnl'] for t in res['trades']), places=4)`

Instructions:
1. Inspect `c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/reviewer_3/handoff.md`.
2. Apply the required fixes in `engine/simulator.py` and `tests/test_simulator_integrity.py`.
3. Verify zero phantom profit by running the near-zero payout test:
   `python -c "import pandas as pd; from engine.simulator import BinarySimulator; day = 86400; t1 = 1767261600; times = [t1 + i * day for i in range(20)]; eur_df = pd.DataFrame({'open_time': times, 'open': [1.1]*20, 'high': [1.105]*20, 'low': [1.095]*20, 'close': [1.102]*20, 'volume': [1000]*20}); signals = [{'time': times[i], 'direction': 'CALL'} for i in range(0, 20, 2)]; sim = BinarySimulator(); res = sim.run_multi_asset({'EURUSD': eur_df}, {'EURUSD': signals}, expiry_candles=1, payout=0.0001, initial_capital=1000.0, mode='BARBELL', n_consecutive=2, bet_fraction=0.5, risk_ratio=0.20); print('Final equity:', res['equity_curve'][-1]['equity'])"`
   (Must output ~1000.00).
4. Run:
   - `python c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/challenger_1_r2/test_2b_barbell_reset_scenario.py`
   - `python -m unittest tests/test_simulator_integrity.py`
   - `pytest test_high_winrate_mechanisms.py`
   - `pytest tests/`
5. Write `handoff.md` in `c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/worker_4/handoff.md` and send completion message via `send_message`.
