## 2026-08-16T19:26:48Z
You are the Explorer for Milestone 1 (Visual Design System & Global Stylesheet Refactor) of the Binary Options Quantitative Terminal UI/UX Redesign project.
Your working directory is: c:\Users\juanc\Desktop\prueba\.agents\explorer_m1\

You MUST read:
1. c:\Users\juanc\Desktop\prueba\ORIGINAL_REQUEST.md
2. c:\Users\juanc\Desktop\prueba\PROJECT.md
3. c:\Users\juanc\Desktop\prueba\.agents\survey_spec_miner\survey_spec_report.md
4. c:\Users\juanc\Desktop\prueba\static\css\style.css
5. c:\Users\juanc\Desktop\prueba\templates\index.html

Your objective is to produce a concrete, granular implementation plan for rewriting `static/css/style.css` to implement the Institutional Dark Design System according to the master guide specifications.
The implementation plan must detail:
1. CSS Variables / Tokens in `:root`:
   - Canvas background (`#080b11`), card base (`#0e1420`), elevated nav (`#141d2e`), hover surface (`#1c273d`).
   - Borders (`rgba(255,255,255,0.07)` subtle, `rgba(56,189,248,0.35)` active/focus).
   - Typography scale & colors (`--text-primary: #f0f6fc`, `--text-secondary: #94a3b8`, `--text-muted: #64748b`, `--text-disabled: #475569`).
   - Semantic accents (`--accent-primary: #38bdf8`, `--accent-green: #10b981`, `--accent-red: #f43f5e`, `--accent-purple: #a855f7`, `--accent-amber: #f59e0b`).
   - Spacing tokens (`--space-1: 4px` to `--space-8: 32px`).
   - Motion tokens (`--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1)`, `--duration-micro: 120ms`, `--duration-state: 180ms`).
2. Global reset, body styling, and font configuration (`Inter` + `JetBrains Mono` with `tabular-nums`).
3. Component classes: `.glass-card`, `.form-control`, `.btn-primary`, `.btn-secondary`, `.badge`, `.status-pill`, `.pulse-dot`, `.console-body`, `.smart-progress-bar-fill`, `.n-table`, `.markov-table`, `.trades-table`, `.top-strat-pill`, `.ladder-item`, and modal overlays.
4. Retention of all existing selector names used in `index.html` and `app.js` so that zero styling regressions occur.

Write your plan to `c:\Users\juanc\Desktop\prueba\.agents\explorer_m1\m1_plan.md` and write `handoff.md`.
Send a completion message to the parent when done.
