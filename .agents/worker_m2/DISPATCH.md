## 2026-08-16T19:51:42Z
You are Worker M2 (Institutional HTML5 Workspace Implementer) for Milestone 2 of the Binary Options Quantitative Terminal UI/UX Redesign project.
Your working directory is: c:\Users\juanc\Desktop\prueba\.agents\worker_m2\

You MUST read:
1. c:\Users\juanc\Desktop\prueba\ORIGINAL_REQUEST.md
2. c:\Users\juanc\Desktop\prueba\PROJECT.md
3. c:\Users\juanc\Desktop\prueba\.agents\explorer_m2\m2_plan.md
4. c:\Users\juanc\Desktop\prueba\templates\index.html
5. c:\Users\juanc\Desktop\prueba\static\css\style.css

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Write ownership:
You EXCLUSIVELY own: c:\Users\juanc\Desktop\prueba\templates\index.html

Your task:
Refactor `templates/index.html` strictly following the full specification and blueprint in `m2_plan.md`:
1. `<head>` metadata: Preconnect Google Fonts for `Inter` (300, 400, 500, 600, 700) and `JetBrains Mono` (400, 500, 600, 700), stylesheets, favicon, Lightweight Charts v4 and Chart.js scripts.
2. Institutional Header (`.app-header`):
   - Logo with glowing gradient: `<h1>Binarias <span>Simulator</span></h1>` + `.badge-quant` ("QUANT TERMINAL PRO").
   - Mode switcher pill: `.mode-switch-container` with `#mode-smart` ("⚡ Modo Inteligente (Piloto Automático)") and `#mode-advanced` ("⚙️ Modo Avanzado (Manual)").
   - Telemetry group: Rust Quantitative Core active pill + Live WebSocket pulse badge (`#live-badge`, `#live-badge-text`, `.pulse-dot`).
   - Advanced mode navigation: `.tabs-nav` with tab buttons (`#btn-resultados`, `#btn-estadisticas`, `#btn-optimizador`, etc.).
3. Smart Mode Workspace (`#smart-dashboard`):
   - High-density control bar (`.smart-sidebar.glass-card`): Single-line layout with `#btn-smart-run`, `#smart-preset-select` (with all 3 presets), 9 universe checkboxes (`name="smart-universe"` with `.asset-wr-badge` spans), 8 numeric inputs (`#smart-streak-length`, `#smart-base-capital`, `#smart-profit-pct`, `#smart-risk-capital` readonly, `#smart-attempts`, `#smart-payout`, `#smart-generations`, `#smart-population`), and tooltips.
   - Cyberpunk SSE console: `#smart-console-box`, `#smart-progress-bar-fill`, `#smart-console-logs`.
   - Results Area (`.smart-results-area`):
     - Top-5 Strategy ranking wrapper `#smart-top-5-box` with `#smart-top-5-list`.
     - Row 1: Plan de Rachas (`#smart-rec-content`) and Escalera Paroli (`#smart-ladder-content`).
     - Row 2: Heatmap de Correlación (`#smart-correlation-canvas`) and Selected Assets Table (`#smart-selected-assets-table`, `#smart-selected-assets-body`).
     - Row 3: Curva de Capital Barbell (`#smart-equity-chart-canvas`) and Conos Monte Carlo P5-P95 (`#smart-mc-chart-canvas`).
     - Row 4: TradingView Candlestick chart (`#smart-asset-selector`, `#smart-tv-chart`, `#smart-tv-chart-empty`) and Matriz de Markov (`#smart-markov-table`, `#smart-markov-explanation`).
4. Advanced Mode Workspace:
   - Mercado (`#dashboard`): `#pair-selector`, `#interval-selector`, `#source-selector`, `#tv-chart`, `#chart-loader`.
   - Backtest (`#backtest`): `#backtest-form`, `#run-backtest-btn`, `#save-backtest-btn`, `#strategy-selector`, `#dynamic-params`, `#expiry-candles`, `#payout`, Barbell capital controls (`#backtest-n-consecutive`, `#backtest-cycle-prob`, `#backtest-bet-fraction`), Rust genetic controls (`#gen-generations`, `#gen-population`, `#gen-min-trades`, `#optimize-genetic-btn`, `#genetic-progress-fill`, `#genetic-progress-text`, `#genetic-progress-eta`, `#genetic-feedback`), backtest progress (`#backtest-progress-fill`), Quick stats cards (`#stat-winrate`, `#stat-trades`, `#stat-pnl`, `#stat-mw`, `#stat-ml`), `#equity-chart`, and `#trades-table`.
   - Historial (`#resultados`): `#btn-clear-history`, `#history-list`, `#saved-list`.
   - Estadísticas (`#estadisticas`): `#autocorr-chart`, `#streaks-chart`, `#hourly-chart`, `#cond-probs`, `#market-state-chart`, `#markov-table`.
   - Optimizador (`#optimizador`): Inputs (`#opt-winrate`, `#opt-payout`, `#opt-base-capital`, `#opt-profit-pct`, `#opt-risk-capital`, `#opt-target-capital`, `#opt-attempts`), `#btn-calc-streak`, `#streak-progress-fill`, `#streak-recommendation-content`, `#bet-ladder-container`, `#streak-alternatives-table`, and `#mc-chart`.
5. Scripts at end of body: `charts.js` and `app.js`.
6. Strict Invariant: 100% preservation of all 105 DOM IDs and form inputs. Zero missing elements.
