import sys
import os
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from engine.simulator import BinarySimulator

def run_test_2b():
    print("=== TEST 2B: Multi-asset Barbell Campaign Reset with Active Trades in Flight ===")

    # Create synthetic universe data for 2 assets: EURUSD and GBPUSD
    # Candle duration: 100s
    times = [1000 + i * 100 for i in range(50)]
    
    # EURUSD prices: upward trend so CALLs win
    eur_df = pd.DataFrame({
        'open_time': times,
        'open': [1.1000 + i * 0.001 for i in range(50)],
        'high': [1.1010 + i * 0.001 for i in range(50)],
        'low': [1.0990 + i * 0.001 for i in range(50)],
        'close': [1.1005 + i * 0.001 for i in range(50)],
        'volume': [100] * 50
    })
    
    # GBPUSD prices: upward trend so CALLs win
    gbp_df = pd.DataFrame({
        'open_time': times,
        'open': [1.3000 + i * 0.001 for i in range(50)],
        'high': [1.3010 + i * 0.001 for i in range(50)],
        'low': [1.2990 + i * 0.001 for i in range(50)],
        'close': [1.3005 + i * 0.001 for i in range(50)],
        'volume': [100] * 50
    })
    
    universe_data = {
        'EURUSD': eur_df,
        'GBPUSD': gbp_df
    }
    
    # Scenario setup:
    # Initial capital = 1000.0, risk_ratio = 0.20 (safe_core = 800.0, risk_cap = 200.0)
    # bet_fraction = 0.5 -> attempts = 2 bullets, initial bet_per_attempt = 100.0 each.
    # n_consecutive = 2 -> 2 consecutive wins in a bullet trigger a campaign reset.
    # payout = 0.85 -> win payout = +85%
    
    # Bullet 0 will take trade 1 on EURUSD at index 1 (time 1100), exit at index 3 (time 1300).
    # Bullet 1 will take trade 2 on GBPUSD at index 2 (time 1200), exit at index 6 (time 1600).
    # Bullet 0 will take trade 3 on EURUSD at index 3 (time 1300), exit at index 5 (time 1500).
    
    # Timeline:
    # t=1100: EURUSD trade 1 entered by Bullet 0 (bet 100).
    # t=1200: GBPUSD trade 2 entered by Bullet 1 (bet 100). [Bullet 1 in flight!]
    # t=1300: EURUSD trade 1 exits -> WIN! Bullet 0 capital = 185.0, consecutive_wins = 1.
    # t=1300: EURUSD trade 3 entered by Bullet 0 (bet 185.0). [Bullet 0 and Bullet 1 both in flight!]
    # t=1500: EURUSD trade 3 exits -> WIN! PnL = 185 * 0.85 = +157.25.
    #         Bullet 0 capital = 185 + 157.25 = 342.25. consecutive_wins = 2.
    #         CAMPAIGN RESET TRIGGERED at t=1500!
    #         safe_core += 342.25 -> 800 + 342.25 = 1142.25.
    #         risk_cap = 1142.25 * 0.20 = 228.45. bet_per_attempt = 114.225.
    #         Bullet 0 is free -> reset to capital 114.225, wins 0, pending_reset = False.
    #         Bullet 1 has active trade (trade 2) -> pending_reset = True, next_capital = 114.225.
    # t=1600: GBPUSD trade 2 exits -> WIN! (Payout +85 on bet 100 = +85.0 PnL).
    
    signals_by_pair = {
        'EURUSD': [
            {'time': 1100, 'direction': 'CALL'}, # Entry idx 1, exit idx 3 (t=1300)
            {'time': 1300, 'direction': 'CALL'}  # Entry idx 3, exit idx 5 (t=1500) -> Triggers reset!
        ],
        'GBPUSD': [
            {'time': 1200, 'direction': 'CALL'}  # Entry idx 2, exit idx 6 (t=1600) -> In flight during reset!
        ]
    }
    
    sim = BinarySimulator()
    res = sim.run_multi_asset(
        universe_data=universe_data,
        signals_by_pair=signals_by_pair,
        expiry_candles=2, # For EURUSD (will set custom expiry or check times)
        payout=0.85,
        initial_capital=1000.0,
        mode='BARBELL',
        n_consecutive=2,
        bet_fraction=0.5,
        risk_ratio=0.20
    )
    
    trades = res['trades']
    summary = res['summary']
    equity_curve = res['equity_curve']
    
    print("\n--- Trades Details ---")
    for idx, tr in enumerate(trades):
        print(f"Trade {idx+1}: Pair={tr['pair']}, Direction={tr['direction']}, EntryTime={tr['time']}, ExitTime={tr['exit_time']}, Result={tr['result']}, BetSize={tr['bet_size']}, PnL={tr['pnl']}")
        
    print("\n--- Equity Curve Details ---")
    for eq in equity_curve:
        print(f"Time={eq['time']}, Equity={eq['equity']}")
        
    print("\n--- Summary ---")
    print(f"Total trades: {summary['total_trades']}")
    print(f"Wins: {summary['wins']}, Losses: {summary['losses']}, Net PnL: {summary['net_pnl']}")
    print(f"Final Equity: {equity_curve[-1]['equity']}")
    
    # Calculate sum of all trade PnLs
    total_trade_pnl = sum(tr['pnl'] for tr in trades)
    print(f"Sum of trade PnLs: {total_trade_pnl}")
    print(f"Equity gain (Final Equity - Initial Capital): {equity_curve[-1]['equity'] - 1000.0}")

    # Check if Trade 2 (GBPUSD in flight during reset) PnL was preserved or wiped out
    # Trade 1: EURUSD (bet 100, PnL +85)
    # Trade 2: EURUSD (bet 185, PnL +157.25) -> triggers reset at t=1500
    # Trade 3: GBPUSD (bet 100, PnL +85) -> exits at t=1600 after reset at t=1500
    
    # Let's check what happened to Trade 3 (GBPUSD)
    gbp_trade = next(t for t in trades if t['pair'] == 'GBPUSD')
    print(f"\nGBPUSD trade PnL recorded in trade list: {gbp_trade['pnl']}")
    
    # Verify equity behavior
    # Is total trade PnL reflected in final equity?
    expected_ideal_equity = 1000.0 + total_trade_pnl
    actual_final_equity = equity_curve[-1]['equity']
    
    print(f"Expected Ideal Final Equity (Initial + Sum(PnL)): {expected_ideal_equity}")
    print(f"Actual Final Equity: {actual_final_equity}")
    print(f"Discrepancy (Ideal - Actual): {expected_ideal_equity - actual_final_equity}")

    return {
        'trades': trades,
        'summary': summary,
        'equity_curve': equity_curve,
        'discrepancy': expected_ideal_equity - actual_final_equity
    }

if __name__ == "__main__":
    run_test_2b()
