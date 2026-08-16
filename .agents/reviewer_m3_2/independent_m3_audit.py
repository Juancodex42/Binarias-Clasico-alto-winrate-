"""
Independent Milestone 3 Auditor & Adversarial Stress-Tester
Reviewer 2 - Milestone 3
"""

import os
import re
import json

BASE_DIR = r"c:\Users\juanc\Desktop\prueba"

def run_checks():
    results = {}
    
    # 1. Read files
    charts_path = os.path.join(BASE_DIR, "static", "js", "charts.js")
    app_path = os.path.join(BASE_DIR, "static", "js", "app.js")
    html_path = os.path.join(BASE_DIR, "templates", "index.html")
    css_path = os.path.join(BASE_DIR, "static", "css", "style.css")
    
    with open(charts_path, "r", encoding="utf-8") as f:
        charts_js = f.read()
    with open(app_path, "r", encoding="utf-8") as f:
        app_js = f.read()
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # 2. Check Line 1098 Bug Fix (mainChart vs tvChart)
    # Check if tvChart is called in highlightTradeOnChart
    tvchart_calls = re.findall(r'highlightTradeOnChart\([^)]*tvChart[^)]*\)', app_js)
    mainchart_calls = re.findall(r'highlightTradeOnChart\([^)]*mainChart[^)]*\)', app_js)
    results['bug_fix_1098'] = {
        'tvChart_calls_found': len(tvchart_calls),
        'mainChart_calls_found': len(mainchart_calls),
        'passed': len(tvchart_calls) == 0 and len(mainchart_calls) > 0
    }

    # 3. Check 105 DOM IDs
    # List of 105 DOM IDs from M2 specification
    expected_ids = [
        "mode-smart", "mode-advanced", "live-badge", "live-badge-text", "btn-resultados",
        "btn-estadisticas", "btn-optimizador", "smart-dashboard", "btn-smart-run",
        "smart-preset-select", "smart-streak-length", "smart-base-capital", "smart-profit-pct",
        "smart-risk-capital", "smart-attempts", "smart-payout", "smart-generations",
        "smart-population", "smart-console-box", "smart-progress-bar-fill", "smart-console-logs",
        "smart-top-5-box", "smart-top-5-list", "smart-rec-content", "smart-ladder-content",
        "smart-correlation-canvas", "smart-selected-assets-table", "smart-selected-assets-body",
        "smart-equity-chart-canvas", "smart-mc-chart-canvas", "smart-asset-selector",
        "smart-tv-chart", "smart-tv-chart-empty", "smart-markov-table", "smart-markov-explanation",
        "dashboard", "pair-selector", "interval-selector", "source-selector", "tv-chart",
        "chart-loader", "backtest", "backtest-form", "sec-strategy", "strategy-selector",
        "dynamic-params", "expiry-candles", "payout", "sec-barbell", "group-n-consecutive",
        "backtest-n-consecutive", "backtest-cycle-prob", "backtest-bet-fraction", "sec-genetic",
        "gen-generations", "gen-population", "gen-min-trades", "optimize-genetic-btn",
        "genetic-progress-container", "genetic-progress-fill", "genetic-progress-text",
        "genetic-progress-eta", "genetic-feedback", "run-backtest-btn", "save-backtest-btn",
        "backtest-progress-container", "backtest-progress-fill", "backtest-progress-text",
        "backtest-progress-eta", "quick-stats", "stat-winrate", "stat-trades", "stat-pnl",
        "stat-mw", "stat-ml", "equity-chart", "trades-table", "resultados", "btn-clear-history",
        "history-list", "saved-list", "estadisticas", "autocorr-chart", "streaks-chart",
        "hourly-chart", "cond-probs", "market-state-chart", "markov-table", "optimizador",
        "opt-winrate", "opt-payout", "opt-base-capital", "opt-profit-pct", "opt-risk-capital",
        "opt-target-capital", "opt-attempts", "btn-calc-streak", "streak-progress-container",
        "streak-progress-fill", "streak-progress-text", "streak-progress-eta",
        "streak-recommendation-content", "bet-ladder-container", "streak-alternatives-table",
        "mc-chart"
    ]
    missing_ids = [dom_id for dom_id in expected_ids if f'id="{dom_id}"' not in html]
    results['dom_ids_105'] = {
        'total_expected': len(expected_ids),
        'missing_count': len(missing_ids),
        'missing_ids': missing_ids,
        'passed': len(missing_ids) == 0
    }

    # 4. Check Form Inputs (37)
    input_matches = re.findall(r'<(?:input|select|textarea)\b[^>]*id="([^"]+)"', html)
    results['form_inputs'] = {
        'found_count': len(input_matches),
        'ids': input_matches
    }

    # 5. Check Global Window Hooks
    required_window_hooks = [
        "window.togglePineScriptModal",
        "window.copyPineScript",
        "window.copyAIPrompt",
        "window.showToast",
        "window.createCandlestickChart",
        "window.initLightweightChart",
        "window.updateCandlestickChart",
        "window.addSignalMarkers",
        "window.formatYAxisTick",
        "window.createEquityCurve",
        "window.renderEquityCurve",
        "window.createBarChart",
        "window.createGrowthRateChart",
        "window.createMonteCarloChart",
        "window.renderMonteCarloCones",
        "window.createCorrelationHeatmap",
        "window.renderCorrelationHeatmap",
        "window.renderDiagnosticsCharts"
    ]
    missing_hooks = []
    combined_js = charts_js + "\n" + app_js
    for hook in required_window_hooks:
        if hook not in combined_js:
            missing_hooks.append(hook)
    results['global_window_hooks'] = {
        'total_required': len(required_window_hooks),
        'missing_hooks': missing_hooks,
        'passed': len(missing_hooks) == 0
    }

    # 6. Chart Lifecycle & Memory Management
    # Verify destroy calls before creating new instances
    destroy_checks = {
        'equity_curve_destroy': 'window[canvasId + \'Inst\'].destroy()' in charts_js,
        'bar_chart_destroy': 'window[canvasId + \'Inst\'].destroy()' in charts_js,
        'growth_rate_chart_destroy': 'window.gnChartInst.destroy()' in charts_js,
        'monte_carlo_destroy': 'window.mcChartInst.destroy()' in charts_js,
        'trade_lines_cleanup': 'removePriceLine' in app_js,
    }
    results['chart_lifecycle'] = {
        'checks': destroy_checks,
        'passed': all(destroy_checks.values())
    }

    # 7. Error states & null guards
    null_guards = {
        'createCandlestickChart_el_null': 'if (!el) return null;' in charts_js,
        'createEquityCurve_el_null': 'if (!el) return;' in charts_js,
        'createBarChart_el_null': 'if (!el) return;' in charts_js,
        'createGrowthRateChart_el_null': 'if (!el) return;' in charts_js,
        'createMonteCarloChart_el_null': 'if (!el) return;' in charts_js,
        'createCorrelationHeatmap_canvas_null': 'if (!canvas) return;' in charts_js,
        'createCorrelationHeatmap_empty_fallback': 'Sin datos de correlación' in charts_js,
        'smart_tv_chart_empty_overlay_present': 'id="smart-tv-chart-empty"' in html,
        'smart_tv_chart_empty_overlay_hidden_on_load': 'document.getElementById(\'smart-tv-chart-empty\')' in app_js,
        'monte_carlo_zero_clamping': 'v <= 0.01 ? 0.01 : v' in charts_js,
        'highlightTradeOnChart_null_guard': 'if (!seriesObj || !trade) return;' in app_js,
    }
    results['error_states_and_null_guards'] = {
        'checks': null_guards,
        'passed': all(null_guards.values())
    }

    # 8. Check Legacy Color Tokens in charts.js and app.js
    legacy_tokens = ["#00f5a0", "#ff4d4d", "#58a6ff", "#30363d", "#8b949e", "#c9d1d9", "#3fb950", "#a371f7"]
    found_legacy = {}
    for token in legacy_tokens:
        in_charts = token in charts_js
        in_app = token in app_js
        if in_charts or in_app:
            found_legacy[token] = {'in_charts': in_charts, 'in_app': in_app}
    results['legacy_tokens'] = {
        'found_legacy': found_legacy,
        'passed': len(found_legacy) == 0
    }

    # 9. Master Design Guide Palette Checks
    mdg_tokens = {
        'cyber_emerald': '#10b981' in charts_js and '#10b981' in app_js,
        'rose_crimson': '#f43f5e' in charts_js and '#f43f5e' in app_js,
        'electric_sky': '#38bdf8' in charts_js and '#38bdf8' in app_js,
        'quantum_amethyst': '#a855f7' in charts_js and '#a855f7' in app_js,
        'amber_flame': '#f59e0b' in charts_js,
        'dark_slate': '#141d2e' in charts_js,
        'text_muted': '#94a3b8' in charts_js,
    }
    results['mdg_tokens'] = {
        'checks': mdg_tokens,
        'passed': all(mdg_tokens.values())
    }

    print(json.dumps(results, indent=2))
    return results

if __name__ == '__main__':
    run_checks()
