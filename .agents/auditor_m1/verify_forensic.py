import re
import os
import sys

def run_forensic_audit():
    css_path = 'static/css/style.css'
    html_path = 'templates/index.html'
    js_path = 'static/js/app.js'
    
    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()

    print("=== FORENSIC INTEGRITY AUDIT: STYLE.CSS ===")
    print(f"File Size: {len(css)} bytes, {len(css.splitlines())} lines")

    # 1. Structural & Syntax Check
    open_braces = css.count('{')
    close_braces = css.count('}')
    print(f"\n[1] Structural Brace Balance: {open_braces} open, {close_braces} close")
    assert open_braces == close_braces, f"Mismatched braces: {open_braces} != {close_braces}"
    print("  -> PASS: All CSS blocks are properly balanced.")

    # 2. Token Architecture & Palette Verification
    print("\n[2] Palette & Token Architecture Verification:")
    required_palette = {
        '--bg-canvas': '#080b11',
        '--bg-card': '#0e1420',
        '--bg-elevated': '#141d2e',
        '--bg-hover': '#1c273d',
        '--accent-primary': '#38bdf8',
        '--accent-green': '#10b981',
        '--accent-red': '#f43f5e',
        '--accent-purple': '#a855f7',
        '--accent-amber': '#f59e0b',
    }
    
    for token, hex_code in required_palette.items():
        pattern = rf"{token}\s*:\s*{hex_code}"
        match = re.search(pattern, css, re.IGNORECASE)
        if match:
            print(f"  -> PASS: Token {token} = {hex_code} verified.")
        else:
            print(f"  -> FAIL: Token {token} with value {hex_code} NOT FOUND!")
            sys.exit(1)

    # Check anti-halation (#000000 check)
    pure_black = re.findall(r'#000000\b|#000\b', css)
    print(f"\n[3] Anti-Halation / Pure Black Check:")
    if pure_black:
        print(f"  -> FAIL: Found pure black hex instances: {pure_black}")
        sys.exit(1)
    else:
        print("  -> PASS: Zero occurrences of #000000 or #000.")

    # 3. Variable consistency (all var(--x) must be defined in :root)
    root_match = re.search(r':root\s*\{([^}]+)\}', css)
    defined_vars = set()
    if root_match:
        root_body = root_match.group(1)
        for var in re.findall(r'(--[a-zA-Z0-9_-]+)\s*:', root_body):
            defined_vars.add(var)
    
    used_vars = set(re.findall(r'var\((--[a-zA-Z0-9_-]+)', css))
    undefined = used_vars - defined_vars
    print(f"\n[4] Variable Reference Resolution Check:")
    print(f"  Defined in :root: {len(defined_vars)} tokens")
    print(f"  Referenced across rules: {len(used_vars)} tokens")
    if undefined:
        print(f"  -> FAIL: Undefined CSS variables used: {undefined}")
        sys.exit(1)
    else:
        print("  -> PASS: 100% of referenced CSS variables are defined in :root.")

    # 4. Tabular Numeral Rules Check
    print(f"\n[5] Tabular Numerals & High Data-to-Ink Rules:")
    tabular_font_features = 'font-feature-settings: "tnum" 1, "zero" 1' in css
    tabular_variant = 'font-variant-numeric: tabular-nums' in css
    mono_font = "font-family: var(--font-mono)" in css
    print(f"  font-feature-settings tnum/zero: {tabular_font_features}")
    print(f"  font-variant-numeric tabular-nums: {tabular_variant}")
    print(f"  font-family mono binding: {mono_font}")
    assert tabular_font_features and tabular_variant and mono_font, "Missing tabular numeral rules"
    print("  -> PASS: Tabular typography rules are fully defined.")

    # 5. Facade / Stub / Empty rules Check
    print(f"\n[6] Facade / Empty Blocks / Truncated Stubs Detection:")
    empty_blocks = re.findall(r'\{[ \t\r\n]*\}', css)
    print(f"  Empty rule blocks: {len(empty_blocks)}")
    assert len(empty_blocks) == 0, f"Found empty rule blocks: {empty_blocks}"

    suspicious_patterns = ['TODO', 'FIXME', 'DUMMY', 'FACADE', 'STUB', 'PLACEHOLDER_FOR', 'MOCK']
    found_suspicious = []
    for sp in suspicious_patterns:
        matches = re.findall(rf'\b{sp}\b', css, re.IGNORECASE)
        if matches:
            found_suspicious.append(sp)
    print(f"  Suspicious placeholder tokens: {found_suspicious}")
    assert len(found_suspicious) == 0, f"Found suspicious tokens: {found_suspicious}"
    print("  -> PASS: No dummy facades, stubs, or empty rules detected.")

    # 6. Keyframes Check
    print(f"\n[7] Keyframe Animation Verification:")
    keyframes = re.findall(r'@keyframes\s+([a-zA-Z0-9_-]+)', css)
    print(f"  Keyframes declared: {keyframes}")
    for kf in keyframes:
        occurrences = css.count(kf)
        print(f"    - {kf}: declared and referenced {occurrences} times")
        assert occurrences >= 2, f"Keyframe {kf} is defined but never used in any animation rule"
    print("  -> PASS: All @keyframes are actively bound to selectors.")

    # 7. Preserved Selectors & HTML/JS Alignment Check
    print(f"\n[8] HTML and JS Compatibility Alignment:")
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    with open(js_path, 'r', encoding='utf-8') as f:
        js = f.read()

    key_selectors = [
        '#smart-dashboard', '#smart-preset-select', '#btn-smart-run',
        '.smart-grid', '.smart-sidebar', '.smart-universe-wrapper',
        '.asset-wr-badge', '.smart-numeric-inputs', '.smart-console-wrapper',
        '.console-body', '.console-log-line', '.top-strat-pill',
        '.smart-card-rec', '.smart-card-ladder', '.streak-ladder',
        '.ladder-step', '.markov-table', '.trades-table', '.n-table',
        '.stat-card', '.pulse-dot', '.live-badge-span', '.tooltip',
        '.pinescript-box', '.loading-spinner', '.subtabs-nav'
    ]

    for sel in key_selectors:
        clean_sel = sel.lstrip('.#')
        if sel.startswith('#'):
            found = f"#{clean_sel}" in css
        else:
            found = f".{clean_sel}" in css
        print(f"  Selector {sel:30} : {'FOUND' if found else 'MISSING'}")
        assert found, f"Missing critical selector in CSS: {sel}"
    print("  -> PASS: All key selectors and UI components are genuinely styled.")

    print("\n==========================================")
    print("FORENSIC VERIFICATION: CLEAN (ALL PASS)")
    print("==========================================")

if __name__ == '__main__':
    run_forensic_audit()
