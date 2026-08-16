import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

hex_matches = re.findall(r'#[0-9a-fA-F]{3,8}', content)
print(f"Total hex codes in index.html: {len(hex_matches)}")
unique_hex = sorted(set(hex_matches))
print(f"Unique hex codes: {unique_hex}")
