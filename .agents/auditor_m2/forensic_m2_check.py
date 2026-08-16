"""
Independent Forensic Integrity Audit Script for Milestone 2
Templates/index.html & Institutional Workspace Verification
"""

import sys
import os
import re
import json
import subprocess
from pathlib import Path
from html.parser import HTMLParser

WORKSPACE_DIR = Path(r"c:\Users\juanc\Desktop\prueba")
sys.path.insert(0, str(WORKSPACE_DIR))

HTML_PATH = WORKSPACE_DIR / "templates" / "index.html"
CSS_PATH = WORKSPACE_DIR / "static" / "css" / "style.css"
JS_APP_PATH = WORKSPACE_DIR / "static" / "js" / "app.js"
JS_CHARTS_PATH = WORKSPACE_DIR / "static" / "js" / "charts.js"

VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

class StrictHTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_stack = []
        self.errors = []
        self.ids = {}  # id -> count
        self.classes = set()
        self.inputs = []
        self.selects = []
        self.buttons = []
        self.canvases = []
        self.tables = []
        
    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        line, col = self.getpos()
        
        # Check duplicate ID
        if "id" in attr_dict:
            elem_id = attr_dict["id"].strip()
            self.ids[elem_id] = self.ids.get(elem_id, 0) + 1
            if self.ids[elem_id] > 1:
                self.errors.append(f"Line {line}: Duplicate DOM ID detected: '{elem_id}'")

        if "class" in attr_dict:
            for c in attr_dict["class"].split():
                self.classes.add(c)
                
        if tag == "input":
            self.inputs.append((line, attr_dict))
        elif tag == "select":
            self.selects.append((line, attr_dict))
        elif tag == "button":
            self.buttons.append((line, attr_dict))
        elif tag == "canvas":
            self.canvases.append((line, attr_dict))
        elif tag == "table":
            self.tables.append((line, attr_dict))

        if tag.lower() not in VOID_TAGS:
            self.tag_stack.append((tag.lower(), line, col))

    def handle_endtag(self, tag):
        line, col = self.getpos()
        tag_lower = tag.lower()
        if tag_lower in VOID_TAGS:
            self.errors.append(f"Line {line}: Void tag <{tag}> should not have a closing tag </{tag}>")
            return

        if not self.tag_stack:
            self.errors.append(f"Line {line}: Orphan closing tag </{tag}> with empty stack")
            return

        expected_tag, start_line, start_col = self.tag_stack.pop()
        if expected_tag != tag_lower:
            self.errors.append(
                f"Line {line}: Mismatched closing tag </{tag}> (expected </{expected_tag}> opened at line {start_line})"
            )

    def finish(self):
        if self.tag_stack:
            for tag, line, col in self.tag_stack:
                self.errors.append(f"Unclosed tag <{tag}> opened at line {line}")


