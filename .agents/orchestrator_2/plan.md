# Execution Plan — Project Orchestrator (Generation 2)

## Strategic Objective
Drive the binary options quantitative strategy simulator and optimization engine to full completion, achieving empirical reproducible Out-Of-Sample (OOS) Win Rate > 65%, positive Expected Value (EV > 0.0), zero temporal causality leakage, and passing 100% of unit/integration/E2E test suites.

## Workflow & Milestone Roadmap

### Step 1: Milestone 1 Verification & Gate Completion (M1)
- Verify `sub_orch_m1` gate state. Review Reviewer verdicts (`APPROVE`) and ensure Forensic Auditor verdict is `CLEAN`.
- If auditor handoff is missing in `sub_orch_m1`, dispatch a `teamwork_preview_auditor` for M1.
- Mark M1 as `DONE` in `PROJECT.md`.

### Step 2: E2E Testing Track Completion & `TEST_READY.md`
- Inspect Tier 1-4 tests in `tests/`.
- Verify Tier 1 (50 tests), Tier 2 (55 tests), Tier 3 (20 tests), Tier 4 (10 tests) coverage in `tests/`.
- Dispatch Worker/Reviewer to generate `TEST_READY.md` summarizing the test suite.

### Step 3: Milestone 2 — Temporal Causality & Zero Leakage Enforcement (M2)
- Decompose/Dispatch M2 scope:
  - Feature 7: Target expiry label alignment (`create_labels` 1-candle expiry shift)
  - Feature 8: Feature scaling & quantile leakage elimination (in-sample only scaling)
  - Feature 9: HMM forward-only probability state estimation (replace Viterbi sequence decoding)
  - Feature 10: Purged CV integration (`PurgedGroupTimeSeriesSplit` + embargo in tuning routines)
  - Feature 11: Capital state split isolation (IS vs OOS independent tracking)
- Iteration Loop: Explorer -> Worker -> Reviewers -> Challengers -> Forensic Auditor.
- Gate evaluation & update `PROJECT.md` M2 to `DONE`.

### Step 4: Milestone 3 — Optuna & Systematic Search Space Exploration (M3)
- Decompose/Dispatch M3 scope:
  - Feature 12: Optuna framework integration (TPE sampler, Bayesian opt, trial pruning)
  - Feature 13: Multi-dimensional search space design (timeframes, expirations 1-12, indicators, filters)
  - Feature 14: True Walk-Forward Optimization Engine (rolling IS tuning & OOS evaluation)
  - Feature 15: Backtest Engine parallel vectorization for fast tuning throughput
- Iteration Loop: Explorer -> Worker -> Reviewers -> Challengers -> Forensic Auditor.
- Execute hyperparameter exploration to discover configurations with OOS Win Rate > 65% & EV > 0.0.
- Gate evaluation & update `PROJECT.md` M3 to `DONE`.

### Step 5: Milestone 4 — Test Suite Expansion & Reproducible Backtest Verification (M4)
- Decompose/Dispatch M4 scope:
  - Feature 16: Formal `tests/` directory & `pytest.ini` clean harness (0 errors/warnings)
  - Feature 17: Integrity & Causality test suite expansion (`test_causality_zero_cheating.py`, `test_high_winrate_mechanisms.py`)
  - Feature 18: Executable `verify_high_winrate_oos.py` script proving empirical OOS Win Rate > 65% & EV > 0.0 across asset universe.
- Phase 1: Verify 100% pass on all test tiers (Tiers 1-4).
- Phase 2: Adversarial coverage hardening (Tier 5 - white-box gap analysis).
- Gate evaluation & update `PROJECT.md` M4 to `DONE`.

### Step 6: Final Victory Report & Handoff to Sentinel
- Aggregate all audit attestations, test logs, and empirical verification summaries.
- Send final report to parent (Sentinel).
