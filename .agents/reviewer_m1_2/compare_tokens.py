import re
from pathlib import Path
from html.parser import HTMLParser

html_text = Path("templates/index.html").read_text(encoding="utf-8")
css_text = Path("static/css/style.css").read_text(encoding="utf-8")
app_js_text = Path("static/js/app.js").read_text(encoding="utf-8")

class HTMLCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.classes = set()
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        self.tags.append((tag, attr_dict))
        if 'class' in attr_dict:
            for c in attr_dict['class'].split():
                self.classes.add(c)
        if 'id' in attr_dict:
            self.ids.add(attr_dict['id'])

collector = HTMLCollector()
collector.feed(html_text)

print(f"Total HTML classes: {len(collector.classes)}")
print("HTML Classes:", sorted(collector.classes))
print(f"\nTotal HTML IDs: {len(collector.ids)}")

# Extract CSS classes from style.css
css_no_comments = re.sub(r'/\*[\s\S]*?\*/', '', css_text)
# Remove keyframe bodies
css_no_kf = re.sub(r'@keyframes\s+[^{]+\{[^}]*\{[^}]*\}[^}]*\}', '', css_no_comments)

css_classes = set(re.findall(r'\.([a-zA-Z0-9\-_]+)', css_no_kf))
css_ids = set(re.findall(r'#([a-zA-Z0-9\-_]+)', css_no_kf))

print(f"\nTotal CSS classes in style.css: {len(css_classes)}")
print(f"Total CSS IDs in style.css: {len(css_ids)}")

html_missing = collector.classes - css_classes
print("\nHTML classes not defined in style.css:", html_missing)

# Check all IDs in HTML vs style.css
html_ids_styled = collector.ids & css_ids
print(f"\nHTML IDs styled in style.css: {len(html_ids_styled)} / {len(collector.ids)}")

# Check app.js dynamic classes
js_classes = set()
for m in re.finditer(r'classList\.(?:add|remove|toggle|contains)\(\s*([^\)]+)\)', app_js_text):
    for s in re.findall(r"['\"`]([a-zA-Z0-9\-_]+)['\"`]", m.group(1)):
        js_classes.add(s)
for m in re.finditer(r'class=["\']([^"\']+)["\']', app_js_text):
    for c in m.group(1).split():
        c_clean = re.sub(r'[\$\{\}]', '', c).strip()
        if c_clean and re.match(r'^[a-zA-Z0-9\-_]+$', c_clean):
            js_classes.add(c_clean)

print(f"\nTotal JS dynamic classes: {len(js_classes)}")
print("JS dynamic classes:", sorted(js_classes))
js_missing = js_classes - css_classes
print("JS classes not in style.css:", js_missing)
