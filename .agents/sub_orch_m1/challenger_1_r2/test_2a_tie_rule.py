import sys
import os
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from engine.simulator import BinarySimulator

def run_test_2a():
    print("=== TEST 2A: BinarySimulator.run_multi_asset tie_rule Handling ===")
    
    # 1. Construct synthetic universe data with exact tie situations
    # Pair EURUSD: 10 candles (open_time 1000, 2000, ..., 10000)
    # Open price = 1.1000, Close price = 1.1000 for exit candle -> exact tie!
    
    times = [1000 * i for i in range(1, 11)]
    # Entry at candle index 1 (time 2000). Entry price will be open[2] = 1.1000.
    # Expiry = 2 candles -> exit candle index 1 + 2 = 3. Close[3] = 1.1000.
    opens =  [1.1000, 1.1000, 1.1000, 1.1000, 1.1000, 1.1000, 1.1000, 1.1000, 1.1000, 1.1000]
    closes = [1.1000, 1.1000, 1.1000, 1.1000, 1.1000, 1.1000, 1.1000, 1.1000, 1.1000, 1.1000]
    highs =  [1.1010] * 10
    lows =   [1.0990] * 10
    vols =   [100] * 10
    
    df_eurusd = pd.DataFrame({
        'open_time': times,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': vols
    })
    
    universe_data = {'EURUSD': df_eurusd}
    signals_by_pair = {'EURUSD': [{'time': 2000, 'direction': 'CALL'}]}
    
    sim = BinarySimulator()
    
    # --- Test Case A1: tie_rule = 'RETURN_STAKE' ---
    res_return = sim.run_multi_asset(
        universe_data=universe_data,
        signals_by_pair=signals_by_pair,
        expiry_candles=2,
        payout=0.85,
        initial_capital=1000.0,
        mode='SIMPLE',
        bet_fraction=0.1,
        tie_rule='RETURN_STAKE'
    )
    
    trades_return = res_return['trades']
    summary_return = res_return['summary']
    equity_return = res_return['equity_curve']
    
    print("\n--- Test Case A1: tie_rule = 'RETURN_STAKE' ---")
    print(f"Total trades: {summary_return['total_trades']}")
    print(f"Wins: {summary_return['wins']}, Losses: {summary_return['losses']}, Ties: {summary_return['ties']}")
    print(f"Net PnL: {summary_return['net_pnl']}")
    print(f"Final Equity: {equity_return[-1]['equity']}")
    if len(trades_return) > 0:
        t = trades_return[0]
        print(f"Trade result: {t['result']}, PnL: {t['pnl']}, Bet Size: {t['bet_size']}")
    
    # Assertions for RETURN_STAKE
    assert summary_return['total_trades'] == 1, f"Expected 1 trade, got {summary_return['total_trades']}"
    assert summary_return['ties'] == 1, f"Expected 1 tie, got {summary_return['ties']}"
    assert summary_return['wins'] == 0, f"Expected 0 wins, got {summary_return['wins']}"
    assert summary_return['losses'] == 0, f"Expected 0 losses, got {summary_return['losses']}"
    assert trades_return[0]['result'] == 'TIE', f"Expected result 'TIE', got '{trades_return[0]['result']}'"
    assert trades_return[0]['pnl'] == 0.0, f"Expected PnL 0.0, got {trades_return[0]['pnl']}"
    assert equity_return[-1]['equity'] == 1000.0, f"Expected Equity 1000.0, got {equity_return[-1]['equity']}"
    
    # --- Test Case A2: tie_rule = 'LOSS' ---
    res_loss = sim.run_multi_asset(
        universe_data=universe_data,
        signals_by_pair=signals_by_pair,
        expiry_candles=2,
        payout=0.85,
        initial_capital=1000.0,
        mode='SIMPLE',
        bet_fraction=0.1,
        tie_rule='LOSS'
    )
    
    trades_loss = res_loss['trades']
    summary_loss = res_loss['summary']
    equity_loss = res_loss['equity_curve']
    
    print("\n--- Test Case A2: tie_rule = 'LOSS' ---")
    print(f"Total trades: {summary_loss['total_trades']}")
    print(f"Wins: {summary_loss['wins']}, Losses: {summary_loss['losses']}, Ties: {summary_loss['ties']}")
    print(f"Net PnL: {summary_loss['net_pnl']}")
    print(f"Final Equity: {equity_loss[-1]['equity']}")
    if len(trades_loss) > 0:
        t = trades_loss[0]
        print(f"Trade result: {t['result']}, PnL: {t['pnl']}, Bet Size: {t['bet_size']}")
        
    # Assertions for LOSS
    assert summary_loss['total_trades'] == 1, f"Expected 1 trade, got {summary_loss['total_trades']}"
    assert summary_loss['ties'] == 0, f"Expected 0 ties, got {summary_loss['ties']}"
    assert summary_loss['wins'] == 0, f"Expected 0 wins, got {summary_loss['wins']}"
    assert summary_loss['losses'] == 1, f"Expected 1 loss, got {summary_loss['losses']}"
    assert trades_loss[0]['result'] == 'LOSS', f"Expected result 'LOSS', got '{trades_loss[0]['result']}'"
    assert trades_loss[0]['pnl'] == -100.0, f"Expected PnL -100.0, got {trades_loss[0]['pnl']}"
    assert equity_loss[-1]['equity'] == 900.0, f"Expected Equity 900.0, got {equity_loss[-1]['equity']}"

    print("\n[PASS] Test 2A passed all assertions successfully!")

if __name__ == "__main__":
    run_test_2a()
