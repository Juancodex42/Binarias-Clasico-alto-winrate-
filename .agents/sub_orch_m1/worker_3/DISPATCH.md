## 2026-08-12T17:40:12Z
Task Objective:
Remediate the Barbell campaign reset PnL overwrite bug in `engine/simulator.py` (lines 549-556) identified by challenger_1_r2.

Bug Description & Context:
When a Barbell campaign reset occurs while another bullet has a trade in flight (`pending_reset = True`), lines 549-556 in `engine/simulator.py` currently overwrite `bullet['capital']` with `next_capital` and reset `consecutive_wins` to 0 upon trade exit. Because `safe_core` was consolidated at the reset timestamp (before the in-flight trade exited), the PnL of the in-flight trade is NEVER added to `safe_core` AND is wiped from the bullet's capital. This creates an equity accounting discrepancy between total trade PnLs and equity gain.

Required Fix in `engine/simulator.py`:
When `bullet.get('pending_reset')` is True:
If `is_win` (the in-flight trade won):
Consolidate the winning PnL into `safe_core`: `safe_core += pnl`.
Then reset the bullet: `bullet['capital'] = bullet.pop('next_capital', bet_per_attempt)`, `bullet['consecutive_wins'] = 0`, `bullet['pending_reset'] = False`.

Instructions:
1. Inspect `c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/challenger_1_r2/handoff.md` and `c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/challenger_1_r2/test_2b_barbell_reset_scenario.py`.
2. Modify `engine/simulator.py` around lines 549-556 to consolidate winning PnL into `safe_core` (`safe_core += pnl`) when `bullet.get('pending_reset')` is True.
3. Update `tests/test_simulator_integrity.py` to include a unit test verifying Barbell campaign reset with active in-flight trade accounting consistency.
4. Execute and verify all test suites:
   - `python c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/challenger_1_r2/test_2b_barbell_reset_scenario.py`
   - `python -m unittest tests/test_simulator_integrity.py`
   - `pytest test_high_winrate_mechanisms.py`
   - `pytest tests/`
5. Write `handoff.md` in `c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/worker_3/handoff.md` detailing changes and test outputs.
6. Send a completion message to parent sub-orchestrator using send_message.
