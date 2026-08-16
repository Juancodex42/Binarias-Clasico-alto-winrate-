## Dispatch for Sub-Orchestrator M1

- Working Directory: `c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1`
- Parent Conversation ID: `2926901b-d6f0-4d09-8db0-0f653bf61856`
- Scope Document: `c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/SCOPE.md`
- Master Project Document: `c:/Users/juanc/Desktop/prueba/PROJECT.md`
- User Request: `c:/Users/juanc/Desktop/prueba/.agents/ORIGINAL_REQUEST.md`

## Task Description
You are the Sub-Orchestrator for Milestone M1 (Engine Bug Remediation & Core Fixes).
Your mission is to execute the iteration loop (Explorers -> Worker -> Reviewers -> Challengers -> Forensic Auditor -> Gate) to implement and verify all 6 features assigned to M1:
1. `BinarySimulator` tie rule consistency (`run_multi_asset`).
2. Multi-asset Barbell bullet state tracking bug fix (prevent PnL wipeout on `pending_reset`).
3. Vectorize `frac_diff_fixed` using `scipy.signal.fftconvolve`.
4. HMM standard deviation leakage fix & CUSUM pause deadlock resolution.
5. MetaLabeler timestamp unit parsing fix & rolling median.
6. `WalkForwardEngine` zero OOS trade stability metric fix.

Refer to `c:/Users/juanc/Desktop/prueba/.agents/explorer_survey_1/handoff.md` for exact line numbers, code snippets, and evidence chains.

Initialize `BRIEFING.md` and `progress.md` in `c:/Users/juanc/Desktop/prueba/.agents/sub_orch_m1/`.
Dispatch Explorer -> Worker -> Reviewer -> Challenger -> Auditor iteration loop.
When all gate checks pass cleanly (Audit = CLEAN, Reviewers = APPROVE, Tests pass), mark milestone M1 complete and send a completion report to the parent orchestrator.
