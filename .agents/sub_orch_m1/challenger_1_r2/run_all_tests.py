import sys
import os
import time

# Add current dir to sys.path
sys.path.insert(0, os.path.dirname(__file__))

import test_2a_tie_rule
import test_2b_barbell_reset_scenario
import test_2c_frac_diff

def main():
    print("=================================================================")
    print("  EMPIRICAL STRESS TEST SUITE - SUB_ORCH_M1 / CHALLENGER_1_R2  ")
    print("=================================================================\n")
    
    # Run 2a
    print(">>> RUNNING TEST 2A: tie_rule Handling")
    test_2a_tie_rule.run_test_2a()
    
    print("\n-----------------------------------------------------------------\n")
    
    # Run 2b
    print(">>> RUNNING TEST 2B: Barbell Campaign Reset with In-Flight Trades")
    test_2b_barbell_reset_scenario.run_test_2b_in_flight()
    
    print("\n-----------------------------------------------------------------\n")
    
    # Run 2c
    print(">>> RUNNING TEST 2C: Frac Diff FFT Equivalence & Speedup")
    test_2c_frac_diff.run_test_2c()

    print("\n=================================================================")
    print("  ALL EMPIRICAL TESTS COMPLETED  ")
    print("=================================================================")

if __name__ == "__main__":
    main()
