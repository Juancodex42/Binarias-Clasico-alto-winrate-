# BRIEFING — 2026-08-12T20:00:15Z

## Mission
Adversarial empirical verification of backtest vectorization (`VectorizedBinarySimulator.run_fast` vs `BinarySimulator.run`) and statistical metric calculations (Wilson 95% CI lower bound) for Milestone 3 Gate.

## 🔒 My Identity
- Archetype: empirical_challenger
- Roles: critic, specialist
- Working directory: c:\Users\juanc\Desktop\prueba\.agents\challenger_m3_1
- Original parent: 57d122eb-bdbc-426c-972a-cbbeb44361b8
- Milestone: Milestone 3 Gate
- Instance: 1 of 1

## 🔒 Key Constraints
- Empirical verification mandatory — run code, do not rely on claims
- Write tests/harnesses in working directory `.agents\challenger_m3_1`
- Review-only — do NOT modify project implementation code
- Assert zero mismatches across 100,000 synthetic trade evaluations
- Check Wilson 95% CI lower bound mathematical correctness against closed-form statistical formulas
- Benchmark execution speedup

## Current Parent
- Conversation ID: 57d122eb-bdbc-426c-972a-cbbeb44361b8
- Updated: 2026-08-12T20:00:15Z

## Review Scope
- **Files to review**: `worker_m3` deliverables (simulators, metrics, backtest engine)
- **Interface contracts**: `PROJECT.md`
- **Review criteria**: Equivalence of `VectorizedBinarySimulator.run_fast` and `BinarySimulator.run`, Wilson CI precision, performance speedup.

## Key Decisions Made
- Will write synthetic stress test harnesses in python executing 100,000+ trade scenarios.
- Will compare scalar vs vectorized simulator trade-by-trade and overall metrics.
- Will verify Wilson 95% CI formula explicitly against mathematical reference values (z = 1.959963984540054).

## Artifact Index
- `DISPATCH.md` — Incoming task assignment
- `BRIEFING.md` — Working context and memory
