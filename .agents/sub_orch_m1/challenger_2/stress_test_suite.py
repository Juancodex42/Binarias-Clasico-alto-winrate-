import sys
import os
import time
import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, r'c:\Users\juanc\Desktop\prueba')

from engine.simulator import BinarySimulator
from engine.ml_engine.feature_extractor import frac_diff_fixed, BinaryFeatureExtractor
from engine.ml_engine.cusum_monitor import CUSUMMonitor
from engine.ml_engine.regime_detector import RegimeDetector
from engine.ml_engine.meta_labeler import MetaLabeler
from engine.ml_engine.meta_filter import BinaryMLMetaFilter
from engine.auto_tuner import WalkForwardEngine

def test_1_simulator_multi_asset_barbell():
    print("=" * 60)
    print("TEST 1: BinarySimulator multi-asset tie_rule & Barbell streak resets")
    print("=" * 60)
    sim = BinarySimulator()

    # Generate synthetic multi-asset data
    dates = pd.date_range('2026-01-01', periods=200, freq='1min')
    open_times = [int(d.timestamp()) for d in dates]

    # Create 2 assets with identical price sequences initially
    df_asset1 = pd.DataFrame({
        'open_time': open_times,
        'open': [100.0] * 200,
        'high': [102.0] * 200,
        'low': [98.0] * 200,
        'close': [100.0] * 200,
        'volume': [1000] * 200
    })
    df_asset2 = pd.DataFrame({
        'open_time': open_times,
        'open': [50.0] * 200,
        'high': [52.0] * 200,
        'low': [48.0] * 200,
        'close': [50.0] * 200,
        'volume': [1000] * 200
    })

    # Modify exit candles for specific trades
    # Asset 1 trade 1: entry idx 10 (exit idx 12) -> WIN
    df_asset1.loc[12, 'close'] = 105.0
    # Asset 1 trade 2: entry idx 100 (exit idx 102) -> TIE (close=100.0)

    # Asset 2 trade 1: entry idx 11 (exit idx 13) -> WIN (overlapping with Asset 1 trade 1!)
    df_asset2.loc[13, 'close'] = 55.0

    universe_data = {'EURUSD': df_asset1, 'GBPUSD': df_asset2}
    signals_by_pair = {
        'EURUSD': [{'time': open_times[10], 'direction': 'CALL'}, {'time': open_times[100], 'direction': 'CALL'}],
        'GBPUSD': [{'time': open_times[11], 'direction': 'CALL'}]
    }

    # Test tie_rule='LOSS' vs 'RETURN_STAKE'
    res_loss = sim.run_multi_asset(universe_data, signals_by_pair, expiry_candles=2, mode='SIMPLE', tie_rule='LOSS')
    res_stake = sim.run_multi_asset(universe_data, signals_by_pair, expiry_candles=2, mode='SIMPLE', tie_rule='RETURN_STAKE')

    print(f"Tie Rule 'LOSS' summary: {res_loss['summary']}")
    print(f"Tie Rule 'RETURN_STAKE' summary: {res_stake['summary']}")

    assert res_loss['summary']['ties'] == 0, f"Expected 0 ties for LOSS rule, got {res_loss['summary']['ties']}"
    assert res_stake['summary']['ties'] == 1, f"Expected 1 tie for RETURN_STAKE rule, got {res_stake['summary']['ties']}"
    assert res_loss['summary']['losses'] == res_stake['summary']['losses'] + 1, "LOSS rule should count TIE as LOSS"

    # Now test BARBELL overlapping streak reset
    # Asset 1 enters at t=10 (exit t=12), Asset 2 enters at t=11 (exit t=13)
    # Asset 1 finishes first at t=12. With n_consecutive=1, Asset 1 win completes campaign!
    # Does Asset 2 (active at t=12, exits at t=13) preserve its profit or capital correctly?
    res_barbell = sim.run_multi_asset(universe_data, signals_by_pair, expiry_candles=2, mode='BARBELL', n_consecutive=1, bet_fraction=0.5, risk_ratio=0.20)

    print(f"Barbell Trades: {res_barbell['trades']}")
    print(f"Barbell Equity Curve: {res_barbell['equity_curve']}")
    print(f"Barbell Summary: {res_barbell['summary']}")

    return res_loss, res_stake, res_barbell

if __name__ == '__main__':
    test_1_simulator_multi_asset_barbell()
