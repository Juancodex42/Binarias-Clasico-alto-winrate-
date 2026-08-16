# Handoff Report — Explorer 1: Milestone 3 (Optuna Framework Integration & Search Space Design)

## 1. Observation

### 1.1 Python Environment & Optuna Dependency
Execution of `python -c "import optuna; print(optuna.__version__)"` confirmed:
- Optuna **version 4.9.0** is already installed in the execution environment.

### 1.2 Existing Optimization Architecture
1. **`optimizer_grid_search.py`**:
   - Lines 158–166: Evaluates static combinations via `ProcessPoolExecutor` grid search:
     ```python
     META_THRESHOLDS = [0.52, 0.55, 0.60, 0.65]
     REGIME_CONFIGS = [('none', None), ('hmm_48', 0.48), ('hmm_50', 0.50)]
     EXPIRY_CANDLES = [1, 2]
     ```
   - Lacks Bayesian optimization, parameter importance ranking, and trial pruning.

2. **`engine/optimizer.py` (`CapitalOptimizer`)**:
   - Focuses primarily on Kelly criterion, streak sizing (`find_optimal_n`, `calculate_streak_plan`), and Monte Carlo simulations (`monte_carlo`, `monte_carlo_discrete`, `monte_carlo_campaign`).
   - Lines 499–620 (`optimize_daily_confluence_stream`): Performs brute-force iteration over 45 candidate parameter combinations without dynamic pruning.

3. **`engine/ml_engine/purged_cv.py` (`PurgedGroupTimeSeriesSplit`)**:
   - Lines 9–42: Provides purged cross-validation with embargo offset:
     ```python
     class PurgedGroupTimeSeriesSplit:
         def __init__(self, n_splits: int = 5, expiry_candles: int = 1, embargo_pct: float = 0.01):
     ```
   - Prevents data leakage between trade expiration windows across CV splits.

4. **Strategy Interfaces (`strategies/`)**:
   - Base class `BaseStrategy` (`strategies/base.py`) defines `get_params_schema()`, `prepare_data(df)`, and `generate_signals(df, params, precomputed)`.
   - Strategies (`volatility_squeeze_ml.py`, `bollinger_bounce.py`, `rsi_extremes.py`, `daily_confluence.py`) accept standard parameter dictionaries and produce entry signals (`CALL`/`PUT`).

---

## 2. Logic Chain

1. **Need for Optuna Integration (Feature 12)**:
   - *Observation*: Existing grid search (`optimizer_grid_search.py`) is restricted to coarse grids and fails to efficiently explore high-dimensional continuous search spaces (e.g. RSI thresholds, BB standard deviations, NATR periods, ML probability thresholds).
   - *Deduction*: Integrating Optuna's Tree-structured Parzen Estimator (`TPESampler`) enables Bayesian optimization, concentrating trial evaluation in promising regions of the hyperparameter space.
   - *Deduction*: Integrating Optuna's `MedianPruner` combined with `PurgedGroupTimeSeriesSplit` allows trials that underperform on early cross-validation folds (e.g. Win Rate < breakeven 54.05%) to be pruned early, saving CPU time for broader exploration.

2. **Multi-Dimensional Search Space Design (Feature 13)**:
   - *Observation*: Binary option strategies are sensitive to timeframe, expiration duration, market session, indicator periods, and probabilistic ML filtering thresholds.
   - *Deduction*: A 5-dimensional search space schema must be defined:
     1. **Dimension 1 (Timeframes)**: 1m, 5m, 15m, 30m, 1h, 4h, 1d datasets.
     2. **Dimension 2 (Expirations)**: 1 to 12 candles.
     3. **Dimension 3 (Session & Days)**: ALL (24h), ASIAN (0-8 UTC), LONDON (8-16 UTC), NEW_YORK (13-21 UTC), OVERLAP_LDN_NY (13-16 UTC), Weekday vs Weekend.
     4. **Dimension 4 (Indicator Periods)**: RSI (2–30, oversold 15–35, overbought 65–85), BB (10–50, std 1.5–3.5, wick ratio 0.1–0.6, vol_mult 0.5–2.5), NATR (7–28), EMA fast/slow (5–100).
     5. **Dimension 5 (Probability Thresholds)**: `MetaLabeler` threshold (0.50–0.90), `RegimeDetector` breakeven (0.45–0.60).

