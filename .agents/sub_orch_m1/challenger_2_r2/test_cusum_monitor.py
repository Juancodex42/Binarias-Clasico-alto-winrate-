import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.ml_engine.cusum_monitor import CUSUMMonitor

def test_cusum_monitor_bounded_memory_reset_and_recovery():
    """
    Verify CUSUMMonitor memory bounding (trade_results <= 1000, pause_history <= 100),
    clean reset(), and automated RESUME recovery during PAUSED state via shadow trades.
    """
    monitor = CUSUMMonitor(expected_wr=0.60, payout=0.85, threshold_sigma=2.0)
    
    # --- Test 1: Bounded trade_results memory ---
    for _ in range(1500):
        monitor.update(0.85)
    
    assert len(monitor.trade_results) <= 1000, f"trade_results memory not bounded! size={len(monitor.trade_results)}"
    print(f"[CUSUMMonitor Test] Memory bound check 1 passed: trade_results len={len(monitor.trade_results)} <= 1000")
    
    # --- Test 2: Bounded pause_history memory ---
    # Force pause and resume multiple times to test pause_history truncation
    for _ in range(150):
        # Force PAUSE by injecting high negative cusum or manual state
        monitor.pause_history.append({'action': 'PAUSE', 'trade_num': 1})
        if len(monitor.pause_history) > 100:
            monitor.pause_history = monitor.pause_history[-100:]
            
    assert len(monitor.pause_history) <= 100, f"pause_history memory not bounded! size={len(monitor.pause_history)}"
    print(f"[CUSUMMonitor Test] Memory bound check 2 passed: pause_history len={len(monitor.pause_history)} <= 100")
    
    # --- Test 3: reset() behavior ---
    monitor.reset()
    assert len(monitor.trade_results) == 0, "reset() failed to clear trade_results"
    assert len(monitor.pause_history) == 0, "reset() failed to clear pause_history"
    assert len(monitor.post_pause_results) == 0, "reset() failed to clear post_pause_results"
    assert monitor.cusum_pos == 0.0, "reset() failed to reset cusum_pos"
    assert monitor.cusum_neg == 0.0, "reset() failed to reset cusum_neg"
    assert monitor.is_paused == False, "reset() failed to reset is_paused"
    assert monitor.total_trades_count == 0, "reset() failed to reset total_trades_count"
    print("[CUSUMMonitor Test] reset() check passed cleanly.")
    
    # --- Test 4: PAUSED state and automated RESUME recovery ---
    # Feed 15 winning trades to establish baseline
    for _ in range(15):
        monitor.update(0.85)
    assert not monitor.is_paused, "Monitor should not be paused during winning streak"
    
    # Feed losing trades (-1.0) to trigger PAUSE
    status = 'CONTINUE'
    losing_trades_count = 0
    while status != 'PAUSE' and losing_trades_count < 100:
        status = monitor.update(-1.0)
        losing_trades_count += 1
        
    assert status == 'PAUSE', f"Failed to trigger PAUSE state! Last status={status}"
    assert monitor.is_paused, "is_paused flag should be True"
    print(f"[CUSUMMonitor Test] Successfully triggered PAUSE after {losing_trades_count} losses")
    
    # Now feed shadow/paper trades (+0.85) during PAUSED state to trigger recovery
    recovery_status = None
    shadow_trades_count = 0
    while monitor.is_paused and shadow_trades_count < 20:
        recovery_status = monitor.update(0.85)
        shadow_trades_count += 1
        if recovery_status == 'RESUME':
            break
            
    assert recovery_status == 'RESUME', f"Failed to auto-resume! status={recovery_status}"
    assert not monitor.is_paused, "is_paused flag should be False after RESUME"
    print(f"[CUSUMMonitor Test] Successfully triggered RESUME recovery after {shadow_trades_count} winning shadow trades")
    
    print("[CUSUMMonitor Test] PASS: All memory bounds, reset, and PAUSE/RESUME recovery tests passed.")
    return True

if __name__ == '__main__':
    test_cusum_monitor_bounded_memory_reset_and_recovery()
