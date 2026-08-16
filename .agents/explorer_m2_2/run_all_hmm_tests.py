import sys
import os
sys.path.insert(0, os.path.abspath('.'))
import pytest

print("--- RUNNING PYTEST FOR ALL REGIME DETECTOR / HMM TESTS ---", flush=True)

retcode = pytest.main([
    "tests/test_tier1_feature_coverage.py",
    "tests/test_tier2_boundary_corner_cases.py",
    "tests/test_tier3_cross_feature_combinations.py",
    "tests/test_tier4_real_world_scenarios.py",
    "-k", "regime or hmm or RegimeDetector",
    "-v",
    "--tb=short"
])

print("Pytest exit code:", retcode, flush=True)
