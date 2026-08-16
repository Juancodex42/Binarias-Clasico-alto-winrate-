## 2026-08-12T17:53:57Z
You are Worker 1 for Milestone M2 (Temporal Causality & Zero Leakage Enforcement).
Your working directory is: `c:/Users/juanc/Desktop/prueba/.agents/worker_m2_1`

Paths to read before starting:
- `c:/Users/juanc/Desktop/prueba/.agents/ORIGINAL_REQUEST.md`
- `c:/Users/juanc/Desktop/prueba/PROJECT.md`
- `c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m2/SCOPE.md`
- `c:/Users/juanc/Desktop/prueba/.agents/explorer_m2_1/handoff.md`
- `c:/Users/juanc/Desktop/prueba/.agents/explorer_m2_1/analysis.md`
- `c:/Users/juanc/Desktop/prueba/.agents/explorer_m2_2/handoff.md`
- `c:/Users/juanc/Desktop/prueba/.agents/explorer_m2_2/analysis.md`
- `c:/Users/juanc/Desktop/prueba/.agents/explorer_m2_3/handoff.md`
- `c:/Users/juanc/Desktop/prueba/.agents/explorer_m2_3/analysis.md`

Your Task:
Implement and verify all 5 features of Milestone M2 per the detailed proposals from Explorers 1, 2, and 3:

1. **Feature 1 (Target Expiry Alignment)**:
   - In `optimizer_grid_search.py` and `strategies/volatility_squeeze_ml.py`, align `create_labels` target shift logic with `BinarySimulator` 1-candle expiry (entry candle close to exit candle close). Ensure multi-candle expiration is parameterized correctly (`locs_valid + expiry_candles`).

2. **Feature 2 (Zero-Leakage Feature Scaling & ATR Medians)**:
   - In `strategies/volatility_squeeze_ml.py` (`prepare_data`), convert global `.quantile(0.01)` and `.quantile(0.99)` clipping to rolling window quantiles (`rolling(200, min_periods=20)`).
   - In `engine/auto_tuner.py` (`DynamicRegimeAdapter.detect_regime`), convert global `atr_14.median()` to rolling median (`atr_14.rolling(100, min_periods=1).median()`).
   - In `strategies/genetic_composite.py` (line 181) and `engine/exporter.py` (line 421), replace `.fillna(bb_width.quantile(0.30))` with expanding quantile `.fillna(bb_width.expanding(min_periods=1).quantile(0.30))`.

3. **Feature 3 (Forward-Only HMM & Covariance Regularization)**:
   - In `engine/ml_engine/regime_detector.py`:
     - Replace Viterbi `self.model.predict(obs)` in `get_current_state` with forward-only log-alpha recursion probabilities (`predict_forward_proba` / `predict_forward`), preventing future observation leakage into historical state estimates.
     - Adjust HMM `min_covar=1e-6`.
     - Wrap `self.model.fit(obs)` in `try...except Exception:`, fall back to uniform state distribution or default regime on failure.
     - Enforce post-fit covariance floor `np.maximum(self.model.covars_, 1e-6)`.
     - Handle potential NaN/Inf in forward probability outputs.

4. **Feature 4 (Purged CV Integration)**:
   - Ensure `PurgedGroupTimeSeriesSplit` is integrated across all optimization routines, replacing any naive train/test split in `engine/auto_tuner.py` (`ParameterSurfaceAnalyzer.analyze_surface`) and `app.py`.

5. **Feature 5 (IS/OOS Multi-Asset Capital State Isolation)**:
   - In `engine/optimizer.py` (`optimize_daily_confluence_stream`) and `app.py`, enforce strict capital state isolation between IS and OOS periods. `sim.run_multi_asset()` must run on `universe_is` and `universe_oos` independently with fresh capital initialization ($1000.0$) and isolated bullet/streak state.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Verification Requirements:
- Run full test suite using terminal execution:
  `pytest tests/`
  `pytest test_high_winrate_mechanisms.py`
- All tests must pass with 0 errors.
- Document executed commands, test results, diff summaries, and verification outcome in `c:/Users/juanc/Desktop/prueba/.agents/worker_m2_1/handoff.md`.
- Send a completion message back to parent orchestrator when done.
