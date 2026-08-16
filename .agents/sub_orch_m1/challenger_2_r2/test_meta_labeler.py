import sys
import os
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.ml_engine.meta_labeler import MetaLabeler

def test_meta_labeler_timestamp_formats():
    """
    Verify MetaLabeler handles nanosecond, microsecond, millisecond, second epoch numeric timestamps
    and datetime dtypes without overflowing unit='s'.
    """
    n = 100
    base_time_s = 1700000000  # Nov 14 2023 ~ 22:13 UTC
    
    # Synthetic bar data
    np.random.seed(42)
    close = 100 + np.cumsum(np.random.randn(n) * 0.1)
    high = close + 0.1
    low = close - 0.1
    open_p = close + 0.01
    volume = np.random.randint(100, 1000, size=n)
    
    labeler = MetaLabeler()
    signal_indices = pd.Index([10, 20, 30, 40, 50, 60, 70, 80, 90])
    
    timestamp_cases = {
        "datetime64": pd.date_range('2026-01-01', periods=n, freq='min'),
        "epoch_seconds (s)": [base_time_s + i * 60 for i in range(n)],
        "epoch_milliseconds (ms)": [(base_time_s + i * 60) * 1000 for i in range(n)],
        "epoch_microseconds (us)": [(base_time_s + i * 60) * 1000000 for i in range(n)],
        "epoch_nanoseconds (ns)": [(base_time_s + i * 60) * 1000000000 for i in range(n)]
    }
    
    for name, open_time_col in timestamp_cases.items():
        df = pd.DataFrame({
            'open': open_p,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume,
            'open_time': open_time_col
        })
        
        try:
            context = labeler._extract_context_features(df, signal_indices)
            assert not context.empty, f"Extracted context dataframe is empty for format {name}"
            assert 'hour_of_day' in context.columns, f"hour_of_day missing for format {name}"
            assert 'day_of_week' in context.columns, f"day_of_week missing for format {name}"
            assert 'is_session_overlap' in context.columns, f"is_session_overlap missing for format {name}"
            assert not context['hour_of_day'].isna().any(), f"hour_of_day contains NaNs for format {name}"
            
            print(f"[MetaLabeler Test] Success for format '{name}': hour range [{context['hour_of_day'].min()}, {context['hour_of_day'].max()}]")
        except Exception as e:
            print(f"[MetaLabeler Test] FAILED for format '{name}': {e}")
            raise e

    print("[MetaLabeler Test] PASS: All timestamp types (s, ms, us, ns, datetime) parsed without overflow.")
    return True

if __name__ == '__main__':
    test_meta_labeler_timestamp_formats()
