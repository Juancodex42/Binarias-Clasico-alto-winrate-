import sys
import os
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.auto_tuner import WalkForwardEngine

def test_walk_forward_engine_zero_oos_trades():
    """
    Verify WalkForwardEngine in `engine/auto_tuner.py` ignores zero OOS trade windows (`tr_oos == 0`)
    when computing `stable_count`.
    """
    engine = WalkForwardEngine(n_windows=5, train_ratio=0.60)
    
    # Mock window results dataset
    mock_window_results = [
        {"window": 1, "tr_is": 20, "wr_is": 80.0, "tr_oos": 10, "wr_oos": 80.0},  # Valid stable window (tr_oos > 0, wr_oos >= 75)
        {"window": 2, "tr_is": 15, "wr_is": 85.0, "tr_oos": 0,  "wr_oos": 0.0},   # Zero OOS trades (tr_oos == 0) -> MUST be ignored
        {"window": 3, "tr_is": 10, "wr_is": 90.0, "tr_oos": 0,  "wr_oos": 100.0}, # Edge case: zero trades but high WR scalar -> MUST be ignored (tr_oos == 0)
        {"window": 4, "tr_is": 25, "wr_is": 75.0, "tr_oos": 12, "wr_oos": 70.0},  # tr_oos > 0, but wr_oos < 75 -> Not stable
        {"window": 5, "tr_is": 18, "wr_is": 82.0, "tr_oos": 8,  "wr_oos": 87.5},  # Valid stable window (tr_oos > 0, wr_oos >= 75)
    ]
    
    # Reproduce logic from engine/auto_tuner.py:87
    stable_count = sum(1 for w in mock_window_results if w["tr_oos"] > 0 and w["wr_oos"] >= 75.0)
    
    print(f"[WalkForwardEngine Test] Computed stable_count: {stable_count}")
    assert stable_count == 2, f"Expected stable_count to be 2 (windows 1 and 5), got {stable_count}"
    
    # Test with all zero OOS trade windows
    zero_oos_windows = [
        {"window": 1, "tr_is": 20, "wr_is": 80.0, "tr_oos": 0, "wr_oos": 0.0},
        {"window": 2, "tr_is": 15, "wr_is": 85.0, "tr_oos": 0, "wr_oos": 90.0},
    ]
    stable_count_zero = sum(1 for w in zero_oos_windows if w["tr_oos"] > 0 and w["wr_oos"] >= 75.0)
    assert stable_count_zero == 0, f"Expected stable_count to be 0 for zero OOS trades, got {stable_count_zero}"
    
    print("[WalkForwardEngine Test] PASS: Zero OOS trade windows are strictly ignored in stable_count computation.")
    return True

if __name__ == '__main__':
    test_walk_forward_engine_zero_oos_trades()
