import re
from pathlib import Path

css_text = Path("static/css/style.css").read_text(encoding="utf-8")
html_text = Path("templates/index.html").read_text(encoding="utf-8")
js_app_text = Path("static/js/app.js").read_text(encoding="utf-8")
js_charts_text = Path("static/js/charts.js").read_text(encoding="utf-8")

# Check all classes in HTML
html_classes = set()
for m in re.finditer(r'class=["\']([^"\']+)["\']', html_text):
    for c in m.group(1).split():
        html_classes.add(c)

# Clean CSS
clean_css = re.sub(r'/\*[\s\S]*?\*/', '', css_text)
clean_css = re.sub(r'@keyframes\s+[^{]+\{[^}]*\{[^}]*\}[^}]*\}', '', clean_css)
css_classes = set(re.findall(r'\.([a-zA-Z0-9\-_]+)', clean_css))

print("=== HTML Classes ===")
for c in sorted(html_classes):
    status = "OK" if c in css_classes else "MISSING"
    print(f"  {c:30} : {status}")

print("\n=== Specific Requested Component Classes ===")
req = [
    'glass-card', 'btn-primary', 'btn-secondary', 'mode-switcher', 'status-pill',
    'pulse-dot', 'smart-progress-bar-fill', 'console-body', 'ladder-step',
    'top-strat-pill', 'markov-table', 'trades-table', 'n-table'
]
for r in req:
    status = "OK" if r in css_classes else "MISSING"
    print(f"  .{r:25} : {status}")

print("\n=== Tabular Numbers Verification ===")
tabular_elements = [
    '.tabular-nums', '.markov-table td', '.trades-table td', '.n-table td',
    '.stat-card p', '.console-body', '.ladder-step-amount', '.smart-rec-item p',
    '.recommendation-stat p', '.asset-wr-badge'
]
for t in tabular_elements:
    present = t in css_text
    print(f"  {t:30} : {'OK' if present else 'MISSING'}")

print("\n=== Numeric Alignment ===")
print("  td.num in CSS:", "td.num" in css_text)
print("  th.num in CSS:", "th.num" in css_text)
print("  trades-table nth-child in CSS:", ".trades-table td:nth-child" in css_text)
print("  n-table nth-child in CSS:", ".n-table td:nth-child" in css_text)

print("\n=== Responsive Breakpoints ===")
print("  @media 1200px:", "@media (max-width: 1200px)" in css_text)
print("  @media 900px:", "@media (max-width: 900px)" in css_text)
print("  @media 600px:", "@media (max-width: 600px)" in css_text)

print("\n=== Scrollbars ===")
print("  ::-webkit-scrollbar in CSS:", "::-webkit-scrollbar" in css_text)
print("  ::-webkit-scrollbar-thumb in CSS:", "::-webkit-scrollbar-thumb" in css_text)
print("  ::-webkit-scrollbar-track in CSS:", "::-webkit-scrollbar-track" in css_text)
