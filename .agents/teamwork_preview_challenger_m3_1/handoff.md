# Milestone 3 Empirical Stress Verification Handoff Report

**Agent Directory**: `c:\Users\juanc\Desktop\prueba\.agents\teamwork_preview_challenger_m3_1`  
**Completion Timestamp**: 2026-08-12T17:02:00Z  
**Verdict**: **FAIL**  

---

## 1. Observation

### 1.1 Mandatory Mandates Evaluated
1. **Vectorization Parity Stress Test (`VectorizedBinarySimulator.run_fast` vs `BinarySimulator.run`)**:
   - Executed `scratch/test_m3_vectorization_parity.py` across 960 synthetic edge-case DataFrames (gaps, zero volume, high volatility, consecutive loss ruin, exact price ties, sparse/dense/edge signals, tie rules `RETURN_STAKE` / `LOSS`, expiries 1–12, slippage 0.0–0.001).
   - **Observed Result**: **287 failures out of 960 test cases**.
   - **Specific Mismatches**:
     - `net_pnl`: scalar=`-1000.0` vs vec=`-1050.0` / `-1056.0`.
     - `max_drawdown`: scalar=`1.0` (100%) vs vec=`1.03788` (103.79%) / `1.03989`.
     - `total_trades`: scalar=`71` vs vec=`72`.
     - `losses`: scalar=`39` vs vec=`40`.
   - **Code Defect Location**: `engine/simulator.py` lines 77–84. `VectorizedBinarySimulator.run_fast` truncates `pnl_vector` at `ruin_idx[0] + 1`, but does NOT cap the final losing trade's bet size to remaining account capital (which scalar `BinarySimulator.run` does on line 217). As a result, the vectorized simulator allows bet sizes > remaining equity, resulting in negative equity (e.g. -$50), net PnL below -$1000, and max drawdowns exceeding 100%.

2. **TrueWalkForwardEngine Edge-Case Robustness**:
   - Executed `scratch/test_m3_wfa_edge_cases.py` across 5 stress scenarios: empty DataFrame, small DataFrame (< 300 rows), zero-signal datasets (flat price line), extreme parameters (`expiry=50`, `std_devs=10.0`), and micro-folds (`n_windows=20`).
   - **Observed Result**: **5 out of 5 edge-case tests PASSED**. The engine handles missing data, small folds, and zero signals gracefully without crashing, throwing zero-division errors, or exceeding array bounds.

3. **Independent Re-Evaluation of Discovered High-Winrate Configurations (`data/optuna_results.json`)**:
   - Executed `scratch/test_m3_validate_top_configs.py` re-evaluating all 5 passing configurations reported in `data/optuna_results.json` using `BinarySimulator.run` and `VectorizedBinarySimulator.run_fast` on full OOS splits.
   - **Observed Results per Configuration**:
     - `Config 1 [DOGEUSDT_4h SupportResistance]`: Claimed WR=90.91%, EV=+0.6818. **Re-evaluated: WR=70.37%, EV=+0.3019 (27 trades)** -> **PASS**.
     - `Config 2 [BNBUSDT_4h MeanReversion]`: Claimed WR=72.50%, EV=+0.3412. **Re-evaluated: WR=52.38%, EV=-0.0310 (63 trades)** -> **FAIL** (Win rate < 65% and EV is negative).
     - `Config 3 [LINKUSDT_4h ISLG_RS]`: Claimed WR=72.73%, EV=+0.3455. **Re-evaluated: WR=70.59%, EV=+0.3059 (17 trades)** -> **PASS**.
     - `Config 4 [LINKUSDT_4h SupportResistance]`: Claimed WR=66.67%, EV=+0.2333. **Re-evaluated: WR=57.14%, EV=+0.0571 (28 trades)** -> **FAIL** (Win rate < 65%).
     - `Config 5 [NASDAQ_1d DailyConfluence]`: Claimed WR=66.67%, EV=+0.2333. **Re-evaluated: 0 trades generated on OOS** -> **FAIL** (Parameters overconstrained: `rsi_min_put == rsi_max_put == 62.5`).

---

## 2. Logic Chain

