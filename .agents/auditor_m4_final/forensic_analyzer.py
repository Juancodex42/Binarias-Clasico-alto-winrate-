import re
import ast
import json
import os
from bs4 import BeautifulSoup

def analyze_html_dom():
    html_path = r"c:\Users\juanc\Desktop\prueba\templates\index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")
    
    # 1. Collect all elements with IDs
    elements_with_id = soup.find_all(id=True)
    all_ids = set(el['id'] for el in elements_with_id)
    
    # 2. Collect all form inputs/selects/textareas
    inputs = soup.find_all(['input', 'select', 'textarea'])
    input_details = []
    for inp in inputs:
        inp_id = inp.get('id', '')
        inp_name = inp.get('name', '')
        inp_type = inp.get('type', inp.name)
        input_details.append({'tag': inp.name, 'id': inp_id, 'name': inp_name, 'type': inp_type})

    # 3. Collect all buttons
    buttons = soup.find_all('button')
    button_details = []
    for btn in buttons:
        btn_id = btn.get('id', '')
        btn_classes = btn.get('class', [])
        btn_onclick = btn.get('onclick', '')
        button_details.append({'id': btn_id, 'classes': btn_classes, 'onclick': btn_onclick, 'text': btn.get_text(strip=True)})

    # 4. Check specific contract IDs from PROJECT.md and GUIA_MAESTRA
    required_ids = [
        "mode-smart", "mode-advanced", "smart-preset-select", "smart-streak-length",
        "smart-base-capital", "smart-profit-pct", "smart-risk-capital", "smart-attempts",
        "smart-payout", "smart-generations", "smart-population", "smart-asset-selector",
        "btn-smart-run", "smart-console-box", "smart-progress-bar-fill", "smart-console-logs",
        "smart-top-5-box", "smart-top-5-list", "smart-rec-content", "smart-ladder-content",
        "smart-selected-assets-table", "smart-selected-assets-body", "smart-markov-table",
        "smart-markov-explanation", "smart-tv-chart", "smart-tv-chart-empty",
        "smart-equity-chart-canvas", "smart-mc-chart-canvas", "smart-correlation-canvas",
        "pair-selector", "interval-selector", "source-selector", "live-badge", "live-badge-text",
        "tv-chart", "chart-loader", "backtest-form", "run-backtest-btn", "save-backtest-btn",
        "strategy-selector", "dynamic-params", "expiry-candles", "payout",
        "backtest-n-consecutive", "backtest-cycle-prob", "backtest-bet-fraction",
        "optimize-genetic-btn", "gen-generations", "gen-population", "gen-min-trades",
        "genetic-progress-fill", "genetic-progress-text", "genetic-progress-eta",
        "genetic-feedback", "backtest-progress-fill", "stat-winrate", "stat-trades",
        "stat-pnl", "stat-mw", "stat-ml", "equity-chart", "trades-table", "btn-clear-history",
        "history-list", "saved-list", "autocorr-chart", "streaks-chart", "hourly-chart",
        "cond-probs", "market-state-chart", "markov-table", "opt-winrate", "opt-payout",
        "opt-base-capital", "opt-profit-pct", "opt-risk-capital", "opt-target-capital",
        "opt-attempts", "btn-calc-streak", "streak-progress-fill",
        "streak-recommendation-content", "bet-ladder-container", "streak-alternatives-table",
        "mc-chart"
    ]
    missing_required_ids = [rid for rid in required_ids if rid not in all_ids]

    return {
        'total_ids': len(all_ids),
        'all_ids': sorted(list(all_ids)),
        'total_inputs': len(inputs),
        'input_details': input_details,
        'total_buttons': len(buttons),
        'button_details': button_details,
        'required_ids_count': len(required_ids),
        'missing_required_ids': missing_required_ids,
        'raw_length': len(content)
    }

