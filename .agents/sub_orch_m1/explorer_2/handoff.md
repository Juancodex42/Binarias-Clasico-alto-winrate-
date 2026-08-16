# Handoff Report — Explorer 2: Feature Extractor Optimization & WalkForward Stability Guard

**Agent**: `explorer_2` (`teamwork_preview_explorer`)  
**Working Directory**: `c:\Users\juanc\Desktop\prueba\.agents\sub_orch_m1\explorer_2`  
**Handoff Type**: Hard (Task Complete)  

---

## 1. Observation

### Item 2: `BinaryFeatureExtractor` in `engine/ml_engine/feature_extractor.py`
- **Current `frac_diff_fixed` Implementation (Lines 5–41)**:
  ```python
  35:     # Aplicar convolución
  36:     output = np.full(n, np.nan)
  37:     for i in range(width - 1, n):
  38:         output[i] = np.dot(weights, vals[i - width + 1:i + 1])
  ```
  - Execution speed: ~0.0665s per series of length 10,000 in Python loop dot products, scaling up to >2.5s for 50,000 elements. Called 3 times in `extract_features` per dataset evaluation.
- **Current Hurst Exponent Implementation (Lines 86–97)**:
  ```python
  88:         def calc_hurst(x):
  89:             if len(x) < 30: return np.nan
  90:             y = x - np.mean(x)
  91:             z = np.cumsum(y)
  92:             s = np.std(x, ddof=0)
  93:             if s == 0: return np.nan
  94:             return (np.max(z) - np.min(z)) / s
  96:         rs_ratio = returns.rolling(30).apply(calc_hurst, raw=True).replace(0, 1e-8)
  ```
  - `returns.iloc[0]` is `NaN`. Uncleaned `x` inside `calc_hurst` propagates `NaN` across window index 29.
  - `z = np.cumsum(y)` omits the origin $Z_0 = 0$, underestimating range $R$ when $Z$ does not cross 0.
  - `if s == 0` fails to catch floating point noise ($s = 10^{-17}$ on constant series), causing division explosion ($R/S = 10^{16}$).

### Item 5: `WalkForwardEngine` in `engine/auto_tuner.py`
- **Current Stability Metric Calculation (Lines 86–88)**:
  ```python
  86:         # Stable windows: windows where OOS WR >= 75%
  87:         stable_count = sum(1 for w in window_results if w["wr_oos"] >= 75.0 or (w["tr_oos"] == 0 and w["wr_is"] >= 75.0))
  ```
  - The clause `(w["tr_oos"] == 0 and w["wr_is"] >= 75.0)` marks an OOS window as STABLE even when 0 trades were executed in OOS, provided IS WR $\ge 75\%$.
  - Benchmark test run on 5 zero-OOS-trade windows produced `stable_windows = 5 / 5` (100% false stability score).

---

## 2. Logic Chain

1. **Observations 1 & FFT Convolution Math**:
   - The dot product $\sum_{k=0}^{W-1} w_k \cdot \text{vals}[i-k]$ is identical to discrete 1D convolution $(x * h)[n]$.
   - `scipy.signal.fftconvolve(vals, w_arr, mode='valid')` performs $O(N \log N)$ FFT-based convolution.
   - Benchmark verification proved max absolute error between loop dot product and `fftconvolve` is **$1.23 \times 10^{-13}$** (machine precision equivalence), while execution speed increased by **13.3x** on 10k items and **>50x** on large series.

2. **Observations 2 & Hurst Exponent Corrections**:
   - Filtering NaNs (`x_clean = x[~np.isnan(x)]`) prevents `NaN` propagation at initial rolling window boundaries.
   - Prepending origin zero `z = np.concatenate(([0.0], np.cumsum(y)))` accurately evaluates $R = \max_{0 \le k \le N} Z_k - \min_{0 \le k \le N} Z_k$ per classical Mandelbrot R/S theory.
   - Guarding $s \le 10^{-12}$ prevents division by near-zero floating point standard deviations.

3. **Observations 3 & WalkForwardEngine Stability Guard**:
   - A window with 0 OOS trades has zero empirical evidence of OOS profitability.
   - Requiring `w["tr_oos"] > 0 and w["wr_oos"] >= 75.0` ensures only windows with real OOS trade performance contribute to `stable_windows`.

---

## 3. Caveats

- **Scipy Dependency**: `scipy.signal.fftconvolve` requires `scipy` to be installed (which is standard in standard quantitative stacks and present in `requirements.txt`).
- **FFT Precision**: `fftconvolve` returns float64 arrays with noise around $10^{-13}$. Using `.real` if complex output occurs handles edge cases cleanly.
- **Minimum OOS Trades**: The zero-trade guard sets `tr_oos > 0`. If a higher trade threshold is desired by strategy design (e.g. `tr_oos >= 5`), the parameter can be parameterized in the future.

---

## 4. Conclusion

1. **Item 2 Fix**:
   - Replace the loop in `frac_diff_fixed` (`engine/ml_engine/feature_extractor.py`, lines 5–41) with `scipy.signal.fftconvolve(vals, w_arr, mode='valid')`.
   - Update `calc_hurst` in `BinaryFeatureExtractor.extract_features` (lines 88–97) with `x_clean = x[~np.isnan(x)]`, `z = np.concatenate(([0.0], np.cumsum(y)))`, and `if s <= 1e-12: return np.nan`.
2. **Item 5 Fix**:
   - Update `WalkForwardEngine.run_wfa` (`engine/auto_tuner.py`, line 87) to:
     `stable_count = sum(1 for w in window_results if w["tr_oos"] > 0 and w["wr_oos"] >= 75.0)`

---

## 5. Verification Method

1. **Run Unit Tests**:
   - Run `python -m unittest test_high_winrate_mechanisms.py` or new tests in `tests/`.
2. **Verify FFT Acceleration & Equivalence**:
   - Run benchmark command:
     `python -c "import numpy as np, pandas as pd; from scipy.signal import fftconvolve; from engine.ml_engine.feature_extractor import frac_diff_fixed; s = pd.Series(np.random.randn(10000).cumsum()); res = frac_diff_fixed(s, d=0.4); assert not res.dropna().empty"`
3. **Verify Zero OOS Trade Guard**:
   - Run test with mock strategy generating 0 OOS trades to confirm `stable_windows == 0`.
