import sys
import re
import json
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

all_ids = []
for tag in soup.find_all(id=True):
    all_ids.append({
        'id': tag['id'],
        'tag': tag.name,
        'classes': tag.get('class', []),
        'type': tag.get('type', None),
        'name': tag.get('name', None),
        'value': tag.get('value', None)
    })

inputs = []
for inp in soup.find_all(['input', 'select', 'textarea']):
    inputs.append({
        'tag': inp.name,
        'id': inp.get('id', None),
        'name': inp.get('name', None),
        'type': inp.get('type', inp.name),
        'value': inp.get('value', None),
        'min': inp.get('min', None),
        'max': inp.get('max', None),
        'step': inp.get('step', None),
        'checked': inp.has_attr('checked'),
        'readonly': inp.has_attr('readonly'),
        'disabled': inp.has_attr('disabled'),
        'data_attrs': {k: v for k, v in inp.attrs.items() if k.startswith('data-')}
    })

buttons = []
for btn in soup.find_all('button'):
    buttons.append({
        'id': btn.get('id', None),
        'class': btn.get('class', []),
        'type': btn.get('type', 'button'),
        'text': btn.get_text(strip=True),
        'disabled': btn.has_attr('disabled'),
        'form': btn.get('form', None),
        'data_attrs': {k: v for k, v in btn.attrs.items() if k.startswith('data-')}
    })

canvases = []
for c in soup.find_all('canvas'):
    canvases.append({
        'id': c.get('id', None),
        'class': c.get('class', [])
    })

tables = []
for t in soup.find_all('table'):
    tables.append({
        'id': t.get('id', None),
        'class': t.get('class', [])
    })

catalog = {
    'all_ids': all_ids,
    'inputs': inputs,
    'buttons': buttons,
    'canvases': canvases,
    'tables': tables
}

with open('.agents/survey_frontend_explorer/dom_catalog.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Catalog saved with {len(all_ids)} IDs, {len(inputs)} inputs, {len(buttons)} buttons, {len(canvases)} canvases, {len(tables)} tables.")
for el in sorted(all_ids, key=lambda x: x['id']):
    print(f"ID: {el['id']:<35} Tag: <{el['tag']}> Classes: {el['classes']} Type: {el['type']} Value: {el['value']}")

print("\n==================== 2. ALL FORM INPUTS & SELECTS ====================")
inputs = []
for inp in soup.find_all(['input', 'select', 'textarea']):
    inputs.append({
        'tag': inp.name,
        'id': inp.get('id', 'NO_ID'),
        'name': inp.get('name', 'NO_NAME'),
        'type': inp.get('type', inp.name),
        'value': inp.get('value', ''),
        'min': inp.get('min', ''),
        'max': inp.get('max', ''),
        'step': inp.get('step', ''),
        'checked': inp.has_attr('checked'),
        'readonly': inp.has_attr('readonly'),
        'disabled': inp.has_attr('disabled'),
        'data_attrs': {k: v for k, v in inp.attrs.items() if k.startswith('data-')}
    })
print(f"Total form inputs: {len(inputs)}")
for inp in inputs:
    print(f"Tag: {inp['tag']:<7} ID: {inp['id']:<25} Name: {inp['name']:<18} Type: {inp['type']:<10} Val: {str(inp['value']):<10} Min/Max/Step: {inp['min']}/{inp['max']}/{inp['step']} Flags: ck={inp['checked']} ro={inp['readonly']} dis={inp['disabled']}")

print("\n==================== 3. ALL BUTTONS ====================")
buttons = []
for btn in soup.find_all('button'):
    buttons.append({
        'id': btn.get('id', 'NO_ID'),
        'class': btn.get('class', []),
        'type': btn.get('type', 'button'),
        'text': btn.get_text(strip=True),
        'disabled': btn.has_attr('disabled'),
        'data_attrs': {k: v for k, v in btn.attrs.items() if k.startswith('data-')}
    })
print(f"Total buttons: {len(buttons)}")
for btn in buttons:
    print(f"ID: {btn['id']:<25} Classes: {str(btn['class']):<30} Data: {str(btn['data_attrs']):<30} Text: {btn['text']}")

print("\n==================== 4. ALL TEMPLATE PANES / TABS / CONTAINERS ====================")
for sec in soup.find_all('section'):
    print(f"Section ID: {sec.get('id')} Class: {sec.get('class')}")

for sub in soup.find_all(class_=re.compile(r'subtab-pane')):
    print(f"Subtab Pane ID: {sub.get('id')} Class: {sub.get('class')}")

with open('static/js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

with open('static/js/charts.js', 'r', encoding='utf-8') as f:
    charts_js = f.read()

print("\n==================== 5. JAVASCRIPT DOM QUERIES (getElementById) ====================")
js_ids = set(re.findall(r'getElementById\([\'"`]([^\'"`$]+)[\'"`]\)', app_js + charts_js))
print(f"Total getElementById targets: {len(js_ids)}")
for j in sorted(js_ids):
    print(f"  {j}")

print("\n==================== 6. JAVASCRIPT querySelector / querySelectorAll ====================")
js_qs = set(re.findall(r'querySelector(?:All)?\([\'"`]([^\'"`]+)[\'"`]\)', app_js + charts_js))
print(f"Total querySelector(All) targets: {len(js_qs)}")
for q in sorted(js_qs):
    print(f"  {q}")

print("\n==================== 7. EVENT LISTENERS IN JS ====================")
event_listeners = re.findall(r'(?:document\.getElementById\([\'"`]([^\'"`]+)[\'"`]\)|([a-zA-Z0-9_$]+))\s*\.\s*addEventListener\(\s*[\'"`]([^\'"`]+)[\'"`]\s*,\s*([a-zA-Z0-9_$.() =>{}]+)', app_js)
print(f"Total addEventListener matches: {len(event_listeners)}")
for el in event_listeners:
    target = el[0] or el[1]
    event = el[2]
    handler = el[3].strip().replace('\n', ' ')[:50]
    print(f"  Target: {target:<30} Event: {event:<10} Handler: {handler}")
