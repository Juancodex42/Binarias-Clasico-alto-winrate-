import numpy as np
import pandas as pd

def compute_wilders_rsi(close: pd.Series, period: int) -> pd.Series:
    """
    Computes Wilder's Smoothing RSI matching the Rust implementation exactly.
    """
    closes_val = close.values
    n = len(closes_val)
    rsi_vals = np.full(n, np.nan, dtype=float)
    
    if n <= period:
        return pd.Series(rsi_vals, index=close.index)
        
    gains = np.zeros(n)
    losses = np.zeros(n)
    
    for i in range(1, n):
        diff = closes_val[i] - closes_val[i - 1]
        if diff > 0:
            gains[i] = diff
        else:
            losses[i] = -diff
            
    # First Average Gain & Loss (SMA of first 'period' diffs)
    # Gains and losses start from index 1. Index period is the 'period'-th difference.
    # Therefore, we sum from index 1 to period (inclusive).
    avg_gain = np.sum(gains[1:period + 1]) / period
    avg_loss = np.sum(losses[1:period + 1]) / period
    
    if avg_loss == 0.0:
        rsi_vals[period] = 50.0 if avg_gain == 0.0 else 100.0
    else:
        rs = avg_gain / avg_loss
        rsi_vals[period] = 100.0 - (100.0 / (1.0 + rs))
        
    for i in range(period + 1, n):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0.0:
            rsi_vals[i] = 50.0 if avg_gain == 0.0 else 100.0
        else:
            rs = avg_gain / avg_loss
            rsi_vals[i] = 100.0 - (100.0 / (1.0 + rs))
            
    return pd.Series(rsi_vals, index=close.index)


def compute_ema(close: pd.Series, period: int) -> pd.Series:
    """
    Computes EMA with SMA initialization matching the Rust implementation exactly.
    """
    closes_val = close.values
    n = len(closes_val)
    ema_vals = np.full(n, np.nan, dtype=float)
    
    if n < period:
        return pd.Series(ema_vals, index=close.index)
        
    k = 2.0 / (period + 1)
    
    # First SMA
    sma = np.sum(closes_val[:period]) / period
    ema_vals[period - 1] = sma
    
    for i in range(period, n):
        ema_vals[i] = closes_val[i] * k + ema_vals[i - 1] * (1.0 - k)
        
    return pd.Series(ema_vals, index=close.index)