1. **Vectorization Parity Failure**:
   - *Observation*: In `BinarySimulator.run` (line 217), when `current_equity < fixed_bet`, `bet_size` is capped to `current_equity`. On bankruptcy, equity reaches exactly 0.0, net PnL is -$1000.0, and drawdown is exactly 1.0 (100%).
   - *Observation*: In `VectorizedBinarySimulator.run_fast` (lines 72-84), `fixed_bet` is unconstrained. When ruin occurs on trade $k$, `pnl_vector[k-1]` subtracts the full $100 bet even if remaining equity was only $50.
   - *Deduction*: This causes negative equity, net PnL exceeding initial capital, drawdowns > 100%, and trade count discrepancies. Therefore, `VectorizedBinarySimulator.run_fast` fails strict parity with scalar `BinarySimulator.run`.

2. **Top Configuration Verification Failure**:
   - *Observation*: `data/optuna_results.json` reports 5 passing configurations with claimed OOS Win Rate > 65% and EV > 0.
   - *Observation*: Independent re-evaluation of Config 2 (`BNBUSDT_4h MeanReversion`) yields 52.38% Win Rate and -0.0310 EV.
   - *Observation*: Independent re-evaluation of Config 4 (`LINKUSDT_4h SupportResistance`) yields 57.14% Win Rate.
   - *Observation*: Independent re-evaluation of Config 5 (`NASDAQ_1d DailyConfluence`) yields 0 trades due to contradictory parameters (`rsi_min_put=62.5` and `rsi_max_put=62.5`).
   - *Deduction*: 3 out of the 5 claimed top configurations do NOT satisfy the acceptance criteria (OOS Win Rate > 65.0% and EV > 0.0) under independent verification.

---

## 3. Caveats

1. **Optuna Cross-Validation Split Differences**:
   - The discrepancies between claimed OOS win rates in `data/optuna_results.json` and static 60/40 OOS re-evaluations stem from how `OptunaStrategyOptimizer` sliced Purged CV folds vs single static temporal splits.
2. **Robustness of WFA Engine Code Structure**:
   - While `TrueWalkForwardEngine` edge-case handling is crash-proof, the hyperparameter exploration script produced configurations that did not generalize reliably across full OOS periods.

---

## 4. Conclusion

- **Verdict**: **FAIL**
- **Reasons**:
  1. `VectorizedBinarySimulator.run_fast` fails parity with `BinarySimulator.run` (287/960 failures) due to uncapped ruin bet sizing and negative equity calculation.
  2. 3 out of 5 top configurations in `data/optuna_results.json` fail independent OOS criteria (Win Rate < 65% or EV <= 0 or 0 trades).
- **Remediation Required**:
  - Update `VectorizedBinarySimulator.run_fast` to cap cumulative loss at initial capital upon account ruin so equity cannot go negative and drawdown cannot exceed 100%.
  - Re-run hyperparameter search with stricter multi-fold cross-validation constraints to ensure discovered passing configurations achieve genuine OOS Win Rate > 65.0% and EV > 0.0 on independent test splits.

---

## 5. Verification Method

### 5.1 Verification Commands
Run the empirical challenger verification suite:

```bash
# 1. Run Vectorization Parity Stress Test
python scratch/test_m3_vectorization_parity.py

# 2. Run TrueWalkForwardEngine Edge Case Test
python scratch/test_m3_wfa_edge_cases.py

# 3. Run Top Configurations Re-Evaluation
python scratch/test_m3_validate_top_configs.py
```

### 5.2 Files to Inspect
- `scratch/test_m3_vectorization_parity.py`: Verifies scalar vs vectorized simulator parity across 960 edge case DataFrames.
- `scratch/test_m3_wfa_edge_cases.py`: Verifies `WalkForwardEngine` edge case handling.
- `scratch/test_m3_validate_top_configs.py`: Re-evaluates top configurations from `data/optuna_results.json`.
- `engine/simulator.py`: Contains `VectorizedBinarySimulator.run_fast` ruin handling bug.
- `data/optuna_results.json`: Hyperparameter results JSON containing failing configurations.

### 5.3 Invalidation Conditions
- Any vectorization parity test failure.
- Any configuration in `data/optuna_results.json` failing OOS Win Rate > 65.0% or EV > 0.0 upon independent re-evaluation.
