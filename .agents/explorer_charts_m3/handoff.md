# Handoff Report: Milestone 3 Charting Engine & Visualizations Analysis
**Agent**: `explorer_charts_m3`  
**Working Directory**: `c:\Users\juanc\Desktop\prueba\.agents\explorer_charts_m3`  
**Handoff Type**: Hard (Task Complete)  
**Date**: 2026-08-16  

---

## 1. Observation

1. **Lightweight Charts Instantiation & Styling**:
   - `static/js/charts.js:11-72` defines `createCandlestickChart(containerId)`. It uses legacy GitHub Dark colors:
     - `textColor: '#8b949e'` (line 16)
     - `vertLines: { color: 'rgba(48, 54, 61, 0.3)' }`, `horzLines: { color: 'rgba(48, 54, 61, 0.3)' }` (lines 21-22)
     - `borderColor: '#30363d'` (lines 30, 38)
     - `upColor: '#00f5a0'`, `downColor: '#ff4d4d'` (lines 59-63)
   - `static/js/app.js:501-521` initializes two chart instances:
     - Advanced Mode: `createCandlestickChart('tv-chart')` with a ResizeObserver (lines 502-510).
     - Smart Mode: `createCandlestickChart('smart-tv-chart')` with a ResizeObserver (lines 513-521).
   - Signal markers are built in `static/js/app.js:415-470` (`buildChartMarkers`), which sets `CALL` to `#00f5a0`, `PUT` to `#ff4d4d`, and `EXIT` (WIN `#00f5a0`, LOSS `#ff4d4d`).
   - Price lines are created in `static/js/app.js:1104-1136` (`highlightTradeOnChart`) using dashed `#00f5a0`/`#ff4d4d` for entry and dotted `#00f5a0`/`#ff4d4d` for exit.

2. **Chart.js Instance Lifecycle & Configurations**:
   - `static/js/charts.js:3-9` sets global defaults with font family `'Inter'` and tooltip background `'rgba(22, 27, 34, 0.9)'` with border `'#30363d'`.
   - `static/js/charts.js:119-234` (`createEquityCurve`):
     - Keyed on `window[canvasId + 'Inst']` (line 125, 163).
     - Border color `#58a6ff`, background `'rgba(88, 166, 255, 0.12)'`.
     - Detects log scale if `(maxVal / Math.max(minVal, 0.01)) > 100 && minVal >= 1.0` (line 160).
     - Formats ticks with `formatYAxisTick()` (line 94).
   - `static/js/charts.js:290-375` (`createMonteCarloChart`):
     - **Bug**: Uses global `window.mcChartInst` (lines 292, 309) instead of `window[canvasId + 'Inst']`.
     - Percentile curves: P95/P75 (`rgba(63, 185, 80, ...)`), P50 (`#58a6ff`), P25/P5 (`rgba(248, 81, 73, ...)`).
   - `static/js/charts.js:262-288` (`createGrowthRateChart`):
     - Uses `window.gnChartInst` (lines 264, 268) instead of `window[canvasId + 'Inst']`.
     - Colors: `#3fb950` for optimal N, `#58a6ff` for non-optimal.
   - `static/js/charts.js:236-260` (`createBarChart`):
     - Uses `window[canvasId + 'Inst']` (lines 238, 240).
     - Used for `#autocorr-chart`, `#streaks-chart`, `#hourly-chart`, `#market-state-chart`, `#kelly-chart`.

3. **Canvas 2D Correlation Heatmap**:
   - `static/js/charts.js:377-470` (`createCorrelationHeatmap`):
     - Handles DPR scaling (`window.devicePixelRatio`).
     - Computes cell dimensions with fixed margins (`leftMargin: 70, topMargin: 15, rightMargin: 15, bottomMargin: 35`).
     - Uses color blend: positive values towards red `rgb(248, 81, 73)`, negative values towards blue `rgb(88, 166, 255)`.
     - Draws numeric values using `Inter, sans-serif`.