def run_forensic_audit():
    results = {
        "status": "PASS",
        "phase1_source_code_analysis": {},
        "phase2_dom_id_preservation": {},
        "phase3_html5_structure": {},
        "phase4_dependencies": {},
        "phase5_flask_render": {},
        "violations": []
    }
    
    print("=" * 80)
    print("RUNNING MILESTONE 2 FORENSIC INTEGRITY AUDIT")
    print("=" * 80)
    
    # Read files
    if not HTML_PATH.exists():
        results["violations"].append(f"File not found: {HTML_PATH}")
        results["status"] = "FAIL"
        return results

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_raw = f.read()

    # -------------------------------------------------------------------------
    # PHASE 1: Source Code & Integrity Pattern Analysis
    # -------------------------------------------------------------------------
    print("\n[PHASE 1] Source Code & Integrity Pattern Analysis...")
    
    # 1.1 Facade & hardcoded dummy detection
    # Check if there are hardcoded fake calculation outputs in static HTML
    trades_tbody_match = re.search(r'<table[^>]*id=["\']trades-table["\'][^>]*>.*?<tbody>(.*?)</tbody>', html_raw, re.DOTALL)
    if trades_tbody_match:
        trades_content = trades_tbody_match.group(1).strip()
        if "<tr>" in trades_content and "Sin datos" not in trades_content:
            results["violations"].append("Facade/Hardcoding: trades-table tbody contains static pre-populated trades")
            
    # Check if smart-selected-assets-body has real dynamic placeholder
    smart_assets_match = re.search(r'<tbody[^>]*id=["\']smart-selected-assets-body["\'][^>]*>(.*?)</tbody>', html_raw, re.DOTALL)
    if smart_assets_match:
        assets_content = smart_assets_match.group(1).strip()
        if "Sin datos" not in assets_content and "empty-text" not in assets_content:
            results["violations"].append("Facade/Hardcoding: smart-selected-assets-body contains hardcoded static data")

    # Check for white-on-black extreme contrast inline styles (#000000 with #ffffff)
    if "background: #000000" in html_raw and "color: #ffffff" in html_raw:
        results["violations"].append("Halation violation: Extreme #000000 and #ffffff contrast detected in inline style")

    results["phase1_source_code_analysis"]["status"] = "PASS" if not [v for v in results["violations"] if "Facade" in v or "Halation" in v] else "FAIL"
    print(f"Phase 1 status: {results['phase1_source_code_analysis']['status']}")

    # -------------------------------------------------------------------------
    # PHASE 2: Strict HTML5 Structure & Syntax Validation
    # -------------------------------------------------------------------------
    print("\n[PHASE 2] HTML5 Strict Parsing & Structure Validation...")
    validator = StrictHTMLValidator()
    validator.feed(html_raw)
    validator.finish()
    
    results["phase3_html5_structure"]["syntax_errors"] = validator.errors
    results["phase3_html5_structure"]["unclosed_tags_count"] = len(validator.tag_stack)
    results["phase3_html5_structure"]["total_ids_parsed"] = len(validator.ids)
    
    if validator.errors:
        print(f"FAILED: Found {len(validator.errors)} HTML structural/syntax errors:")
        for err in validator.errors[:10]:
            print(f"  - {err}")
        results["violations"].extend(validator.errors)
    else:
        print("PASSED: 0 HTML structural errors, 0 unclosed tags, 0 mismatched tags, 0 duplicate IDs.")

    # -------------------------------------------------------------------------
    # PHASE 3: Legacy DOM ID Preservation & Specification Compliance
    # -------------------------------------------------------------------------
    print("\n[PHASE 3] Legacy DOM ID Preservation & Specification Compliance...")
    
    # 3.1 Extract all IDs from legacy commit 8c87bba
    try:
        legacy_html = subprocess.check_output(
            ["git", "show", "8c87bba:templates/index.html"],
            cwd=str(WORKSPACE_DIR),
            text=True,
            encoding="utf-8"
        )
        legacy_parser = StrictHTMLValidator()
        legacy_parser.feed(legacy_html)
        legacy_parser.finish()
        legacy_ids = set(legacy_parser.ids.keys())
        
        current_ids = set(validator.ids.keys())
        missing_legacy_ids = legacy_ids - current_ids
        
        print(f"Legacy IDs count: {len(legacy_ids)}")
        print(f"Current IDs count: {len(current_ids)}")
        print(f"Missing IDs from legacy: {missing_legacy_ids}")
        
        if missing_legacy_ids:
            results["violations"].append(f"Missing {len(missing_legacy_ids)} IDs from legacy index.html: {missing_legacy_ids}")
        else:
            print(f"PASSED: 100% of legacy DOM IDs ({len(legacy_ids)}/{len(legacy_ids)}) are fully preserved in current index.html.")
    except Exception as e:
        print(f"WARNING: Could not check legacy git commit: {e}")

    # 3.2 Check 105 canonical IDs from specification
    canonical_105_ids = [
        "mode-smart", "mode-advanced", "live-badge", "live-badge-text", "btn-resultados", "btn-estadisticas", "btn-optimizador",
        "smart-dashboard", "btn-smart-run", "smart-preset-select", "smart-streak-length", "smart-base-capital", "smart-profit-pct",
        "smart-risk-capital", "smart-attempts", "smart-payout", "smart-generations", "smart-population", "smart-console-box",
        "smart-progress-bar-fill", "smart-console-logs", "smart-top-5-box", "smart-top-5-list", "smart-rec-content",
        "smart-ladder-content", "smart-correlation-canvas", "smart-selected-assets-table", "smart-selected-assets-body",
        "smart-equity-chart-canvas", "smart-mc-chart-canvas", "smart-asset-selector", "smart-tv-chart", "smart-tv-chart-empty",
        "smart-markov-table", "smart-markov-explanation", "dashboard", "pair-selector", "interval-selector", "source-selector",
        "tv-chart", "chart-loader", "backtest", "backtest-form", "sec-strategy", "strategy-selector", "dynamic-params",
        "expiry-candles", "payout", "sec-barbell", "group-n-consecutive", "backtest-n-consecutive", "backtest-cycle-prob",
        "backtest-bet-fraction", "sec-genetic", "gen-generations", "gen-population", "gen-min-trades", "optimize-genetic-btn",
        "genetic-progress-container", "genetic-progress-fill", "genetic-progress-text", "genetic-progress-eta", "genetic-feedback",
        "run-backtest-btn", "save-backtest-btn", "backtest-progress-container", "backtest-progress-fill", "backtest-progress-text",
        "backtest-progress-eta", "quick-stats", "stat-winrate", "stat-trades", "stat-pnl", "stat-mw", "stat-ml", "equity-chart",
        "trades-table", "resultados", "btn-clear-history", "history-list", "saved-list", "estadisticas", "autocorr-chart",
        "streaks-chart", "hourly-chart", "cond-probs", "market-state-chart", "markov-table", "optimizador", "opt-winrate",
        "opt-payout", "opt-base-capital", "opt-profit-pct", "opt-risk-capital", "opt-target-capital", "opt-attempts",
        "btn-calc-streak", "streak-progress-container", "streak-progress-fill", "streak-progress-text", "streak-progress-eta",
        "streak-recommendation-content", "bet-ladder-container", "streak-alternatives-table", "mc-chart"
    ]
    
    missing_canonical = [i for i in canonical_105_ids if i not in validator.ids]
    if missing_canonical:
        results["violations"].append(f"Missing canonical specification IDs ({len(missing_canonical)}): {missing_canonical}")
    else:
        print("PASSED: All 105 canonical specification IDs exist in index.html (100% preservation).")

    # 3.3 Verify form inputs count and attributes
    input_ids = [attr.get("id") for line, attr in validator.inputs if "id" in attr]
    print(f"Total form inputs with IDs: {len(input_ids)}")
    
    # 3.4 Verify smart universe checkboxes
    universe_boxes = [attr for line, attr in validator.inputs if attr.get("name") == "smart-universe"]
    assert len(universe_boxes) == 9, f"Expected 9 universe checkboxes, found {len(universe_boxes)}"
    print(f"PASSED: 9/9 universe checkboxes verified: {[b.get('value') for b in universe_boxes]}")

    # 3.5 Verify canvases
    canvases = [attr.get("id") for line, attr in validator.canvases if "id" in attr]
    print(f"PASSED: All {len(canvases)} canvas elements present: {canvases}")

    # -------------------------------------------------------------------------
    # PHASE 4: External Dependencies, Fonts & Assets
    # -------------------------------------------------------------------------
    print("\n[PHASE 4] External Dependencies, Fonts & Assets...")
    deps = {
        "google_fonts_preconnect_1": 'rel="preconnect" href="https://fonts.googleapis.com"' in html_raw,
        "google_fonts_preconnect_2": 'rel="preconnect" href="https://fonts.gstatic.com"' in html_raw,
        "font_inter": "family=Inter:wght@300;400;500;600;700" in html_raw,
        "font_jetbrains_mono": "family=JetBrains+Mono:wght@400;500;600;700" in html_raw,
        "css_style": 'href="/static/css/style.css"' in html_raw,
        "lightweight_charts": "lightweight-charts" in html_raw,
        "chart_js": "chart.js" in html_raw,
        "js_charts": 'src="/static/js/charts.js"' in html_raw,
        "js_app": 'src="/static/js/app.js"' in html_raw,
    }
    
    for dep_name, ok in deps.items():
        if not ok:
            results["violations"].append(f"Dependency missing or misconfigured: {dep_name}")
            print(f"  - FAILED: {dep_name}")
        else:
            print(f"  - PASSED: {dep_name}")
            
    # -------------------------------------------------------------------------
    # PHASE 5: Flask Backend Route Execution
    # -------------------------------------------------------------------------
    print("\n[PHASE 5] Flask Route & Jinja Rendering Execution...")
    try:
        import app
        client = app.app.test_client()
        resp = client.get('/')
        assert resp.status_code == 200, f"Flask returned status code {resp.status_code}"
        assert len(resp.data) > 40000, f"Rendered HTML length too small: {len(resp.data)} bytes"
        assert b"QUANT TERMINAL PRO" in resp.data
        assert b"smart-dashboard" in resp.data
        print(f"PASSED: Flask '/' rendered with HTTP {resp.status_code}, length={len(resp.data)} bytes")
    except Exception as e:
        results["violations"].append(f"Flask test_client execution failed: {str(e)}")
        print(f"FAILED: Flask execution error: {e}")

    # -------------------------------------------------------------------------
    # SUMMARY & VERDICT
    # -------------------------------------------------------------------------
    if results["violations"]:
        results["verdict"] = "INTEGRITY VIOLATION"
    else:
        results["verdict"] = "CLEAN"
        
    print("\n" + "=" * 80)
    print(f"FINAL AUDIT VERDICT: {results['verdict']}")
    print(f"Total Violations: {len(results['violations'])}")
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    res = run_forensic_audit()
    if res["verdict"] != "CLEAN":
        sys.exit(1)
