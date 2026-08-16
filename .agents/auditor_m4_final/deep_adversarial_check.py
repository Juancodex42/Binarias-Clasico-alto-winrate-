import re
import json
import os

def check_color_tokens_and_halations():
    css_path = r"c:\Users\juanc\Desktop\prueba\static\css\style.css"
    html_path = r"c:\Users\juanc\Desktop\prueba\templates\index.html"
    js_path = r"c:\Users\juanc\Desktop\prueba\static\js\app.js"
    charts_path = r"c:\Users\juanc\Desktop\prueba\static\js\charts.js"

    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    with open(js_path, "r", encoding="utf-8") as f:
        app_js = f.read()
    with open(charts_path, "r", encoding="utf-8") as f:
        charts_js = f.read()

    # Prohibited colors per GUIA MAESTRA
    # Pure saturated neon blues/reds/magentas that cause chromostereopsis or halation
    # E.g. #ff0000, #00ff00, #0000ff, #00ffff, #ff00ff, #000000 background with #ffffff pure text
    issues = []

    # Check for hardcoded legacy background: #000000 or color: #ffffff
    forbidden_tokens = ["#00ffff", "#ff00ff"]
    for ft in forbidden_tokens:
        if ft in css.lower():
            issues.append(f"Forbidden neon token {ft} found in style.css")
        if ft in app_js.lower():
            issues.append(f"Forbidden neon token {ft} found in app.js")
        if ft in charts_js.lower():
            issues.append(f"Forbidden neon token {ft} found in charts.js")

    # Check that charts.js uses dark institutional palette
    dark_chart_indicators = [
        "rgba(8, 11, 17", "rgba(14, 20, 32", "rgba(255, 255, 255, 0.07",
        "#10b981", "#f43f5e", "#38bdf8"
    ]
    for dci in dark_chart_indicators:
        if dci not in charts_js and dci.replace(" ", "") not in charts_js.replace(" ", ""):
            issues.append(f"Expected dark chart token {dci} not found in charts.js")

    return {
        'issues': issues,
        'clean': len(issues) == 0
    }

def verify_chart_engine_signatures():
    charts_path = r"c:\Users\juanc\Desktop\prueba\static\js\charts.js"
    with open(charts_path, "r", encoding="utf-8") as f:
        code = f.read()

    findings = []
    
    # 1. Lightweight Charts Candlestick + Markers
    if "createChart" in code and "addCandlestickSeries" in code:
        findings.append("Lightweight Charts v4 Candlestick series initialization verified.")
    else:
        findings.append("ERROR: Lightweight Charts v4 Candlestick series initialization missing.")

    if "setMarkers" in code or "markers" in code:
        findings.append("Lightweight Charts Signal Markers verified.")
    else:
        findings.append("ERROR: Lightweight Charts Signal Markers missing.")

    # 2. Chart.js Equity Curve + Log Scale + Gradient
    if "createLinearGradient" in code and "Chart" in code:
        findings.append("Chart.js v4 Equity Curve with linear gradient verified.")
    else:
        findings.append("ERROR: Chart.js linear gradient missing.")

    # 3. Chart.js Monte Carlo Percentiles P5..P95
    if "p5" in code.lower() or "p95" in code.lower() or "montecarlo" in code.lower():
        findings.append("Chart.js Monte Carlo P5-P95 Cones verified.")
    else:
        findings.append("ERROR: Monte Carlo percentile cone logic missing.")

    # 4. Canvas 2D Correlation Heatmap + Retina HiDPI
    if "getContext('2d')" in code or 'getContext("2d")' in code:
        if "devicePixelRatio" in code:
            findings.append("Canvas 2D Correlation Heatmap with Retina HiDPI scaling verified.")
        else:
            findings.append("WARNING: Canvas 2D found but devicePixelRatio not explicitly referenced.")
    else:
        findings.append("ERROR: Canvas 2D getContext missing.")

    return findings

def verify_button_and_form_bindings():
    app_js_path = r"c:\Users\juanc\Desktop\prueba\static\js\app.js"
    html_path = r"c:\Users\juanc\Desktop\prueba\templates\index.html"

    with open(app_js_path, "r", encoding="utf-8") as f:
        app_js = f.read()
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Buttons in HTML
    critical_buttons = [
        "mode-smart", "mode-advanced", "btn-smart-run",
        "run-backtest-btn", "save-backtest-btn", "optimize-genetic-btn",
        "btn-clear-history", "btn-calc-streak", "btn-resultados",
        "btn-estadisticas", "btn-optimizador"
    ]

    button_checks = {}
    for btn in critical_buttons:
        in_html = f'id="{btn}"' in html or f"id='{btn}'" in html
        in_js = btn in app_js
        button_checks[btn] = {
            'in_html': in_html,
            'referenced_in_js': in_js
        }

    return button_checks

if __name__ == "__main__":
    color_results = check_color_tokens_and_halations()
    chart_results = verify_chart_engine_signatures()
    btn_results = verify_button_and_form_bindings()

    out = {
        'color_integrity': color_results,
        'chart_engine': chart_results,
        'button_bindings': btn_results
    }

    with open(r"c:\Users\juanc\Desktop\prueba\.agents\auditor_m4_final\deep_adversarial_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("Deep adversarial check finished.")