3. **Targeting Out-Of-Sample (OOS) Win Rate > 65% & EV > 0.0**:
   - *Observation*: For a typical binary payout of $r = 0.85$, the breakeven win rate is $p_{\text{be}} = \frac{1}{1 + 0.85} \approx 54.05\%$.
   - *Deduction*: Optimization objective functions must penalize any configuration with $WR_{\text{oos}} \le 54.05\%$ or trade count $N_{\text{oos}} < 30$.
   - *Deduction*: Evaluating the 95% Wilson score confidence interval lower bound ensures statistical confidence that true underlying win rate exceeds breakeven ($WR_{\text{wilson\_low}} > 54.05\%$).

---

## 3. Caveats

1. **Computational Overhead of ML Meta-Filters in Optuna Loops**:
   - Fitting `HistGradientBoostingClassifier` or `MetaLabeler` inside every Optuna trial fold increases per-trial execution time. Precomputing strategy features (`prepare_data()`) outside trial loops is essential to maintain high search throughput.
2. **Dataset Granularity & Expiry Alignment**:
   - Expiration candles (1–12) depend on timeframe. For instance, a 12-candle expiry on a 4h chart represents 48 hours, whereas on a 5m chart it represents 1 hour.
3. **Execution Environment Dependencies**:
   - Optuna 4.9.0 is verified installed. No additional `pip install` steps are needed for core Optuna functionality.

---

## 4. Conclusion

1. **Feature 12 Design Blueprint**:
   - Created `proposed_optimizer_optuna.py` in the agent working directory (`.agents/teamwork_preview_explorer_m3_1/proposed_optimizer_optuna.py`).
   - Implements `OptunaOptimizer` using `TPESampler(multivariate=True, group=True)` and `MedianPruner(n_startup_trials=10, n_warmup_steps=1)`.
   - Integrates `PurgedGroupTimeSeriesSplit` for leakage-free cross-validation.
   - Computes parameter importances (`optuna.importance.get_param_importances`) and outputs full trial dataframes.

2. **Feature 13 Design Blueprint**:
   - Created `proposed_search_space.py` in the agent working directory (`.agents/teamwork_preview_explorer_m3_1/proposed_search_space.py`).
   - Structures 5 search space dimensions and defines target acceptance criteria (OOS Win Rate > 65.0%, Expected Value > 0.0, minimum 30 OOS trades, Wilson 95% CI lower bound > 54.05%).

---

## 5. Verification Method

### 5.1 Verification Commands
To verify the Optuna integration blueprints, run:
```bash
python -c "import sys; sys.path.insert(0, '.agents/teamwork_preview_explorer_m3_1'); sys.path.insert(0, '.'); from proposed_optimizer_optuna import OptunaOptimizer; from strategies.volatility_squeeze_ml import VolatilitySqueezeMLStrategy; import pandas as pd; df = pd.read_csv('data/raw/BTCUSDT_30m.csv').tail(1000).reset_index(drop=True); opt = OptunaOptimizer(); res = opt.optimize(df, VolatilitySqueezeMLStrategy, 'volatility_squeeze_ml', n_trials=5, timeout=30); print('Optuna trials completed:', res['completed_trials']); print('Best params:', res['best_params'])"
```

### 5.2 Files to Inspect
- `.agents/teamwork_preview_explorer_m3_1/proposed_optimizer_optuna.py`
- `.agents/teamwork_preview_explorer_m3_1/proposed_search_space.py`
- `engine/ml_engine/purged_cv.py`
- `optimizer_grid_search.py`

### 5.3 Invalidation Conditions
- Optuna study fails to prune unpromising trials where IS Win Rate < 54.05%.
- Data leakage occurs across IS and OOS splits in trial evaluations.
- Search space parameters fail to yield candidates with OOS Win Rate > 65.0% and positive Expected Value.
