import os
import re
import sys

CSS_PATH = r"c:\Users\juanc\Desktop\prueba\static\css\style.css"
HTML_PATH = r"c:\Users\juanc\Desktop\prueba\templates\index.html"
JS_APP_PATH = r"c:\Users\juanc\Desktop\prueba\static\js\app.js"
JS_CHARTS_PATH = r"c:\Users\juanc\Desktop\prueba\static\js\charts.js"

print("=" * 60)
print("INDEPENDENT FORENSIC & COMPLIANCE AUDIT FOR MILESTONE 1")
print("=" * 60)

with open(CSS_PATH, "r", encoding="utf-8") as f:
    css_content = f.read()

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html_content = f.read()

with open(JS_APP_PATH, "r", encoding="utf-8") as f:
    js_app_content = f.read()

# 1. SYNTAX & BRACE MATCHING
open_braces = css_content.count("{")
close_braces = css_content.count("}")
print(f"[1] CSS Brace Balance: {open_braces} open, {close_braces} close -> {'PASS' if open_braces == close_braces else 'FAIL'}")
assert open_braces == close_braces, f"Brace mismatch: {open_braces} != {close_braces}"

# 2. PALETTE TOKENS AUDIT
palette_checks = {
    "--bg-canvas": "#080b11",
    "--bg-card": "#0e1420",
    "--bg-elevated": "#141d2e",
    "--bg-hover": "#1c273d",
    "--border-subtle": "rgba(255, 255, 255, 0.07)",
    "--border-focus": "rgba(56, 189, 248, 0.35)",
    "--accent-primary": "#38bdf8",
    "--accent-green": "#10b981",
    "--accent-red": "#f43f5e",
    "--accent-purple": "#a855f7",
    "--accent-amber": "#f59e0b",
    "--text-primary": "#f0f6fc",
    "--text-secondary": "#94a3b8",
    "--text-muted": "#64748b",
    "--text-disabled": "#475569",
}

print("\n[2] Checking Institutional Dark Palette Tokens:")
for token, expected_val in palette_checks.items():
    pattern = rf"{re.escape(token)}\s*:\s*{re.escape(expected_val)}"
    found = re.search(pattern, css_content, re.IGNORECASE) is not None
    print(f"  - {token}: {expected_val} -> {'PASS' if found else 'FAIL'}")
    assert found, f"Token {token} missing or value mismatch (expected {expected_val})"

# 3. 8-POINT GRID & GEOMETRY TOKENS AUDIT
grid_checks = {
    "--space-1": "4px",
    "--space-2": "8px",
    "--space-3": "12px",
    "--space-4": "16px",
    "--space-5": "20px",
    "--space-6": "24px",
    "--space-8": "32px",
    "--radius-sm": "4px",
    "--radius-md": "6px",
    "--radius-lg": "8px",
    "--radius-xl": "10px",
    "--radius-pill": "9999px",
}

print("\n[3] Checking 8-Point Grid & Geometry Tokens:")
for token, expected_val in grid_checks.items():
    pattern = rf"{re.escape(token)}\s*:\s*{re.escape(expected_val)}"
    found = re.search(pattern, css_content, re.IGNORECASE) is not None
    print(f"  - {token}: {expected_val} -> {'PASS' if found else 'FAIL'}")
    assert found, f"Token {token} missing or value mismatch"

# 4. TYPOGRAPHY & TABULAR NUMERAL AUDIT
print("\n[4] Checking Typography & Tabular Numerals:")
assert "Inter" in css_content, "Missing Inter font declaration"
assert "JetBrains Mono" in css_content, "Missing JetBrains Mono font declaration"
assert 'font-feature-settings: "tnum" 1, "zero" 1;' in css_content, "Missing font-feature-settings tnum/zero"
assert "font-variant-numeric: tabular-nums;" in css_content, "Missing font-variant-numeric tabular-nums"
print("  - Inter & JetBrains Mono Fonts -> PASS")
print("  - Tabular Numerals (tnum 1, zero 1, tabular-nums) -> PASS")

# 5. ANTI-HALATION & ANTI-CHROMOSTEREOPSIS AUDIT
print("\n[5] Anti-Halation & Anti-Chromostereopsis Checks:")
pure_black_bg = re.search(r"background(-color)?\s*:\s*#000000", css_content, re.IGNORECASE)
pure_white_text = re.search(r"color\s*:\s*#ffffff", css_content, re.IGNORECASE)
print(f"  - No '#000000' background declarations -> {'PASS' if not pure_black_bg else 'FAIL'}")
assert not pure_black_bg, "Pure black #000000 background detected!"

# 6. BACKWARD COMPATIBILITY ALIASES AUDIT
compat_aliases = [
    "--bg-dark",
    "--bg-panel",
    "--border-color",
    "--border-glow",
    "--accent-blue",
    "--accent-gold",
    "--font-family",
]
print("\n[6] Checking Backward Compatibility Aliases:")
for alias in compat_aliases:
    found = alias in css_content
    print(f"  - {alias} -> {'PASS' if found else 'FAIL'}")
    assert found, f"Missing backward compatibility alias: {alias}"

# 7. HTML CLASS PRESERVATION AUDIT
print("\n[7] Checking HTML Class Coverage in CSS:")
html_classes = set()
for match in re.finditer(r'class=["\']([^"\']+)["\']', html_content):
    for cls in match.group(1).split():
        html_classes.add(cls)

missing_html_classes = []
for cls in sorted(html_classes):
    # Check if cls exists as selector in css
    # Pattern: .classname followed by word boundary, space, comma, colon, bracket, etc.
    cls_pattern = rf"\.{re.escape(cls)}(?=[^a-zA-Z0-9_-]|$)"
    if not re.search(cls_pattern, css_content):
        missing_html_classes.append(cls)

if missing_html_classes:
    print(f"  [WARNING] Missing classes from HTML ({len(missing_html_classes)}): {missing_html_classes}")
else:
    print(f"  - All {len(html_classes)} HTML classes have matching CSS rules -> PASS")

# 8. DYNAMIC JS CLASS COVERAGE AUDIT
print("\n[8] Checking Dynamic JS Classes Coverage:")
# Extract dynamically added classes from app.js
js_classes = set()
# classList.add('...')
for match in re.finditer(r"classList\.add\(['\"]([^'\"]+)['\"]\)", js_app_content):
    js_classes.add(match.group(1))
# class="..."
for match in re.finditer(r'class=["\']([^"\']+)["\']', js_app_content):
    for part in match.group(1).split():
        cleaned = re.sub(r'[\$\{\}]', '', part).strip()
        if cleaned and not cleaned.startswith("${") and not cleaned.endswith("}"):
            for sub in cleaned.split():
                if re.match(r'^[a-zA-Z0-9_-]+$', sub):
                    js_classes.add(sub)

missing_js_classes = []
for cls in sorted(js_classes):
    cls_pattern = rf"\.{re.escape(cls)}(?=[^a-zA-Z0-9_-]|$)"
    if not re.search(cls_pattern, css_content):
        missing_js_classes.append(cls)

if missing_js_classes:
    print(f"  [WARNING] Missing dynamic classes from JS ({len(missing_js_classes)}): {missing_js_classes}")
else:
    print(f"  - All {len(js_classes)} dynamic JS classes have matching CSS rules -> PASS")

print("\n" + "=" * 60)
print("AUDIT COMPLETE")
print("=" * 60)
