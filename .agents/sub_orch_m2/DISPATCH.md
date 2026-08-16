## 2026-08-12T17:41:26Z

You are the Sub-Orchestrator for Milestone M2 (Temporal Causality & Zero Leakage Enforcement).
Your working directory is: `c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m2`
Your scope document is: `c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m2/SCOPE.md`
The master project specification is: `c:/Users/juanc/Desktop/prueba/PROJECT.md`
The original user request is at: `c:/Users/juanc/Desktop/prueba/.agents/ORIGINAL_REQUEST.md`

Objective: Execute the full iteration loop (Explorers -> Worker -> Reviewers -> Challengers -> Forensic Auditor -> Gate) to implement and verify all 5 features in Milestone M2:
1. Align `create_labels` target shift logic with `BinarySimulator` 1-candle expiry in `optimizer_grid_search.py`.
2. Eliminate global quantile clipping in `strategies/volatility_squeeze_ml.py` and global ATR medians in `engine/auto_tuner.py`.
3. Replace Viterbi `predict()` sequence decoding in `engine/ml_engine/regime_detector.py` with forward-only state probabilities.
4. Integrate `PurgedGroupTimeSeriesSplit` into all optimization routines.
5. Isolate multi-asset capital state tracking between IS and OOS periods in `engine/optimizer.py`.

Instructions:
1. Initialize your `BRIEFING.md`, `plan.md`, and `progress.md` in `c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m2/`.
2. Refer to `c:/Users/juanc/Desktop/prueba/.agents/explorer_survey_1/handoff.md` and `c:/Users/juanc/Desktop/prueba/.agents/explorer_survey_3/handoff.md` for exact line numbers, code snippets, and evidence chains.
3. Dispatch Explorers -> Worker -> Reviewers -> Challengers -> Forensic Auditor. Include the mandatory zero-cheating warning in all Worker prompts.
4. Enforce strict gate checks: Auditor MUST be CLEAN, Reviewers MUST APPROVE, builds/tests MUST pass (`pytest tests/` and `pytest test_high_winrate_mechanisms.py`).
5. Update `GATE_STATUS.md` and `PROJECT.md` status when M2 completes.
6. Send a completion message to the parent orchestrator (`2926901b-d6f0-4d09-8db0-0f653bf61856` / `f189c50a-7635-437f-91e9-1631d1d31b62`).
