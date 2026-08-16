# Handoff Report — Milestone 3 Specification Mining

## 1. Observation
From inspecting `documentos_md/GUIA_MAESTRA_REDISENO_UI_UX_TERMINAL_PRO.md`, `ORIGINAL_REQUEST.md`, `PROJECT.md`, `static/css/style.css`, `static/js/charts.js`, `static/js/app.js`, and `templates/index.html`, the following authoritative specifications were directly observed:

- **Color Tokens & Palettes**:
  - Background & Surface Architecture: Canvas `--bg-canvas: #080b11`, Base Card `--bg-card: #0e1420`, Elevated Surface `--bg-elevated: #141d2e`, Hover `--bg-hover: #1c273d`.
  - Borders: Standard 1px `--border-subtle: rgba(255, 255, 255, 0.07)`, Focus / Active `--border-focus: rgba(56, 189, 248, 0.35)`.
  - Semantic Accents: Electric Sky `--accent-primary: #38bdf8` (RGB: 56, 189, 248), Cyber Emerald `--accent-green: #10b981` (RGB: 16, 185, 129), Rose Crimson `--accent-red: #f43f5e` (RGB: 244, 63, 94), Quantum Amethyst `--accent-purple: #a855f7` (RGB: 168, 85, 247), Golden Amber `--accent-amber: #f59e0b` (RGB: 245, 158, 11).
  - Typography: UI font `'Inter', sans-serif`, Numerics / Tabular `'JetBrains Mono', monospace` with `font-variant-numeric: tabular-nums` and `font-feature-settings: "tnum" 1, "zero" 1`.

- **Lightweight Charts Candlesticks & Signal Markers**:
  - Theme: Transparent canvas background (`{ type: 'solid', color: 'transparent' }`), grid lines `rgba(255, 255, 255, 0.03)`, text `#94a3b8`, borders `rgba(255, 255, 255, 0.07)`.
  - Candlestick Series: `upColor: '#10b981'`, `downColor: '#f43f5e'`, `borderVisible: false`, `wickUpColor: '#10b981'`, `wickDownColor: '#f43f5e'`, price precision `5`, `minMove: 0.00001`.
  - Markers:
    - CALL Entry: `shape: 'arrowUp'`, `position: 'belowBar'`, `color: '#10b981'`, `text: 'CALL @ <price>'`.
    - PUT Entry: `shape: 'arrowDown'`, `position: 'aboveBar'`, `color: '#f43f5e'`, `text: 'PUT @ <price>'`.
    - EXIT Resolution: `shape: 'circle'`, `color: '#10b981'` (WIN) / `'#f43f5e'` (LOSS), dynamic positioning (`aboveBar` for CALL WIN / PUT LOSS; `belowBar` for CALL LOSS / PUT WIN), `text: 'WIN @ <price> (+<pnl>$)'` / `'LOSS @ <price> (<pnl>$)'`.
    - Deduplication: Handled through `seenKeys` `Set` with composite key `${time}_${direction}_${result}`.

- **Chart.js v4 Curves & Stochastic Cones**:
  - Global defaults: `color: '#94a3b8'`, font `'Inter'`, Tooltip background `rgba(20, 29, 46, 0.95)` (`--bg-elevated`) with border `rgba(255, 255, 255, 0.08)` and monospaced tabular body.
  - Equity Curve: `borderColor: '#38bdf8'`, gradient background `rgba(56, 189, 248, 0.25)` to `rgba(56, 189, 248, 0.00)`, point hover radius `4`, auto-logarithmic scale switch when dynamic range $> 100$ and minimum $\ge 1.0$.
  - Monte Carlo Cones: 5 bands (P95 `#10b981` dashed, P75 `#10b981` 0.45 opacity, P50 `#38bdf8` 2.5px solid, P25 `#f43f5e` 0.45 opacity, P5 `#f43f5e` dashed).
  - Diagnostic Bar Charts: Autocorrelation (`#a855f7`), Streaks (`#38bdf8`), Hourly WR (`#38bdf8`), Market State (`#a855f7`), Growth Rate G(N) (Optimal N `#10b981`, others `#38bdf8`).

- **Canvas 2D Correlation Matrix Heatmap**:
  - Container `#smart-correlation-canvas`, responsive dimensions with High-DPI Retina scaling (`dpr = window.devicePixelRatio || 1`).
  - Margins: left `70px`, top `15px`, right `15px`, bottom `35px`, cell gap `1.5px`.
  - Color interpolation: Base neutral `#0e1420`, positive correlation to Rose Crimson `#f43f5e` (or Cyber Emerald `#10b981`), negative correlation to Electric Sky `#38bdf8`.
  - Fallback state: `Sin datos de correlación` on empty matrix.

