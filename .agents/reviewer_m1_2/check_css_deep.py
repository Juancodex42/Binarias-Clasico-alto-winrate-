import re
import sys

def analyze_css():
    with open('static/css/style.css', 'r', encoding='utf-8') as f:
        css = f.read()

    results = {}
    
    # 1. Check balanced braces
    open_b = css.count('{')
    close_b = css.count('}')
    results['braces_balanced'] = (open_b == close_b, f"open: {open_b}, close: {close_b}")
    
    # 2. Check tokens in :root
    root_match = re.search(r':root\s*\{([^}]+)\}', css, re.DOTALL)
    root_content = root_match.group(1) if root_match else ""
    tokens = [
        '--bg-canvas', '--bg-card', '--bg-elevated', '--bg-hover', '--bg-overlay',
        '--border-subtle', '--border-focus', '--border-active', '--focus-ring',
        '--text-primary', '--text-secondary', '--text-muted', '--text-disabled',
        '--accent-primary', '--accent-green', '--accent-red', '--accent-purple', '--accent-amber', '--accent-slate',
        '--space-1', '--space-2', '--space-3', '--space-4', '--space-5', '--space-6', '--space-8',
        '--radius-sm', '--radius-md', '--radius-lg', '--radius-xl', '--radius-pill',
        '--font-sans', '--font-mono',
        '--ease-out-expo', '--duration-micro', '--duration-state', '--duration-reveal'
    ]
    missing_tokens = [t for t in tokens if t not in root_content]
    results['tokens'] = (len(missing_tokens) == 0, f"Missing: {missing_tokens}")
    
    # 3. Check requested component classes
    required_classes = [
        '.glass-card', '.btn-primary', '.btn-secondary', '.pulse-dot',
        '.smart-progress-bar-fill', '.console-body', '.ladder-step',
        '.top-strat-pill', '.markov-table', '.trades-table', '.n-table'
    ]
    missing_classes = [c for c in required_classes if c not in css]
    results['required_classes'] = (len(missing_classes) == 0, f"Missing: {missing_classes}")
    
    # Check mode switcher classes
    results['mode_switcher'] = (
        ('.mode-switch-container' in css or '.mode-switcher' in css) and '.mode-btn' in css,
        f".mode-switch-container in css: {'.mode-switch-container' in css}, .mode-btn in css: {'.mode-btn' in css}, .mode-switcher in css: {'.mode-switcher' in css}"
    )
    
    # Check status pill / badges
    results['status_pill'] = (
        '.status-pill' in css or '.live-badge-span' in css or '.asset-wr-badge' in css or '--radius-pill' in css,
        f".status-pill: {'.status-pill' in css}, .live-badge-span: {'.live-badge-span' in css}, .asset-wr-badge: {'.asset-wr-badge' in css}"
    )

    # 4. Tabular nums rule
    has_tnum = 'font-variant-numeric: tabular-nums' in css and 'font-feature-settings: "tnum" 1, "zero" 1' in css
    results['tabular_nums'] = (has_tnum, "Checked font-variant-numeric and font-feature-settings")

    # 5. Right alignment on table numbers
    align_match = re.search(r'(td\.num|th\.num|\.trades-table|\.n-table)[^{]*\{[^}]*text-align:\s*right', css, re.DOTALL)
    results['numeric_right_align'] = (align_match is not None, "Right alignment CSS rule found")

    # 6. Shimmer animation
    has_shimmer = '@keyframes progressShimmer' in css and 'animation: progressShimmer' in css
    results['shimmer_animation'] = (has_shimmer, "Shimmer animation found")

    # 7. Pulse animation
    has_pulse = '@keyframes livePulse' in css and 'animation: livePulse' in css
    results['pulse_animation'] = (has_pulse, "Live pulse animation found")

    # 8. Responsive breakpoints
    has_1200 = '@media (max-width: 1200px)' in css
    has_900 = '@media (max-width: 900px)' in css
    has_600 = '@media (max-width: 600px)' in css
    results['responsive_breakpoints'] = (has_1200 and has_900 and has_600, f"1200: {has_1200}, 900: {has_900}, 600: {has_600}")

    # 9. Custom scrollbars
    has_scrollbars = '::-webkit-scrollbar' in css and '::-webkit-scrollbar-thumb' in css and '::-webkit-scrollbar-track' in css
    results['custom_scrollbars'] = (has_scrollbars, "Custom scrollbar rules found")

    # 10. Check halation / pure black #000000
    # Search for #000000 or #000 (excluding rgba(0, 0, 0, ...) or comments)
    # Check background: #000000 or background-color: #000000
    pure_black = re.findall(r'background(?:-color)?\s*:\s*(?:#000000|#000)\b', css)
    results['no_pure_black_bg'] = (len(pure_black) == 0, f"Occurrences of #000000 / #000 bg: {len(pure_black)}")

    for k, (ok, detail) in results.items():
        print(f"[{'PASS' if ok else 'FAIL'}] {k}: {detail}")

if __name__ == '__main__':
    analyze_css()
