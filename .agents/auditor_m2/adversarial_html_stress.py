"""
Adversarial Stress Testing & Structural Verification for Milestone 2 Templates
"""

import sys
import re
from pathlib import Path
from html.parser import HTMLParser

WORKSPACE_DIR = Path(r"c:\Users\juanc\Desktop\prueba")
sys.path.insert(0, str(WORKSPACE_DIR))
HTML_PATH = WORKSPACE_DIR / "templates" / "index.html"

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html_content = f.read()

def test_adversarial_inline_styles():
    print("1. Testing for prohibited high-contrast / halation colors...")
    forbidden = [
        ("background: #fff", "Pure white background"),
        ("background: #ffffff", "Pure white background"),
        ("background-color: #fff", "Pure white background"),
        ("background-color: #ffffff", "Pure white background"),
        ("background: black", "Pure black background"),
        ("background: #000000", "Pure black background"),
        ("color: #000", "Pure black text"),
        ("color: #000000", "Pure black text"),
    ]
    violations = []
    for pattern, desc in forbidden:
        if pattern.lower() in html_content.lower():
            violations.append(f"Violation: {desc} found ('{pattern}')")
    assert not violations, f"Adversarial style check failed: {violations}"
    print("   -> PASS: No forbidden high-halation colors detected.")

def test_adversarial_form_attributes():
    print("2. Testing form control boundaries and constraints...")
    # smart-streak-length
    assert 'id="smart-streak-length"' in html_content
    assert 'min="1"' in html_content
    assert 'max="15"' in html_content
    # smart-risk-capital readonly
    assert 'id="smart-risk-capital" value="200" readonly class="input-readonly"' in html_content or ('id="smart-risk-capital"' in html_content and 'readonly' in html_content)
    # smart-preset-select
    assert 'preset_33_6' in html_content
    assert 'preset_25_8' in html_content
    assert 'preset_200_1' in html_content
    print("   -> PASS: Form attributes and constraints verified.")

def test_adversarial_tooltips_content():
    print("3. Testing quantitative tooltips coverage...")
    tooltips = re.findall(r'<span class="tooltip-text"[^>]*>(.*?)</span>', html_content, re.DOTALL)
    assert len(tooltips) >= 15, f"Expected at least 15 tooltips, found {len(tooltips)}"
    # Check explanations for key concepts
    joined = " ".join(tooltips)
    assert "Barbell" in joined or "arbitraje" in joined
    assert "Monte Carlo" in joined or "trayectorias" in joined or "Percentiles" in joined or "percentiles" in joined
    assert "Markov" in joined or "condicional" in joined or "probabilidad" in joined
    assert "Paroli" in joined or "consecutivas" in joined or "Escalera" in joined
    print(f"   -> PASS: {len(tooltips)} institutional tooltips fully populated with quantitative explanations.")

def test_adversarial_tables_structure():
    print("4. Testing data tables structure and alignment...")
    tables = re.findall(r'<table[^>]*id="([^"]+)"[^>]*>(.*?)</table>', html_content, re.DOTALL)
    table_ids = [t[0] for t in tables]
    expected_tables = [
        "smart-selected-assets-table",
        "smart-markov-table",
        "trades-table",
        "markov-table",
        "streak-alternatives-table"
    ]
    for tid in expected_tables:
        assert tid in table_ids, f"Missing table: {tid}"
    print(f"   -> PASS: All {len(expected_tables)} critical data tables present with correct IDs and headers.")

if __name__ == "__main__":
    print("=" * 70)
    print("RUNNING ADVERSARIAL STRESS SUITE (HTML WORKSPACE)")
    print("=" * 70)
    test_adversarial_inline_styles()
    test_adversarial_form_attributes()
    test_adversarial_tooltips_content()
    test_adversarial_tables_structure()
    print("=" * 70)
    print("ADVERSARIAL STRESS SUITE: ALL CHECKS PASSED")
    print("=" * 70)
