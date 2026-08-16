import sys
import os
import traceback

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from test_regime_detector import test_regime_detector_lookahead_leakage
from test_cusum_monitor import test_cusum_monitor_bounded_memory_reset_and_recovery
from test_meta_labeler import test_meta_labeler_timestamp_formats
from test_meta_filter import test_binary_ml_meta_filter_rolling_natr_median
from test_auto_tuner import test_walk_forward_engine_zero_oos_trades

def run_suite():
    tests = [
        ("Check 2a: RegimeDetector Zero Look-Ahead Leakage", test_regime_detector_lookahead_leakage),
        ("Check 2b: CUSUMMonitor Bounded Memory, Reset, & Shadow Recovery", test_cusum_monitor_bounded_memory_reset_and_recovery),
        ("Check 2c: MetaLabeler Multi-Unit Epoch & Datetime Handling", test_meta_labeler_timestamp_formats),
        ("Check 2d: BinaryMLMetaFilter Rolling NATR Median per Signal Index", test_binary_ml_meta_filter_rolling_natr_median),
        ("Check 2e: WalkForwardEngine Zero OOS Trade Window Filtering", test_walk_forward_engine_zero_oos_trades),
    ]
    
    results = {}
    all_passed = True
    
    print("=" * 80)
    print("RUNNING EMPIRICAL SUITE FOR CHALLENGER 2 (MILESTONE M1 RE-VERIFICATION)")
    print("=" * 80)
    
    for name, test_fn in tests:
        print(f"\n---> Executing: {name}")
        try:
            passed = test_fn()
            results[name] = "PASS" if passed else "FAIL"
        except Exception as e:
            print(f"FAILED with error: {e}")
            traceback.print_exc()
            results[name] = f"FAIL ({e})"
            all_passed = False
            
    print("\n" + "=" * 80)
    print("EMPIRICAL TEST SUITE SUMMARY")
    print("=" * 80)
    for name, status in results.items():
        print(f"[{status}] {name}")
    print("=" * 80)
    
    if all_passed:
        print("\nOVERALL VERDICT: PASS")
        sys.exit(0)
    else:
        print("\nOVERALL VERDICT: FAIL")
        sys.exit(1)

if __name__ == '__main__':
    run_suite()
