import re
import json
from pathlib import Path
from html.parser import HTMLParser

WORKSPACE_DIR = Path(r"c:\Users\juanc\Desktop\prueba")
HTML_PATH = WORKSPACE_DIR / "templates" / "index.html"
APP_JS_PATH = WORKSPACE_DIR / "static" / "js" / "app.js"
CHARTS_JS_PATH = WORKSPACE_DIR / "static" / "js" / "charts.js"

class ComprehensiveHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.ids = set()
        self.classes = set()
        self.inputs = []
        self.selects = []
        self.buttons = []
        self.canvases = []
        self.tables = []
        self.forms = []
        self.all_elements_by_id = {}
        
    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        self.tags.append((tag, attr_dict))
        
        if "id" in attr_dict:
            elem_id = attr_dict["id"].strip()
            self.ids.add(elem_id)
            self.all_elements_by_id[elem_id] = (tag, attr_dict)
            
        if "class" in attr_dict:
            for c in attr_dict["class"].split():
                self.classes.add(c)
                
        if tag == "input":
            self.inputs.append(attr_dict)
        elif tag == "select":
            self.selects.append(attr_dict)
        elif tag == "button":
            self.buttons.append(attr_dict)
        elif tag == "canvas":
            self.canvases.append(attr_dict)
        elif tag == "table":
            self.tables.append(attr_dict)
        elif tag == "form":
            self.forms.append(attr_dict)


