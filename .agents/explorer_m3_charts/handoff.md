# Handoff Report: Milestone 3 Charting Engine & Visual System Investigation

**Target**: Orchestrator  
**From**: Explorer Agent (`explorer_m3_charts`)  
**Working Directory**: `c:\Users\juanc\Desktop\prueba\.agents\explorer_m3_charts`  
**Date**: 2026-08-16  

---

## 1. Observation
1. **Lightweight Charts Initialization (`static/js/charts.js:11-72`)**:
   - `createCandlestickChart` uses `vertLines: { color: 'rgba(48, 54, 61, 0.3)' }` and `horzLines: { color: 'rgba(48, 54, 61, 0.3)' }` (legacy GitHub grey).
   - Candlestick series uses `upColor: '#00f5a0'` (fluorescent green) and `downColor: '#ff4d4d'` (neon red), violating the anti-chromostereopsis design guidelines in `documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md` Section 3.1 & 4.3.
   - Crosshair configuration is minimal with unstyled grey lines.
2. **Signal Markers & Candle Pre-processing (`static/js/app.js:281-314, 415-470, 618-659`)**:
   - `prepareCandles` (`app.js:640`) and `updateLiveCandleInChart` (`app.js:295`) directly inject hardcoded bar colors `#00f5a0` and `#ff4d4d`.
   - `buildChartMarkers` (`app.js:435, 443, 462`) assigns `#00f5a0` (CALL/WIN) and `#ff4d4d` (PUT/LOSS).
   - `#smart-tv-chart-empty` is present in `templates/index.html:350` and is properly hidden when candles are loaded in `app.js:2337`.
3. **Chart.js Equity Curve (`static/js/charts.js:119-234`)**:
   - `createEquityCurve` uses flat `#58a6ff` line and `rgba(88, 166, 255, 0.12)` background without vertical linear gradient.
   - Tooltip uses default styling without tabular numerals or localized currency format.
   - Dynamic log scale condition `(maxVal / Math.max(minVal, 0.01)) > 100 && minVal >= 1.0` is functional but tick formatting can be further refined for readability.
4. **Chart.js Monte Carlo Cones (`static/js/charts.js:290-375`)**:
   - `createMonteCarloChart` renders 5 unshaded lines without area fills between percentiles.
   - Color palette uses legacy tones (`#3fb950`, `#58a6ff`, `#f85149`).
   - Missing Initial Capital horizontal baseline reference.
5. **Canvas 2D Correlation Heatmap (`static/js/charts.js:377-469`)**:
   - `createCorrelationHeatmap` handles `window.devicePixelRatio`, but positive values interpolate toward red `(248, 81, 73)` instead of Cyber Emerald / Electric Sky, and numeric text uses `Inter` instead of `JetBrains Mono`.
6. **Statistical Diagnostics Charts (`static/js/charts.js:236-289`, `static/js/app.js:1140-1185`)**:
   - `#autocorr-chart`, `#streaks-chart`, `#hourly-chart`, `#market-state-chart`, `#gn-chart`, and `#kelly-chart` use generic single-color bar styling without threshold lines or regime-specific colors.
7. **Test Suite Baseline**:
   - Executed `pytest` across entire project: **322 passed, 0 failed** in 186.70s.

---

## 2. Logic Chain
1. **Observation 1 & 2 $\rightarrow$ Lightweight Charts Theme**:
   - Because `prepareCandles` and `updateLiveCandleInChart` in `app.js` attach per-candle `color` properties, modifying only `createCandlestickChart` in `charts.js` is insufficient. Both `charts.js` and `app.js` must be synchronized with Cyber Emerald `#10b981` (CALL/WIN) and Rose Crimson `#f43f5e` (PUT/LOSS).
   - Replacing `rgba(48, 54, 61, 0.3)` with `rgba(255, 255, 255, 0.03)` directly satisfies Edward Tufte's Data-to-Ink ratio by removing intrusive grid contrast.
2. **Observation 3 $\rightarrow$ Equity Curve Gradient & Dark Tooltips**:
   - A vertical Canvas linear gradient (`ctx.createLinearGradient(0, 0, 0, height)`) with stops at `rgba(56, 189, 248, 0.22)` $\rightarrow$ `rgba(56, 189, 248, 0.00)` combined with Electric Sky `#38bdf8` stroke creates the luminous FinTech glow specified in `GUIA_MAESTRA` Section 4.3.
   - Setting tooltip `backgroundColor: '#141d2e'` with body font `'JetBrains Mono', monospace` ensures numbers never drift or blur during hover inspection.
3. **Observation 4 $\rightarrow$ Monte Carlo Probability Fan**:
   - Configuring `fill: '+1'` with subtle 0.06-0.07 alpha on percentiles (P95 $\rightarrow$ P75 $\rightarrow$ P50 $\rightarrow$ P25 $\rightarrow$ P5) transforms flat lines into intuitive probability density cones.
   - Adding a dashed Initial Capital baseline (`Array(N).fill(initialCapital)`) provides an immediate visual benchmark for expected payoff.
4. **Observation 5 $\rightarrow$ Heatmap Precision & Typography**:
   - Setting explicit CSS width/height alongside backing store DPI scaling eliminates subpixel blur.
   - Calibrating color interpolation to Diverging (Rose `#f43f5e` $\rightarrow$ Dark Slate `#141d2e` $\rightarrow$ Cyber Emerald `#10b981`) aligns with portfolio diversification theory.
   - Tabular monospace numbers in `'JetBrains Mono'` prevent misalignment inside matrix cells.
5. **Observation 6 $\rightarrow$ Diagnostics Cohesion**:
   - Customizing bar palettes (Amethyst `#a855f7` for Autocorr, WR-based color thresholding for Hourly, and Regime tokens for Market State) elevates Advanced Mode to institutional grade.

---

## 3. Caveats
- No caveats regarding backend API schema: all chart renderers consume existing payload schemas (`candles`, `equity_curve`, `signals`, `correlation_matrix`, `p95..p5`).
- Preserving canvas DOM IDs (`#tv-chart`, `#smart-tv-chart`, `#equity-chart`, `#smart-equity-chart-canvas`, `#smart-mc-chart-canvas`, `#mc-chart`, `#smart-correlation-canvas`, `#autocorr-chart`, `#streaks-chart`, `#hourly-chart`, `#market-state-chart`, `#gn-chart`, `#kelly-chart`) is mandatory to maintain 100% test and contract compatibility.

---

## 4. Conclusion
The charting architecture is functionally solid and structurally sound, but requires visual refactoring across `static/js/charts.js` and `static/js/app.js` to eliminate legacy GitHub/neon artifacts and fully implement the Design System specified in `documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`. Detailed analysis and step-by-step implementation plan have been written to `c:\Users\juanc\Desktop\prueba\.agents\explorer_m3_charts\analysis.md`.

---

## 5. Verification Method
1. **Unit & Regression Tests**:
   - Run `pytest` to ensure all 322 existing tests pass with zero regressions.
2. **Static Integrity Checks**:
   - Verify `charts.js` and `app.js` contain the calibrated color tokens (`#38bdf8`, `#10b981`, `#f43f5e`, `#a855f7`, `#141d2e`, `rgba(255, 255, 255, 0.03)`).
   - Verify no remaining `#00f5a0` or `#ff4d4d` tokens exist in chart renderers.
3. **DOM & Canvas Verification**:
   - Ensure all 13 chart and diagnostic canvas elements initialize and resize without throwing JavaScript exceptions.