def analyze_css():
    css_path = r"c:\Users\juanc\Desktop\prueba\static\css\style.css"
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # Check color variables
    variables = dict(re.findall(r'(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);', css))
    
    # Check for forbidden pure black / pure white contrasts
    clean_css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    pure_black_bg = re.findall(r'background(?:-color)?\s*:\s*(#000|#000000|rgb\(\s*0\s*,\s*0\s*,\s*0\s*\))\b', clean_css, re.IGNORECASE)
    
    # Check font definitions
    has_inter = "Inter" in css
    has_jetbrains = "JetBrains Mono" in css
    has_tabular_nums = "tabular-nums" in css
    
    # Balanced braces
    open_braces = clean_css.count('{')
    close_braces = clean_css.count('}')

    return {
        'css_len': len(css),
        'variables_count': len(variables),
        'key_variables': {k: variables[k] for k in ['--bg-canvas', '--bg-surface', '--bg-surface-elevated', '--border-subtle', '--accent-primary', '--accent-profit', '--accent-loss', '--accent-quantum', '--accent-bullet'] if k in variables},
        'pure_black_bg_count': len(pure_black_bg),
        'pure_black_bg_matches': pure_black_bg,
        'has_inter': has_inter,
        'has_jetbrains': has_jetbrains,
        'has_tabular_nums': has_tabular_nums,
        'braces_balanced': open_braces == close_braces,
        'open_braces': open_braces,
        'close_braces': close_braces
    }

