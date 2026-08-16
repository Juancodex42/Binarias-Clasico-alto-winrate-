# Execution Plan — Milestone M1: Engine Bug Remediation & Core Fixes

## Working Directory
`c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1`

## Milestones & Tasks Overview
Milestone M1 covers 6 core engine bug remediation items:
1. `BinarySimulator` tie rule consistency (`tie_rule` in `run_multi_asset`).
2. Multi-asset Barbell bullet state tracking bug fix (prevent PnL wipeout on `pending_reset`).
3. Vectorize `frac_diff_fixed` in `BinaryFeatureExtractor` using `scipy.signal.fftconvolve`.
4. HMM standard deviation leakage fix in `RegimeDetector` & CUSUM pause deadlock resolution in `CUSUMMonitor`.
5. MetaLabeler millisecond timestamp parsing fix & rolling NATR median in `BinaryMLMetaFilter`.
6. `WalkForwardEngine` zero OOS trade stability metric fix.

## Iteration Plan
1. **Initialize State**: Write `plan.md`, update `progress.md`, `BRIEFING.md`. Set up heartbeat cron.
2. **Review Existing Work**:
   - Explorers (1, 2, 3): Completed mapping of code flaws.
   - Worker (1): Completed implementation and verified tests pass.
   - Reviewers (1, 2): Completed code review and both issued `APPROVE` verdicts.
3. **Dispatch Challengers & Auditor**:
   - Dispatch `challenger_1` & `challenger_2` (`teamwork_preview_challenger`) for empirical stress testing and boundary validation.
   - Dispatch `auditor_1` (`teamwork_preview_auditor`) for forensic integrity verification (checking zero cheating, no hardcoded results, no static mock returns).
4. **Gate Evaluation**:
   - Verify all Reviewers APPROVE (Done: 2/2 APPROVE).
   - Verify all Challengers confirm empirical correctness.
   - Verify Forensic Auditor is CLEAN.
   - Verify unit tests (`pytest tests/` and `pytest test_high_winrate_mechanisms.py`) pass.
   - Record in `GATE_STATUS.md`.
5. **Finalize Milestone**:
   - Update `SCOPE.md` status to DONE.
   - Update master `PROJECT.md` Milestone 1 status to DONE.
   - Write `handoff.md` and report completion to parent orchestrator via `send_message`.
