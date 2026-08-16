import sys
import os
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from engine.simulator import BinarySimulator

def run_test_2b_in_flight():
    print("=== TEST 2B: Barbell Campaign Reset with Active In-Flight Trade ===")

    # Daily timestamps in seconds:
    day = 86400
    t1 = 1767261600 # 2026-01-01 (Day 1)
    t2 = t1 + day    # Day 2
    t3 = t1 + 2*day  # Day 3
    t4 = t1 + 3*day  # Day 4
    t5 = t1 + 4*day  # Day 5
    t6 = t1 + 5*day  # Day 6
    t7 = t1 + 6*day  # Day 7
    
    # EURUSD timestamps: [Day 1, Day 2, Day 3, Day 4, Day 5, Day 6, Day 7]
    eur_df = pd.DataFrame({
        'open_time': [t1, t2, t3, t4, t5, t6, t7],
        'open':  [1.1000] * 7,
        'high':  [1.1050] * 7,
        'low':   [1.0950] * 7,
        'close': [1.1020] * 7, # CALL wins
        'volume': [1000] * 7
    })
    
    # BTCUSDT timestamps: [Day 1, Day 2, Day 6, Day 7, Day 8]
    btc_df = pd.DataFrame({
        'open_time': [t1, t2, t6, t7, t1 + 7*day],
        'open':  [50000.0] * 5,
        'high':  [50500.0] * 5,
        'low':   [49500.0] * 5,
        'close': [50200.0] * 5, # CALL wins
        'volume': [100] * 5
    })
    
    universe_data = {
        'EURUSD': eur_df,
        'BTCUSDT': btc_df
    }
    
    # Initial capital = 1000.0, risk_ratio = 0.20 (safe_core = 800.0, risk_cap = 200.0)
    # bet_fraction = 0.5 -> 2 bullets: bullet 0 (100.0), bullet 1 (100.0)
    # n_consecutive = 2
    # payout = 0.85
    
    # Signals:
    # 1) EURUSD at Day 1 (t1): Entry at Day 2 (t2), exit at Day 3 (t3). (WIN: PnL +85, cap 185, wins 1)
    # 2) BTCUSDT at Day 1 (t1): Entry at Day 2 (t2), exit at Day 6 (t6). (IN FLIGHT until Day 6!)
    # 3) EURUSD at Day 3 (t3): Entry at Day 4 (t4), exit at Day 5 (t5). (WIN 2nd in row -> CAMPAIGN RESET at Day 5!)
    # 4) BTCUSDT exits at Day 6 (t6).
    
    signals_by_pair = {
        'EURUSD': [
            {'time': t1, 'direction': 'CALL'}, # Entry Day 2, exit Day 3
            {'time': t3, 'direction': 'CALL'}  # Entry Day 4, exit Day 5 -> campaign reset!
        ],
        'BTCUSDT': [
            {'time': t1, 'direction': 'CALL'}  # Entry Day 2, exit Day 6 -> in flight during reset at Day 5!
        ]
    }
    
    sim = BinarySimulator()
    res = sim.run_multi_asset(
        universe_data=universe_data,
        signals_by_pair=signals_by_pair,
        expiry_candles=1,
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
    
    print("\n--- Trades Chronological Order ---")
    for idx, tr in enumerate(trades):
        print(f"Trade {idx+1}: Pair={tr['pair']}, Entry={tr['time']}, Exit={tr['exit_time']}, Result={tr['result']}, Bet={tr['bet_size']}, PnL={tr['pnl']}")

    print("\n--- Equity Curve ---")
    for eq in equity_curve:
        print(f"Time={eq['time']}, Equity={eq['equity']}")

    print("\n--- Summary ---")
    print(f"Total trades: {summary['total_trades']}")
    print(f"Wins: {summary['wins']}, Losses: {summary['losses']}, Net PnL: {summary['net_pnl']}")
    print(f"Final Equity: {equity_curve[-1]['equity']}")

    eur_trades = [t for t in trades if t['pair'] == 'EURUSD']
    btc_trade = next(t for t in trades if t['pair'] == 'BTCUSDT')
    
    print(f"\nEURUSD Trade 1 (Exit Day 3): Bet={eur_trades[0]['bet_size']}, PnL={eur_trades[0]['pnl']}")
    print(f"EURUSD Trade 2 (Exit Day 5 - Reset Trigger): Bet={eur_trades[1]['bet_size']}, PnL={eur_trades[1]['pnl']}")
    print(f"BTCUSDT Trade (Exit Day 6 - In Flight): Bet={btc_trade['bet_size']}, PnL={btc_trade['pnl']}")

    sum_pnl = sum(t['pnl'] for t in trades)
    # Check that in-flight trade PnL (+85.0) was added to equity upon exit at Day 6
    # Day 5 equity: 1256.475, Day 6 equity: 1455.70, Bullet 1 reset cap: 114.225
    # PnL captured = (Day 6 equity - Day 5 equity) - Bullet 1 reset cap = 1455.70 - 1256.475 - 114.225 = 85.0
    eq_day5 = equity_curve[-2]['equity']
    eq_day6 = equity_curve[-1]['equity']
    next_cap = 114.225
    in_flight_pnl_captured = (eq_day6 - eq_day5) - next_cap
    discrepancy = btc_trade['pnl'] - in_flight_pnl_captured

    print(f"\nSum of all trade PnLs: {sum_pnl:.4f}")
    print(f"BTCUSDT In-Flight PnL: {btc_trade['pnl']:.4f}")
    print(f"Equity gain between Day 5 and Day 6: {eq_day6 - eq_day5:.4f}")
    print(f"In-flight PnL captured in safe_core: {in_flight_pnl_captured:.4f}")

    if abs(discrepancy) > 1e-4:
        print(f"\n[FAIL] Discrepancy detected! In-flight trade PnL was wiped out during campaign reset.")
    else:
        print(f"\n[PASS] No discrepancy! In-flight trade PnL and equity accounting preserved perfectly.")

    return res

if __name__ == "__main__":
    run_test_2b_in_flight()
