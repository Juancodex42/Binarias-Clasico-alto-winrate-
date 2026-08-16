import sys, os, numpy as np, pandas as pd
sys.path.insert(0, r'c:\Users\juanc\Desktop\prueba')

from engine.simulator import BinarySimulator
from optimizer_grid_search import create_labels

def generate_test_ohlcv(n_rows=500, seed=42):
    np.random.seed(seed)
    returns = np.random.normal(0.0002, 0.01, n_rows)
    price = 100.0 * np.exp(np.cumsum(returns))
    high = price * (1.0 + np.abs(np.random.normal(0, 0.005, n_rows)))
    low = price * (1.0 - np.abs(np.random.normal(0, 0.005, n_rows)))
    open_p = price * (1.0 + np.random.normal(0, 0.002, n_rows))
    close_p = price
    volume = np.random.uniform(100, 1000, n_rows)
    open_time = np.arange(n_rows) * 300 + 1600000000

    df = pd.DataFrame({
        'open_time': open_time,
        'open': open_p,
        'high': high,
        'low': low,
        'close': close_p,
        'volume': volume
    })
    return df

df = generate_test_ohlcv(n_rows=300, seed=42)
signals = pd.Series(index=df.index, dtype=object)
np.random.seed(42)
signals.iloc[:] = np.random.choice(['CALL', 'PUT', None], size=len(df), p=[0.2, 0.2, 0.6])

sim = BinarySimulator()
res = sim.run(df, signals, expiry_candles=1, initial_capital=1e9)
sim_trades = {t['index']: t for t in res['trades']}

labels = create_labels(df, signals, expiry_candles=1)

out_path = r'c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_challenger_m2_1\diag2.txt'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(f"Total signals in series: {(signals.isin(['CALL', 'PUT'])).sum()}\n")
    f.write(f"Total labels created: {len(labels)}\n")
    f.write(f"Total trades in sim: {len(sim_trades)}\n")
    missing_in_sim = []
    for idx in labels.index:
        if idx not in sim_trades:
            missing_in_sim.append(idx)
    f.write(f"Missing in sim ({len(missing_in_sim)}): {missing_in_sim}\n\n")

    # Trace first few missing indices
    for m in missing_in_sim[:10]:
        prev_trades = [t for t in res['trades'] if t['index'] < m]
        last_prev = prev_trades[-1] if prev_trades else None
        f.write(f"Signal idx {m} (sig={signals.loc[m]}): last prev trade in sim: {last_prev}\n")
    f.flush()
print("DIAG2 DONE")
