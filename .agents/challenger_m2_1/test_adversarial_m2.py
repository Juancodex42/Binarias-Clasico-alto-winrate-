"""
Adversarial Verification and Stress Testing Suite for Milestone 2.
Empirically challenges DOM contracts, selector queries, form attributes, event bindings, and runtime safety.
"""

import re
import pytest
from pathlib import Path
from html.parser import HTMLParser

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
HTML_PATH = WORKSPACE_DIR / "templates" / "index.html"
CSS_PATH = WORKSPACE_DIR / "static" / "css" / "style.css"
APP_JS_PATH = WORKSPACE_DIR / "static" / "js" / "app.js"
CHARTS_JS_PATH = WORKSPACE_DIR / "static" / "js" / "charts.js"


class DOMParser(HTMLParser):
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
        self.elements_by_id = {}
        self.classes_by_id = {}

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        self.tags.append((tag, attr_dict))
        
        elem_id = attr_dict.get("id", "").strip()
        if elem_id:
            self.ids.add(elem_id)
            self.elements_by_id[elem_id] = (tag, attr_dict)
            
        elem_classes = attr_dict.get("class", "").split()
        for c in elem_classes:
            self.classes.add(c)
        if elem_id:
            self.classes_by_id[elem_id] = elem_classes

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


@pytest.fixture(scope="module")
def html_content():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture(scope="module")
def app_js():
    with open(APP_JS_PATH, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture(scope="module")
def charts_js():
    with open(CHARTS_JS_PATH, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture(scope="module")
def css_content():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        return f.read()

@pytest.fixture(scope="module")
def dom(html_content):
    p = DOMParser()
    p.feed(html_content)
    return p


# =========================================================================
# 1. CONTRACT VERIFICATION (PROJECT.md)
# =========================================================================

CONTRACT_IDS = [
    # Header & Modes
    "mode-smart", "mode-advanced", "live-badge", "live-badge-text", "btn-resultados", "btn-estadisticas", "btn-optimizador",
    # Smart Mode Controls
    "smart-preset-select", "smart-streak-length", "smart-base-capital", "smart-profit-pct", "smart-risk-capital",
    "smart-attempts", "smart-payout", "smart-generations", "smart-population", "btn-smart-run",
    # Smart Mode Telemetry & Output
    "smart-console-box", "smart-progress-bar-fill", "smart-console-logs", "smart-top-5-box", "smart-top-5-list",
    "smart-rec-content", "smart-ladder-content", "smart-selected-assets-table", "smart-selected-assets-body",
    "smart-markov-table", "smart-markov-explanation", "smart-asset-selector", "smart-tv-chart", "smart-tv-chart-empty",
    "smart-equity-chart-canvas", "smart-mc-chart-canvas", "smart-correlation-canvas", "smart-dashboard",
    # Advanced Mode Controls & Panels
    "dashboard", "pair-selector", "interval-selector", "source-selector", "tv-chart", "chart-loader",
    "backtest", "backtest-form", "run-backtest-btn", "save-backtest-btn", "sec-strategy", "strategy-selector",
    "dynamic-params", "expiry-candles", "payout", "sec-barbell", "group-n-consecutive", "backtest-n-consecutive",
    "backtest-cycle-prob", "backtest-bet-fraction", "sec-genetic", "optimize-genetic-btn", "gen-generations",
    "gen-population", "gen-min-trades", "genetic-progress-container", "genetic-progress-fill", "genetic-progress-text",
    "genetic-progress-eta", "genetic-feedback", "backtest-progress-container", "backtest-progress-fill",
    "backtest-progress-text", "backtest-progress-eta", "quick-stats", "stat-winrate", "stat-trades", "stat-pnl",
    "stat-mw", "stat-ml", "equity-chart", "trades-table", "resultados", "btn-clear-history", "history-list",
    "saved-list", "estadisticas", "autocorr-chart", "streaks-chart", "hourly-chart", "cond-probs", "market-state-chart",
    "markov-table", "optimizador", "opt-winrate", "opt-payout", "opt-base-capital", "opt-profit-pct", "opt-risk-capital",
    "opt-target-capital", "opt-attempts", "btn-calc-streak", "streak-progress-container", "streak-progress-fill",
    "streak-progress-text", "streak-progress-eta", "streak-recommendation-content", "bet-ladder-container",
    "streak-alternatives-table", "mc-chart"
]

def test_all_contract_ids_exist(dom):
    missing = [cid for cid in CONTRACT_IDS if cid not in dom.ids]
    assert not missing, f"Missing {len(missing)} interface contract DOM IDs: {missing}"


# =========================================================================
# 2. ADVERSARIAL JS QUERY & NULL-SAFETY ANALYSIS
# =========================================================================

def test_js_direct_queries_exist_or_null_guarded(app_js, charts_js, dom):
    """
    Every getElementById or querySelector in app.js and charts.js MUST either:
    1. Exist directly in index.html, OR
    2. Be explicitly null-guarded (if (el) ...), OR
    3. Be a dynamically generated element created by app.js (e.g. pinescript modals, ranking pills, dynamic inputs).
    """
    dynamic_prefixes = ("pinescript-", "ai-prompt-", "opt-strat-", "strat-badge-", "param-", "chart-")

    # Find all document.getElementById('X') calls in app.js
    pattern = re.compile(r"document\.getElementById\(\s*['\"`]([a-zA-Z0-9_\-]+)['\"`]\s*\)")
    
    app_matches = pattern.findall(app_js)
    charts_matches = pattern.findall(charts_js)

    all_queried = set(app_matches + charts_matches)

    ungarded_missing = []

    for elem_id in all_queried:
        if elem_id in dom.ids:
            continue
        if any(elem_id.startswith(p) for p in dynamic_prefixes):
            continue
        
        # Check if it is null guarded in app.js / charts.js
        # Find occurrences in code
        for file_content, fname in [(app_js, "app.js"), (charts_js, "charts.js")]:
            for line in file_content.splitlines():
                if f"'{elem_id}'" in line or f'"{elem_id}"' in line or f"`{elem_id}`" in line:
                    # Check if line immediately chains or has no guard
                    if f"document.getElementById('{elem_id}')." in line or f'document.getElementById("{elem_id}").' in line:
                        ungarded_missing.append((fname, elem_id, line.strip()))

    assert not ungarded_missing, f"Found ungarded getElementById calls on missing IDs: {ungarded_missing}"


# =========================================================================
# 3. FORM CONTROLS ADVERSARIAL STRESS TESTING
# =========================================================================

class TestFormControlsAdversarial:
    def test_smart_numeric_inputs_complete_spec(self, dom):
        controls = {
            "smart-streak-length": {"type": "number", "value": "3", "min": "1", "max": "15"},
            "smart-base-capital": {"type": "number", "value": "1000", "min": "10"},
            "smart-profit-pct": {"type": "number", "value": "20", "min": "1", "max": "100"},
            "smart-risk-capital": {"type": "number", "value": "200", "readonly": True},
            "smart-attempts": {"type": "number", "value": "6", "min": "1", "max": "50"},
            "smart-payout": {"type": "number", "value": "0.85", "min": "0.1", "max": "1.0", "step": "0.01"},
            "smart-generations": {"type": "number", "value": "50", "min": "5", "max": "200"},
            "smart-population": {"type": "number", "value": "150", "min": "10", "max": "500"},
        }
        for cid, spec in controls.items():
            assert cid in dom.elements_by_id, f"Missing input #{cid}"
            tag, attrs = dom.elements_by_id[cid]
            assert tag == "input"
            assert attrs.get("type", "text") == spec["type"]
            assert attrs.get("value") == spec["value"]
            if "min" in spec:
                assert attrs.get("min") == spec["min"]
            if "max" in spec:
                assert attrs.get("max") == spec["max"]
            if "step" in spec:
                assert attrs.get("step") == spec["step"]
            if spec.get("readonly"):
                assert "readonly" in attrs

    def test_advanced_backtest_form_controls(self, dom):
        controls = {
            "expiry-candles": {"value": "1", "min": "1"},
            "payout": {"value": "0.92", "min": "0.1", "step": "0.01"},
            "backtest-n-consecutive": {"value": "4", "min": "1", "max": "15"},
            "backtest-bet-fraction": {"value": "0.10", "min": "0.01", "max": "1.0", "step": "0.01"},
            "gen-generations": {"value": "50", "min": "5", "max": "200"},
            "gen-population": {"value": "150", "min": "10", "max": "500"},
            "gen-min-trades": {"value": "5.0", "min": "0.5", "step": "0.5"},
        }
        for cid, spec in controls.items():
            assert cid in dom.elements_by_id, f"Missing input #{cid}"
            tag, attrs = dom.elements_by_id[cid]
            assert attrs.get("value") == spec["value"]
            if "min" in spec:
                assert attrs.get("min") == spec["min"]
            if "max" in spec:
                assert attrs.get("max") == spec["max"]
            if "step" in spec:
                assert attrs.get("step") == spec["step"]

    def test_optimizer_form_controls(self, dom):
        controls = {
            "opt-payout": {"value": "0.85", "step": "0.01"},
            "opt-base-capital": {"value": "1000", "min": "10"},
            "opt-profit-pct": {"value": "20", "min": "1", "max": "100"},
            "opt-risk-capital": {"value": "200", "readonly": True},
            "opt-target-capital": {"value": "1000", "min": "50"},
            "opt-attempts": {"value": "5", "min": "1", "max": "50"},
        }
        for cid, spec in controls.items():
            assert cid in dom.elements_by_id, f"Missing input #{cid}"
            tag, attrs = dom.elements_by_id[cid]
            assert attrs.get("value") == spec["value"]
            if "min" in spec:
                assert attrs.get("min") == spec["min"]
            if "max" in spec:
                assert attrs.get("max") == spec["max"]
            if "step" in spec:
                assert attrs.get("step") == spec["step"]
            if spec.get("readonly"):
                assert "readonly" in attrs


# =========================================================================
# 4. BUTTONS & INTERACTION BINDINGS
# =========================================================================

class TestInteractiveElements:
    def test_run_backtest_button_form_binding(self, dom):
        tag, attrs = dom.elements_by_id["run-backtest-btn"]
        assert tag == "button"
        assert attrs.get("type") == "submit"
        assert attrs.get("form") == "backtest-form"

    def test_save_backtest_button_state(self, dom):
        tag, attrs = dom.elements_by_id["save-backtest-btn"]
        assert tag == "button"
        assert attrs.get("type") == "button"
        assert "disabled" in attrs

    def test_calc_streak_button_type(self, dom):
        tag, attrs = dom.elements_by_id["btn-calc-streak"]
        assert tag == "button"

    def test_clear_history_button_type(self, dom):
        tag, attrs = dom.elements_by_id["btn-clear-history"]
        assert tag == "button"
        assert attrs.get("type") == "button"

    def test_subtab_navigation_buttons(self, dom):
        subtabs = [b for b in dom.buttons if "data-subtab" in b]
        assert len(subtabs) == 3
        subtab_targets = [b["data-subtab"] for b in subtabs]
        assert "sec-strategy" in subtab_targets
        assert "sec-barbell" in subtab_targets
        assert "sec-genetic" in subtab_targets
        for target in subtab_targets:
            assert target in dom.ids, f"Subtab target pane #{target} missing in DOM"


# =========================================================================
# 5. SEMANTIC & ACCESSIBILITY ATTRIBUTES
# =========================================================================

def test_labels_have_matching_for_attributes(dom):
    """Verify that form labels accurately point to existing element IDs."""
    label_for_pattern = re.compile(r'<label\s+[^>]*for=["\']([^"\']+)["\']', re.IGNORECASE)
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    
    label_fors = label_for_pattern.findall(html)
    assert len(label_fors) >= 15
    for target_id in label_fors:
        assert target_id in dom.ids, f"Label for='{target_id}' does not match any element ID in index.html"
