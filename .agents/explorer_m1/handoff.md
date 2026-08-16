# Handoff Report: Milestone 1 — Visual Design System & Global Stylesheet Refactor Plan

**Agent:** Explorer M1  
**Target Milestone:** Milestone 1 (M1) — Visual Design System & Global Stylesheet Refactor  
**Deliverable:** `c:\Users\juanc\Desktop\prueba\.agents\explorer_m1\m1_plan.md`  
**Date:** 2026-08-16  

---

## 1. Observation

Direct observations from codebase inspection:

1. **Existing CSS Architecture (`static/css/style.css:1-14`)**:
   ```css
   :root {
       --bg-dark: #090d16;
       --bg-panel: #111827;
       --border-color: rgba(255, 255, 255, 0.08);
       --border-glow: rgba(56, 189, 248, 0.2);
       --accent-blue: #38bdf8;
       --accent-green: #00f5a0;
       --accent-red: #ff4d4d;
       --accent-purple: #8b5cf6;
       --accent-gold: #fbbf24;
       --text-primary: #f8fafc;
       --text-secondary: #94a3b8;
       --font-family: 'Inter', system-ui, -apple-system, sans-serif;
   }
   ```
   *Finding*: The current stylesheet uses highly saturated neon colors (`--accent-green: #00f5a0`, `--accent-red: #ff4d4d`), lacking calibration against chromostereopsis, and does not define the full 8-point grid spacing hierarchy, motion tokens, or dedicated monospace font variables for quantitative tables.

2. **Master Design System Specifications (`documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md:§4.1, §4.3, §5.1`) & `survey_spec_report.md:25-59`**:
   - Surface Layer Architecture: Canvas `#080b11`, Card Base `#0e1420`, Elevated Nav `#141d2e`, Hover `#1c273d`.
   - Subtle borders: `rgba(255, 255, 255, 0.07)`, active borders: `rgba(56, 189, 248, 0.35)`.
   - Typography tokens: `--text-primary: #f0f6fc`, `--text-secondary: #94a3b8`, `--text-muted: #64748b`, `--text-disabled: #475569`.
   - Semantic accents: `--accent-primary: #38bdf8`, `--accent-green: #10b981`, `--accent-red: #f43f5e`, `--accent-purple: #a855f7`, `--accent-amber: #f59e0b`.
   - Spacing tokens: `--space-1: 4px` to `--space-8: 32px`.
   - Motion tokens: `--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1)`, `--duration-micro: 120ms`, `--duration-state: 180ms`.
   - Inviolable tabular numerals: `font-family: 'JetBrains Mono', monospace; font-feature-settings: "tnum" 1, "zero" 1; font-variant-numeric: tabular-nums;`.

3. **DOM & JS Dynamic Selectors (`templates/index.html` & `static/js/app.js`)**:
   - `index.html` contains 89 distinct DOM IDs and structured components: `.glass-card`, `.form-control`, `.btn-primary`, `.btn-secondary`, `.mode-switch-container`, `.mode-btn`, `.tabs-nav`, `.tab-btn`, `.smart-grid`, `.smart-sidebar`, `.smart-universe-wrapper`, `.smart-universe-select`, `.smart-numeric-inputs`, `.smart-console-wrapper`, `.console-header`, `.smart-progress-bar-fill`, `.console-body`, `.top-strategies-wrapper`, `.smart-row-top`, `.smart-rec-grid`, `.smart-rec-item`, `.streak-ladder`, `.ladder-step`, `.smart-row-correlation`, `.markov-table`, `.trades-table`, `.n-table`, `.stats-cards`, `.stat-card`, `.cond-probs-grid`, `.subtabs-nav`, `.subtab-btn`, `.backtest-item`, `.live-badge-span`, `.pulse-dot`, `.tooltip`.
   - `app.js` dynamically generates and toggles classes: `.top-strat-pill` (lines 2426-2434), `.ladder-step.completed` (lines 1325, 2262), `.console-log-line.info/.success/.error/.warning` (line 2009), `.asset-wr-badge` (line 2101), `.text-green` / `.text-red` (lines 1063, 1086).

---

## 2. Logic Chain

1. **Step 1 (Token Unification)**: Based on Observation 1 and Observation 2, replacing the legacy `:root` variables with the calibrated FinTech Slate & Obsidian design tokens eliminates retinal halation and optical chromostereopsis while establishing standard 8-point grid metrics and cubic-bezier motion curves.
2. **Step 2 (Backward Compatibility Aliases)**: In Observation 1, legacy code references `--bg-dark`, `--bg-panel`, `--border-color`, `--border-glow`, and `--accent-blue`. By aliasing these legacy tokens to the new variables (`--bg-dark: var(--bg-canvas)`, `--border-color: var(--border-subtle)`), any unrefactored references will automatically resolve to the correct institutional colors with zero visual breakage.
3. **Step 3 (Tabular Alignment Engine)**: In Observation 2 and Observation 3, quantitative matrices (`.markov-table`, `.trades-table`, `.n-table`, `.stat-card p`, `.ladder-step-amount`) require vertical digit alignment. Applying `font-family: var(--font-mono)` with `tabular-nums` across all tabular selectors guarantees zero horizontal jumping during data streaming.
4. **Step 4 (Component Coverage & Selector Mapping)**: By cataloging every static selector from `index.html` and dynamic selector from `app.js` (Observation 3), the modular structure designed in `m1_plan.md` ensures 100% selector coverage without missing classes or breaking UI state changes.

---

## 3. Caveats

- **HTML Font Loading**: The Google Fonts `<link>` in `templates/index.html` currently imports `Inter` (weights 300-700) but does not yet explicitly include `JetBrains Mono`. While CSS will specify fallback `monospace`, Milestone 2 (Header & HTML update) should ensure the Google Fonts tag imports both `Inter` and `JetBrains Mono` for maximum rendering fidelity.
- **Chart.js & Lightweight Charts Theme Synchronization**: Chart rendering styling is defined within `static/js/charts.js`. The CSS changes in M1 provide the canvas background containers and DOM overlays; chart line/candle colors will be fully harmonized in Milestone 4.

---

## 4. Conclusion

A comprehensive, granular, and zero-regression implementation plan for `static/css/style.css` has been produced and saved to:
`c:\Users\juanc\Desktop\prueba\.agents\explorer_m1\m1_plan.md`

The plan provides:
- Complete `:root` tokens (surfaces, borders, typography, calibrated semantic accents, 8-pt spacing, motion).
- Global reset with tabular numerals configuration.
- Full specifications for all 14 CSS component modules.
- Preserved selector mappings for all DOM elements in `index.html` and `app.js`.

The builder agent can immediately execute this plan to rewrite `static/css/style.css`.

---

## 5. Verification Method

1. **File Inspection**:
   - Inspect `c:\Users\juanc\Desktop\prueba\.agents\explorer_m1\m1_plan.md` to review the full 14-section CSS specification.
2. **Selector Coverage Check**:
   - Verify that all classes listed in `m1_plan.md` match the elements discovered in `templates/index.html` and `static/js/app.js`.
3. **Backend Test Suite Execution**:
   - Run `pytest` to ensure test suite integrity:
     ```powershell
     pytest -v
     ```