- **Micro-Interactions & Motion Tokens**:
  - Acceleration curve: `cubic-bezier(0.16, 1, 0.3, 1)` (`--ease-out-expo`).
  - Durations: `--duration-micro: 120ms`, `--duration-state: 180ms`, `--duration-reveal: 240ms`.
  - Progress bar shimmer: `linear-gradient(90deg, #a855f7 0%, #38bdf8 50%, #10b981 100%)` with 2s linear infinite background shift.
  - Live pulse streaming indicator: `.pulse-dot` with 2s ease-in-out breathing animation (`scale(1)` to `scale(0.85)`).
  - Strategy ranking pills: `transform: translateY(-1px)` hover elevation and active state highlight.

- **API & UI Hooks Invariant Contract**:
  - Global export functions: `window.togglePineScriptModal(id)`, `window.copyPineScript(id)`, `window.copyAIPrompt(id)`.
  - Charting bridge: `createCandlestickChart`, `createEquityCurve`, `createMonteCarloChart`, `createCorrelationHeatmap`, `createBarChart`, `createGrowthRateChart`, `addSignalMarkers`, `buildChartMarkers`.
  - Preserved 105 DOM element IDs.

---

## 2. Logic Chain
1. **Observation**: The design system requires strict dark mode anti-halation and anti-chromostereopsis principles (`GUIA_MAESTRA` §3, §4).
   **Inference**: Charting canvases must not use pure black `#000000` or aggressive saturated neon colors (`#00f5a0`, `#ff4d4d`, `#58a6ff`). They must be updated to use the calibrated tokens: `#0e1420` surface, `#10b981` Cyber Emerald, `#f43f5e` Rose Crimson, and `#38bdf8` Electric Sky.

2. **Observation**: In `charts.js`, `Chart.defaults.color` is `#8b949e`, candlestick `upColor` is `#00f5a0`, and equity curve border is `#58a6ff`.
   **Inference**: Milestone 3 implementation must harmonize these parameters with CSS variables and hex tokens defined in Milestone 1 (`style.css`), ensuring seamless visual alignment between the UI cards and the chart renders.

3. **Observation**: High-density numerical displays and tables require fixed character widths to prevent visual jitter during streaming (`GUIA_MAESTRA` §5.1).
   **Inference**: Chart tooltips, axis tick formatters (`formatYAxisTick`), and Canvas 2D correlation matrix text must use `'JetBrains Mono', monospace` or tabular numeric formatting (`font-variant-numeric: tabular-nums`).

4. **Observation**: The user may switch between Smart Mode and Advanced Mode tabs, which unmounts or resizes containers (`app.js:661`).
   **Inference**: Charting engines must bind to `ResizeObserver` and apply a debounced refit `timeScale().fitContent()` to ensure charts always render at 100% container width with zero blurriness or layout distortion.

5. **Observation**: Network dropouts during live streaming or missing backtest data could leave blank canvases or throw JavaScript exceptions (`app.js:361`).
   **Inference**: Robust fallback mechanisms must be enforced: empty chart overlays (`#smart-tv-chart-empty`), centered canvas fallback text for correlation heatmaps, $\ge 0.01$ clamping for Monte Carlo log scales, and seamless REST polling fallbacks for WebSocket dropouts.

---

## 3. Caveats
- No caveats. All charting engines (Lightweight Charts v4, Chart.js v4, HTML5 Canvas 2D) and their interaction hooks in the codebase were inspected against the Master Design Guide, HTML templates, and test suites.

---

## 4. Conclusion
The specification for Milestone 3 (Charting Engine Harmonization & Micro-Interactions) has been extracted and documented in `spec.md`. The implementation requires:
1. Updating `charts.js` defaults and series colors to match the institutional palette (`#10b981`, `#f43f5e`, `#38bdf8`, `#a855f7`, `#0e1420`).
2. Refining marker formatting and dynamic positioning for CALL/PUT entries and WIN/LOSS resolutions.
3. Applying high-DPI scaling and smooth slate interpolation to the Canvas 2D correlation heatmap.
4. Ensuring auto-logarithmic scaling and tabular tick formatters on the equity curve and Monte Carlo cones.
5. Preserving all 105 DOM IDs, window hooks, and backend SSE/REST endpoints.

---

## 5. Verification Method
1. **Specification Document Inspection**:
   - Verify `c:\Users\juanc\Desktop\prueba\.agents\spec_miner_m3\spec.md` contains the complete specification, Features Discovered table (15 features), and Edge Cases table (10 edge cases).
2. **Design Tokens & Contrast Verification**:
   - Inspect CSS variables in `static/css/style.css` and check contrast ratios against WCAG 2.2 AAA / APCA.
3. **Automated Test Suite Verification**:
   - Run `pytest tests/test_ui_visual_system.py`, `pytest tests/test_m1_css_integrity.py`, and `pytest tests/test_m2_html_workspace_integrity.py`.
