# Master Plan — Quantitative Engine Optimization & Bug Fixes

## Objectives
1. Perform Step 0 Survey via 3 parallel Explorers to inspect codebase structure, test suite (`test_high_winrate_mechanisms.py`), quantitative components (`BinarySimulator`, `BinaryFeatureExtractor`, `RegimeDetector`/`CUSUMMonitor`, `MetaLabeler`, `engine/`, `strategies/`), and optimization pipelines.
2. Formulate global project specification in `PROJECT.md` at root, decomposing scope into implementation milestones and parallel E2E testing track.
3. Execute implementation milestones via subagent iteration loops (Explorer -> Worker -> Reviewer -> Challenger -> Forensic Auditor -> Gate).
4. Build and execute comprehensive E2E testing track (Tiers 1-4, published in `TEST_READY.md`).
5. Execute Final Milestone: 100% E2E test pass (Phase 1) and Adversarial Coverage Hardening (Phase 2).
6. Verify and document reproducible backtest performance (>65% Win Rate, positive OOS EV).

## Step Breakdown
- Step 0: Survey codebase with 3 parallel Explorers (`explorer_1`, `explorer_2`, `explorer_3`).
- Step 1: Synthesize survey findings into `PROJECT.md` (Feature Inventory, Architecture, Code Layout, Milestones, Interface Contracts).
- Step 2: Dispatch implementation track milestones and parallel E2E testing track orchestrator/writer.
- Step 3: Run iteration loops and gate checks for each milestone.
- Step 4: Final verification and report synthesis to Sentinel.
