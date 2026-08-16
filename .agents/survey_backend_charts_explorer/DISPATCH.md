## 2026-08-16T19:19:05Z
You are the Backend & Charts Explorer for the Binary Options Quantitative Terminal UI/UX Redesign project.
Your working directory is: c:\Users\juanc\Desktop\prueba\.agents\survey_backend_charts_explorer\

You MUST read:
1. c:\Users\juanc\Desktop\prueba\ORIGINAL_REQUEST.md
2. Backend Python / Flask / Rust integration files across c:\Users\juanc\Desktop\prueba (e.g. app.py, server.py, routes, simulation engines, Rust extensions if any).
3. Chart implementation scripts and test suites.

Your task is to perform an exhaustive survey of:
1. Backend APIs & Endpoints:
   - All Flask / HTTP routes (GET, POST), request parameters, response JSON schemas.
   - WebSocket events, message formats, streaming channels (real-time quotes, backtest progress, optimizer ticks).
   - How simulation results, Monte Carlo simulations, Markov matrices, and trade logs are structured and passed to the frontend.
2. Charting Integrations:
   - Lightweight Charts initialization, candlestick series, volume series, marker creation for CALL/PUT signals, time scaling, theme configuration.
   - Chart.js instances (Equity curve, Monte Carlo percentiles P5/P25/P50/P75/P95, Correlation heatmap / Markov matrix, drawdown charts), dataset structures, options, plugins.
3. Test Infrastructure & Run Commands:
   - Existing automated test suites (pytest, unittest, backend test scripts, frontend tests).
   - How to start the backend server, run simulations, and execute verification commands.
4. Potential Integration Risks & Constraints:
   - Any backend expectations on DOM structure or form submission format.

Write your comprehensive report to:
c:\Users\juanc\Desktop\prueba\.agents\survey_backend_charts_explorer\survey_backend_charts_report.md
and write a standard handoff.md in your working directory.
When finished, send a message to the caller with the summary and path to your report.
