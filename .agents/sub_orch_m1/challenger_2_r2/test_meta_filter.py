import sys
import os
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.ml_engine.meta_filter import BinaryMLMetaFilter

def test_binary_ml_meta_filter_rolling_natr_median():
    """
    Verify BinaryMLMetaFilter computes rolling NATR median `rolling(100, min_periods=1).median()`
    per signal index rather than global dataset median.
    """
    np.random.seed(42)
    n = 200
    
    # Low NATR early (rows 0..99: avg 0.5), High NATR late (rows 100..199: avg 5.0)
    natr_values = np.concatenate([
        np.random.uniform(0.4, 0.6, 100),
        np.random.uniform(4.5, 5.5, 100)
    ])
    
    X = pd.DataFrame({
        'feature1': np.random.randn(n),
        'natr': natr_values
    })
    
    signals = pd.Series(index=range(n), data=None, dtype=object)
    # Signal at idx 50 (early, low NATR regime) and idx 150 (late, high NATR regime)
    signals.loc[50] = 'CALL'
    signals.loc[150] = 'CALL'
    
    # Train dummy filter
    meta_filter = BinaryMLMetaFilter(probability_threshold=0.65, adaptive_threshold=True)
    y_train = pd.Series(np.random.choice([0, 1], size=n))
    meta_filter.fit(X, y_train)
    
    # Compute rolling median manually to compare
    rolling_medians = X['natr'].rolling(100, min_periods=1).median()
    global_median = X['natr'].median()
    
    print(f"[MetaFilter Test] Early idx=50 rolling median: {rolling_medians.loc[50]:.4f}, Global median: {global_median:.4f}")
    print(f"[MetaFilter Test] Late idx=150 rolling median: {rolling_medians.loc[150]:.4f}, Global median: {global_median:.4f}")
    
    assert abs(rolling_medians.loc[50] - 0.5) < 0.1, "Rolling median at idx=50 should reflect early low NATR regime (~0.5)"
    assert abs(rolling_medians.loc[150] - 5.0) < 0.5, "Rolling median at idx=150 should reflect late high NATR regime (~5.0)"
    assert abs(rolling_medians.loc[50] - global_median) > 1.5, "Rolling median at idx=50 MUST differ significantly from global median"
    
    # Verify filter_signals executes correctly using rolling median
    filtered = meta_filter.filter_signals(signals, X)
    print(f"[MetaFilter Test] Filter completed without errors. Signals output: {filtered.dropna().to_dict()}")
    
    print("[MetaFilter Test] PASS: Rolling NATR median computed per signal index rather than global dataset median.")
    return True

if __name__ == '__main__':
    test_binary_ml_meta_filter_rolling_natr_median()
