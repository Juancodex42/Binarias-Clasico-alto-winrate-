"""
Multi-Dimensional Search Space Specifications (Feature 13 - Milestone 3).
Module: engine/search_space.py (Proposed Implementation Blueprint)
Targeting Out-Of-Sample (OOS) Win Rate > 65% and EV > 0.0
"""

from typing import Dict, Any, List

SEARCH_SPACE_DIMENSIONS = {
    "dimension_1_timeframes": [
        "1m", "5m", "15m", "30m", "1h", "4h", "1d"
    ],
    "dimension_2_expirations": [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
    ],
    "dimension_3_session_hours": {
        "ALL": "00:00 - 24:00 UTC",
        "ASIAN": "00:00 - 08:00 UTC",
        "LONDON": "08:00 - 16:00 UTC",
        "NEW_YORK": "13:00 - 21:00 UTC",
        "OVERLAP_LDN_NY": "13:00 - 16:00 UTC"
    },
    "dimension_4_indicator_periods": {
        "rsi_period": {"min": 2, "max": 30, "step": 1},
        "rsi_oversold": {"min": 15.0, "max": 35.0, "step": 1.0},
        "rsi_overbought": {"min": 65.0, "max": 85.0, "step": 1.0},
        "bb_period": {"min": 10, "max": 50, "step": 1},
        "bb_std": {"min": 1.5, "max": 3.5, "step": 0.1},
        "wick_ratio": {"min": 0.10, "max": 0.60, "step": 0.05},
        "vol_mult": {"min": 0.5, "max": 2.5, "step": 0.1},
        "natr_period": {"min": 7, "max": 28, "step": 1},
        "ema_fast": {"min": 5, "max": 30, "step": 1},
        "ema_slow": {"min": 20, "max": 100, "step": 1},
        "ema_weekly": {"min": 5, "max": 100, "step": 5},
        "pullback_tolerance": {"min": 0.001, "max": 0.050, "step": 0.002}
    },
    "dimension_5_probability_thresholds": {
        "meta_threshold": {"min": 0.50, "max": 0.90, "step": 0.05},
        "regime_breakeven": {"min": 0.45, "max": 0.60, "step": 0.02}
    }
}

ACCEPTANCE_TARGETS = {
    "target_oos_win_rate": 0.65,      # > 65% OOS Win Rate
    "target_oos_ev": 0.0,             # EV per trade > 0.0
    "breakeven_win_rate_85": 0.5405,  # 1 / (1 + 0.85) = 54.05%
    "min_oos_trades": 30,             # Statistical significance threshold
    "confidence_level": 0.95,         # Wilson 95% CI lower bound > breakeven_win_rate_85
}
