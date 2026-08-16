import re
import os
import sys
from bs4 import BeautifulSoup

# Ensure utf-8 output encoding on Windows console
sys.stdout.reconfigure(encoding='utf-8')

def audit_html():
    html_path = 'templates/index.html'
    if not os.path.exists(html_path):
        print(f"Error: {html_path} does not exist.")
        sys.exit(1)
        
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Total DOM IDs
    all_elements_with_id = soup.find_all(id=True)
    html_ids = [tag['id'] for tag in all_elements_with_id]
    unique_html_ids = set(html_ids)
    
    print(f"--- DOM ID INTEGRITY ---")
    print(f"Total elements with ID: {len(all_elements_with_id)}")
    print(f"Unique IDs: {len(unique_html_ids)}")
    
    # Check for duplicates
    duplicates = [id_name for id_name in unique_html_ids if html_ids.count(id_name) > 1]
    print(f"Duplicate IDs: {duplicates}")

    # 2. Form Controls (input, select, textarea)
    inputs = soup.find_all('input')
    selects = soup.find_all('select')
    textareas = soup.find_all('textarea')
    total_form_controls = len(inputs) + len(selects) + len(textareas)
    print(f"\n--- FORM CONTROLS ---")
    print(f"Inputs: {len(inputs)}")
    print(f"Selects: {len(selects)}")
    print(f"Textareas: {len(textareas)}")
    print(f"Total Form Controls: {total_form_controls}")
    
    # 3. Buttons
    buttons = soup.find_all('button')
    print(f"\n--- BUTTONS ---")
    print(f"Total Buttons: {len(buttons)}")
    for b in buttons:
        btn_id = b.get('id', 'NO_ID')
        btn_class = b.get('class', [])
        btn_text = b.get_text(strip=True)
        print(f"  Button id='{btn_id}' class='{btn_class}' text='{btn_text[:30]}'")

    # 4. Check JS references
    print(f"\n--- JAVASCRIPT DOM REFERENCES ---")
    js_files = ['static/js/app.js', 'static/js/charts.js']
    for js_path in js_files:
        if os.path.exists(js_path):
            with open(js_path, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            # Find getElementById('...') and getElementById("...")
            id_pattern = r'getElementById\([\'"]([a-zA-Z0-9_\-]+)[\'"]\)'
            qs_pattern = r'querySelector\([\'"]#([a-zA-Z0-9_\-]+)[\'"]\)'
            qsa_pattern = r'querySelectorAll\([\'"]#([a-zA-Z0-9_\-]+)[\'"]\)'
            
            found_ids = set(re.findall(id_pattern, js_content) + 
                            re.findall(qs_pattern, js_content) + 
                            re.findall(qsa_pattern, js_content))
            
            missing = [i for i in sorted(found_ids) if i not in unique_html_ids]
            print(f"File: {js_path}")
            print(f"  Referenced Static IDs: {len(found_ids)}")
            print(f"  Missing IDs in HTML: {missing}")
            
    # 5. Check Fonts and CDNs
    print(f"\n--- FONTS & CDNS ---")
    fonts_links = [link.get('href', '') for link in soup.find_all('link') if 'fonts.googleapis.com' in link.get('href', '')]
    print(f"Google Fonts Links: {fonts_links}")
    
    scripts = [s.get('src', '') for s in soup.find_all('script') if s.get('src')]
    print(f"Script tags: {scripts}")

    # 6. Check Smart Mode specific elements
    print(f"\n--- SMART MODE REQUIREMENTS ---")
    smart_reqs = {
        "smart-dashboard": soup.find(id="smart-dashboard") is not None,
        "mode-smart": soup.find(id="mode-smart") is not None,
        "mode-advanced": soup.find(id="mode-advanced") is not None,
        "btn-smart-run": soup.find(id="btn-smart-run") is not None,
        "smart-preset-select": soup.find(id="smart-preset-select") is not None,
        "smart-universe checkboxes": len(soup.find_all('input', {'name': 'smart-universe'})) >= 9,
        "asset-wr-badge count": len(soup.find_all('span', class_='asset-wr-badge')),
        "smart-console-box": soup.find(id="smart-console-box") is not None,
        "smart-progress-bar-fill": soup.find(id="smart-progress-bar-fill") is not None,
        "smart-console-logs": soup.find(id="smart-console-logs") is not None,
        "smart-top-5-box": soup.find(id="smart-top-5-box") is not None,
        "smart-top-5-list": soup.find(id="smart-top-5-list") is not None,
        "smart-rec-content": soup.find(id="smart-rec-content") is not None,
        "smart-ladder-content": soup.find(id="smart-ladder-content") is not None,
        "smart-correlation-canvas": soup.find(id="smart-correlation-canvas") is not None,
        "smart-selected-assets-table": soup.find(id="smart-selected-assets-table") is not None,
        "smart-selected-assets-body": soup.find(id="smart-selected-assets-body") is not None,
        "smart-equity-chart-canvas": soup.find(id="smart-equity-chart-canvas") is not None,
        "smart-mc-chart-canvas": soup.find(id="smart-mc-chart-canvas") is not None,
        "smart-asset-selector": soup.find(id="smart-asset-selector") is not None,
        "smart-tv-chart": soup.find(id="smart-tv-chart") is not None,
        "smart-tv-chart-empty": soup.find(id="smart-tv-chart-empty") is not None,
        "smart-markov-table": soup.find(id="smart-markov-table") is not None,
        "smart-markov-explanation": soup.find(id="smart-markov-explanation") is not None,
    }
    for req, present in smart_reqs.items():
        print(f"  {req}: {present}")

    # 7. Check Advanced Mode 5 Tabs
    print(f"\n--- ADVANCED MODE TABS ---")
    adv_tabs = ["dashboard", "backtest", "resultados", "estadisticas", "optimizador"]
    for tab in adv_tabs:
        elem = soup.find(id=tab)
        print(f"  Tab #{tab}: {'Found' if elem else 'MISSING'}")

    # 8. Check Header and Telemetry Elements
    print(f"\n--- HEADER & TELEMETRY ---")
    header_reqs = {
        "header.app-header": soup.find('header', class_='app-header') is not None,
        "badge-quant": soup.find(class_='badge-quant') is not None,
        "rust-engine-pill": soup.find(class_='rust-engine-pill') is not None,
        "live-badge": soup.find(id="live-badge") is not None,
        "live-badge-text": soup.find(id="live-badge-text") is not None,
        "pulse-dot": len(soup.find_all(class_='pulse-dot')) >= 2,
        "tabs-nav": soup.find('nav', class_='tabs-nav') is not None,
    }
    for req, present in header_reqs.items():
        print(f"  {req}: {present}")

if __name__ == '__main__':
    audit_html()