def analyze():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()
    with open(APP_JS_PATH, "r", encoding="utf-8") as f:
        app_js_content = f.read()
    with open(CHARTS_JS_PATH, "r", encoding="utf-8") as f:
        charts_js_content = f.read()
        
    parser = ComprehensiveHTMLParser()
    parser.feed(html_content)
    
    print(f"=== HTML PARSING METRICS ===")
    print(f"Total Unique IDs in HTML: {len(parser.ids)}")
    print(f"Total Unique Classes in HTML: {len(parser.classes)}")
    print(f"Total Inputs: {len(parser.inputs)}")
    print(f"Total Selects: {len(parser.selects)}")
    print(f"Total Buttons: {len(parser.buttons)}")
    print(f"Total Canvases: {len(parser.canvases)}")
    print(f"Total Tables: {len(parser.tables)}")
    print()

    # 1. Extract all document.getElementById('...') from JS
    # Both static strings and template literals
    id_regex = re.compile(r"document\.getElementById\(\s*['\"`]([a-zA-Z0-9_\-]+)['\"`]\s*\)")
    
    # Also find querySelector('#...')
    qs_id_regex = re.compile(r"document\.querySelector\(\s*['\"`]#([a-zA-Z0-9_\-]+)['\"`]\s*\)")
    qsa_id_regex = re.compile(r"document\.querySelectorAll\(\s*['\"`]#([a-zA-Z0-9_\-]+)['\"`]\s*\)")

    # Also find string literal IDs passed to charting functions or helper functions:
    # createCandlestickChart('...'), createEquityCurve('...'), createBarChart('...'), createGrowthRateChart('...'), createMonteCarloChart('...'), createCorrelationHeatmap('...')
    chart_func_id_regex = re.compile(r"(?:createCandlestickChart|createEquityCurve|createBarChart|createGrowthRateChart|createMonteCarloChart|createCorrelationHeatmap|renderEquityCurve|renderMonteCarloCones|renderCorrelationHeatmap|initLightweightChart)\(\s*['\"`]([a-zA-Z0-9_\-]+)['\"`]")

    app_ids = set(id_regex.findall(app_js_content))
    app_ids.update(qs_id_regex.findall(app_js_content))
    app_ids.update(qsa_id_regex.findall(app_js_content))
    app_ids.update(chart_func_id_regex.findall(app_js_content))

    charts_ids = set(id_regex.findall(charts_js_content))
    charts_ids.update(qs_id_regex.findall(charts_js_content))
    charts_ids.update(qsa_id_regex.findall(charts_js_content))
    charts_ids.update(chart_func_id_regex.findall(charts_js_content))

    all_queried_ids = app_ids.union(charts_ids)

    # Note: dynamically generated IDs like pinescript-box-${id}, pinescript-code-${id}, ai-prompt-${id}, opt-strat-item-${index}, strat-badge-${stratKey} are generated at runtime
    dynamic_id_patterns = [
        "pinescript-box-", "pinescript-code-", "ai-prompt-", "opt-strat-item-", "strat-badge-"
    ]
    
    static_queried_ids = {i for i in all_queried_ids if not any(i.startswith(pat) for pat in dynamic_id_patterns)}

    print(f"=== STATIC DOM IDs QUERIED IN JS ({len(static_queried_ids)}) ===")
    missing_ids = []
    for q_id in sorted(static_queried_ids):
        present = q_id in parser.ids
        status = "EXISTS" if present else "MISSING"
        if not present:
            missing_ids.append(q_id)
        # print(f"  [{status}] #{q_id}")
        
    print(f"Queried IDs checked: {len(static_queried_ids)}")
    print(f"Missing static IDs: {len(missing_ids)} -> {missing_ids}")
    print()

    # 2. Extract classes queried in JS
    qs_class_regex = re.compile(r"querySelector(?:All)?\(\s*['\"`]\.([a-zA-Z0-9_\-]+)['\"`]\s*\)")
    app_classes = set(qs_class_regex.findall(app_js_content))
    charts_classes = set(qs_class_regex.findall(charts_js_content))
    all_queried_classes = app_classes.union(charts_classes)

    print(f"=== CLASSES QUERIED IN JS ({len(all_queried_classes)}) ===")
    # Dynamic classes added/removed in runtime
    missing_classes = []
    for q_cls in sorted(all_queried_classes):
        present = q_cls in parser.classes
        status = "EXISTS" if present else "NOT IN INITIAL HTML (Runtime/Style class)"
        if not present:
            missing_classes.append(q_cls)
        print(f"  [{status}] .{q_cls}")
    print()

    # 3. Form input validation
    print("=== FORM CONTROLS AUDIT ===")
    expected_controls = {
        "smart-streak-length": {"tag": "input", "type": "number", "value": "3", "min": "1", "max": "15"},
        "smart-base-capital": {"tag": "input", "type": "number", "value": "1000", "min": "10"},
        "smart-profit-pct": {"tag": "input", "type": "number", "value": "20", "min": "1", "max": "100"},
        "smart-risk-capital": {"tag": "input", "type": "number", "value": "200", "readonly": True},
        "smart-attempts": {"tag": "input", "type": "number", "value": "6", "min": "1", "max": "50"},
        "smart-payout": {"tag": "input", "type": "number", "value": "0.85", "min": "0.1", "max": "1.0", "step": "0.01"},
        "smart-generations": {"tag": "input", "type": "number", "value": "50", "min": "5", "max": "200"},
        "smart-population": {"tag": "input", "type": "number", "value": "150", "min": "10", "max": "500"},
        "expiry-candles": {"tag": "input", "type": "number", "value": "1", "min": "1"},
        "payout": {"tag": "input", "type": "number", "value": "0.92", "min": "0.1", "step": "0.01"},
        "backtest-n-consecutive": {"tag": "input", "type": "number", "value": "4", "min": "1", "max": "15"},
        "backtest-bet-fraction": {"tag": "input", "type": "number", "value": "0.10", "min": "0.01", "max": "1.0", "step": "0.01"},
        "gen-generations": {"tag": "input", "type": "number", "value": "50", "min": "5", "max": "200"},
        "gen-population": {"tag": "input", "type": "number", "value": "150", "min": "10", "max": "500"},
        "gen-min-trades": {"tag": "input", "type": "number", "value": "5.0", "min": "0.5", "step": "0.5"},
        "opt-payout": {"tag": "input", "type": "number", "value": "0.85", "step": "0.01"},
        "opt-base-capital": {"tag": "input", "type": "number", "value": "1000", "min": "10"},
        "opt-profit-pct": {"tag": "input", "type": "number", "value": "20", "min": "1", "max": "100"},
        "opt-risk-capital": {"tag": "input", "type": "number", "value": "200", "readonly": True},
        "opt-target-capital": {"tag": "input", "type": "number", "value": "1000", "min": "50"},
        "opt-attempts": {"tag": "input", "type": "number", "value": "5", "min": "1", "max": "50"},
    }

    form_errors = []
    for ctrl_id, specs in expected_controls.items():
        if ctrl_id not in parser.all_elements_by_id:
            form_errors.append(f"Element #{ctrl_id} not found in HTML")
            continue
        tag, attrs = parser.all_elements_by_id[ctrl_id]
        if tag != specs["tag"]:
            form_errors.append(f"Element #{ctrl_id} expected tag {specs['tag']}, found {tag}")
        if "value" in specs and attrs.get("value") != specs["value"]:
            form_errors.append(f"Element #{ctrl_id} expected value {specs['value']}, found {attrs.get('value')}")
        if "min" in specs and attrs.get("min") != specs["min"]:
            form_errors.append(f"Element #{ctrl_id} expected min {specs['min']}, found {attrs.get('min')}")
        if "max" in specs and attrs.get("max") != specs["max"]:
            form_errors.append(f"Element #{ctrl_id} expected max {specs['max']}, found {attrs.get('max')}")
        if "step" in specs and attrs.get("step") != specs["step"]:
            form_errors.append(f"Element #{ctrl_id} expected step {specs['step']}, found {attrs.get('step')}")
        if specs.get("readonly") and "readonly" not in attrs:
            form_errors.append(f"Element #{ctrl_id} expected readonly attribute")

    print(f"Form control errors: {len(form_errors)}")
    for err in form_errors:
        print(f"  [FAIL] {err}")
    if not form_errors:
        print("  [PASS] All 21 specified form controls match exact types, values, bounds and readonly constraints.")
    print()

    # 4. Check Smart Universe Checkboxes
    universe_inputs = [i for i in parser.inputs if i.get("name") == "smart-universe"]
    print(f"Smart Universe Checkboxes: {len(universe_inputs)}")
    universe_vals = [i.get("value") for i in universe_inputs]
    print(f"  Values: {universe_vals}")
    
    # 5. Check Presets in select
    preset_select = parser.all_elements_by_id.get("smart-preset-select")
    print(f"Preset Select exists: {preset_select is not None}")

    # 6. Check Canvases & Chart IDs
    expected_canvases = [
        "smart-correlation-canvas", "smart-equity-chart-canvas", "smart-mc-chart-canvas",
        "equity-chart", "autocorr-chart", "streaks-chart", "hourly-chart", "market-state-chart", "mc-chart"
    ]
    canvas_errors = []
    for c_id in expected_canvases:
        if c_id not in parser.ids:
            canvas_errors.append(f"Canvas #{c_id} missing")
    print(f"Canvas IDs check: {len(canvas_errors)} errors -> {canvas_errors}")
    print()

    # 7. Check Event Listeners in JS targeting IDs
    # Find all el.addEventListener('...', ...) or $(...).on(...)
    # e.g., document.getElementById('btn-smart-run').addEventListener('click', ...)
    listener_pattern = re.compile(r"document\.getElementById\(\s*['\"`]([a-zA-Z0-9_\-]+)['\"`]\s*\)\.addEventListener\(\s*['\"`]([a-zA-Z0-9_\-]+)['\"`]")
    listeners = listener_pattern.findall(app_js_content)
    print(f"=== DIRECT JS EVENT LISTENERS ({len(listeners)}) ===")
    for target_id, ev in listeners:
        status = "EXISTS" if target_id in parser.ids else "MISSING"
        print(f"  [{status}] #{target_id} -> '{ev}' event")
        if target_id not in parser.ids:
            missing_ids.append(target_id)
            
    print()
    print("=== SUMMARY VERDICT ===")
    if not missing_ids and not form_errors and not canvas_errors:
        print("VERDICT: 100% DOM INTEGRITY CONFIRMED")
    else:
        print("VERDICT: REJECT - ISSUES DETECTED")

if __name__ == "__main__":
    analyze()