4. **Institutional Standard (`GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`) Requirements**:
   - Surface colors: Base `#0e1420`, Elevated `#141d2e`, Canvas `#080b11`, Borders `rgba(255, 255, 255, 0.07)` (§4.1).
   - Semantic accents: Electric Sky `#38bdf8`, Cyber Emerald `#10b981`, Rose Crimson `#f43f5e`, Quantum Amethyst `#a855f7`, Golden Amber `#f59e0b` (§4.3).
   - Ergonomics: Eliminate retinal halation and chromostereopsis from neon greens (`#00f5a0`) and neon reds (`#ff4d4d`) on dark backgrounds (§3.1).
   - Typography: Use `'JetBrains Mono'` with tabular figures for all data/numeric displays (§5.1).

---

## 2. Logic Chain

1. **Premise 1**: The current charting scripts (`static/js/charts.js` and `static/js/app.js`) utilize obsolete color constants (`#00f5a0`, `#ff4d4d`, `#58a6ff`, `#3fb950`, `#30363d`, `rgba(22, 27, 34, 0.9)`) inherited from standard GitHub dark themes.
2. **Premise 2**: These legacy color codes violate the institutional design system and induce visual fatigue (halation & chromostereopsis) per §3.1 and §4.3 of the Master Guide.
3. **Premise 3**: In `createMonteCarloChart` and `createGrowthRateChart`, saving chart instances to fixed global variables (`window.mcChartInst`, `window.gnChartInst`) instead of dynamic keyed properties (`window[canvasId + 'Inst']`) creates instance collisions when switching between Smart Mode (`#smart-mc-chart-canvas`) and Advanced Mode (`#mc-chart`).
4. **Premise 4**: Chart axes, tooltips, and canvas heatmap numeric overlays currently employ proportional fonts (`Inter`) rather than monospaced tabular numerals (`JetBrains Mono`), causing character jitter and column misalignment.
5. **Conclusion**: Updating `static/js/charts.js` and the corresponding marker/price-line helpers in `static/js/app.js` with institutional color tokens, vertical canvas gradients, monospaced tabular fonts, and robust keyed instance destruction will bring the charting layer into 100% compliance with Milestone 3 while resolving potential memory leaks and canvas collisions.

---

## 3. Caveats

- **No backend modification required**: All chart data contracts from Flask REST / SSE APIs (`/api/data/candles`, `/api/backtest-stream`, `/api/smart-optimize-v2-stream`, `/api/montecarlo`) remain 100% untouched.
- **Lightweight Charts version**: The project uses Lightweight Charts v4.0.0 standalone production build; configuration options must strictly follow v4 API specifications (e.g. `layout.background`, `applyOptions`, `setMarkers`, `createPriceLine`).
- **DOM IDs**: All 89 DOM IDs across `templates/index.html` are preserved, ensuring all chart canvases and containers bind properly without renaming.

---

## 4. Conclusion

The charting architecture is structurally sound but requires visual and architectural modernization:
1. **Palette Calibration**: Replace all legacy neon/GitHub hex codes with institutional tokens (`#10b981`, `#f43f5e`, `#38bdf8`, `#a855f7`, `#f59e0b`, `rgba(255, 255, 255, 0.04)`).
2. **Instance Management Fix**: Unify all Chart.js instances under `window[canvasId + 'Inst']`.
3. **Gradient & Typography Polish**: Introduce vertical linear fill gradients on the equity curve and apply `JetBrains Mono` for axes ticks, tooltips, and heatmap text.
4. **Implementation Strategy**: Detailed step-by-step roadmap provided in `analysis.md` for immediate execution by the Worker.

---

## 5. Verification Method

1. **File Inspection**:
   - Inspect `c:\Users\juanc\Desktop\prueba\.agents\explorer_charts_m3\analysis.md` for the comprehensive function map, code-level analysis, and implementation roadmap.
2. **Backend Regression Verification**:
   - Run the Python test suite to ensure quantitative integrity:
     ```powershell
     python -m pytest tests/
     ```
3. **Frontend Invalidation Conditions**:
   - If any `Chart` canvas throws "Canvas is already in use", check that `window[canvasId + 'Inst'].destroy()` is executed.
   - If Lightweight Charts grid is illegible or too bright, verify grid line opacity is between `0.03` and `0.05`.