def analyze_js():
    app_js_path = r"c:\Users\juanc\Desktop\prueba\static\js\app.js"
    charts_js_path = r"c:\Users\juanc\Desktop\prueba\static\js\charts.js"
    
    with open(app_js_path, "r", encoding="utf-8") as f:
        app_js = f.read()
    with open(charts_js_path, "r", encoding="utf-8") as f:
        charts_js = f.read()

    # Extract all getElementById calls
    dom_lookups_app = set(re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", app_js))
    dom_lookups_charts = set(re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", charts_js))
    
    # Extract functions in charts.js
    chart_funcs = re.findall(r"function\s+([a-zA-Z0-9_]+)\s*\(", charts_js)
    chart_window_exports = re.findall(r"window\.([a-zA-Z0-9_]+)\s*=", charts_js)

    # Check for presence of real Lightweight Charts v4, Chart.js v4, Canvas 2D
    uses_lightweight_charts = "LightweightCharts" in charts_js or "createChart" in charts_js
    uses_chartjs = "new Chart(" in charts_js
    uses_canvas2d = "getContext('2d')" in charts_js or 'getContext("2d")' in charts_js

    # Check SSE & WebSocket connections in app.js
    uses_sse = "EventSource" in app_js
    uses_ws = "WebSocket" in app_js

    # Global window functions preserved
    window_hooks = [
        "togglePineScriptModal", "copyPineScript", "copyAIPrompt"
    ]
    hooks_in_app = [h for h in window_hooks if f"window.{h}" in app_js]

    return {
        'app_js_len': len(app_js),
        'charts_js_len': len(charts_js),
        'app_dom_lookups': sorted(list(dom_lookups_app)),
        'charts_dom_lookups': sorted(list(dom_lookups_charts)),
        'chart_funcs': sorted(list(set(chart_funcs))),
        'chart_window_exports': sorted(list(set(chart_window_exports))),
        'uses_lightweight_charts': uses_lightweight_charts,
        'uses_chartjs': uses_chartjs,
        'uses_canvas2d': uses_canvas2d,
        'uses_sse': uses_sse,
        'uses_ws': uses_ws,
        'hooks_in_app': hooks_in_app
    }

def analyze_app_backend():
    app_py_path = r"c:\Users\juanc\Desktop\prueba\app.py"
    with open(app_py_path, "r", encoding="utf-8") as f:
        app_code = f.read()

    # Extract all route decorators
    routes = re.findall(r"@app\.route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[([^\]]+)\])?\)", app_code)
    
    # Check for hardcoded responses or dummy mocks
    has_dummy_returns = bool(re.search(r"return\s+jsonify\(\{'status':\s*'ok'\}\)\s*#\s*mock", app_code))

    return {
        'app_py_len': len(app_code),
        'routes_count': len(routes),
        'routes': routes,
        'has_dummy_returns': has_dummy_returns
    }

def scan_tests_comprehensive():
    tests_dir = r"c:\Users\juanc\Desktop\prueba\tests"
    test_files = [os.path.join(tests_dir, f) for f in os.listdir(tests_dir) if f.endswith(".py")]
    
    suspicious = []
    total_test_functions = 0
    total_assertions_and_checks = 0
    test_file_stats = []

    for tfile in sorted(test_files):
        fname = os.path.basename(tfile)
        with open(tfile, "r", encoding="utf-8") as f:
            content = f.read()
        
        try:
            tree = ast.parse(content, filename=tfile)
        except Exception as e:
            suspicious.append({'file': fname, 'issue': f"AST Parse Error: {e}"})
            continue

        file_tests = 0
        file_asserts = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                total_test_functions += 1
                file_tests += 1
                
                # Check for empty body with pass only
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    suspicious.append({'file': fname, 'test': node.name, 'issue': 'Empty test with pass only'})

                # Find asserts (ast.Assert)
                assert_nodes = [n for n in ast.walk(node) if isinstance(n, ast.Assert)]
                
                # Find calls to self.assert*, np.testing.assert_*, pytest.raises, pytest.fail, pytest.approx
                calls = [n for n in ast.walk(node) if isinstance(n, ast.Call)]
                assert_calls = []
                for c in calls:
                    call_name = ""
                    if isinstance(c.func, ast.Attribute):
                        call_name = c.func.attr
                    elif isinstance(c.func, ast.Name):
                        call_name = c.func.id
                    
                    if (call_name.startswith("assert") or 
                        call_name in ["raises", "fail", "approx", "assert_allclose", "assert_almost_equal", "assert_array_equal", "assert_series_equal", "assert_frame_equal"]):
                        assert_calls.append(call_name)

                num_checks = len(assert_nodes) + len(assert_calls)
                total_assertions_and_checks += num_checks
                file_asserts += num_checks

                # Trivial asserts: assert True, assert 1, self.assertTrue(True)
                for an in assert_nodes:
                    if isinstance(an.test, ast.Constant) and an.test.value in [True, 1]:
                        suspicious.append({'file': fname, 'test': node.name, 'issue': f'Trivial assert: assert {an.test.value}'})
                for c in calls:
                    if isinstance(c.func, ast.Attribute) and c.func.attr in ["assertTrue", "assertEqual"]:
                        if len(c.args) > 0 and isinstance(c.args[0], ast.Constant) and c.args[0].value is True:
                            suspicious.append({'file': fname, 'test': node.name, 'issue': 'Trivial self.assertTrue(True)'})

                if num_checks == 0:
                    # check if the test contains execution of code that would throw exceptions
                    # e.g. loops or calls without explicit assert
                    body_stmts = [type(s).__name__ for s in node.body]
                    suspicious.append({'file': fname, 'test': node.name, 'issue': f'Zero assertions/checks detected. Body: {body_stmts}'})

        test_file_stats.append({
            'file': fname,
            'test_count': file_tests,
            'check_count': file_asserts
        })

    return {
        'test_files_count': len(test_files),
        'total_test_functions': total_test_functions,
        'total_assertions_and_checks': total_assertions_and_checks,
        'suspicious_findings': suspicious,
        'test_file_stats': test_file_stats
    }

if __name__ == "__main__":
    html_info = analyze_html_dom()
    css_info = analyze_css()
    js_info = analyze_js()
    app_info = analyze_app_backend()
    test_info = scan_tests_comprehensive()
    
    full_report = {
        'html': html_info,
        'css': css_info,
        'js': js_info,
        'app_backend': app_info,
        'tests': test_info
    }
    with open(r"c:\Users\juanc\Desktop\prueba\.agents\auditor_m4_final\comprehensive_forensic_scan.json", "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)
    print("Comprehensive scan completed successfully.")
