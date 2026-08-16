import sys
from html.parser import HTMLParser

class StrictTagValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.void_elements = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
        self.errors = []
        
    def handle_starttag(self, tag, attrs):
        if tag.lower() not in self.void_elements:
            self.stack.append((tag.lower(), self.getpos()))
            
    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in self.void_elements:
            return
        if not self.stack:
            self.errors.append(f"Unexpected closing tag </{tag_lower}> at {self.getpos()}")
            return
        last_tag, pos = self.stack.pop()
        if last_tag != tag_lower:
            self.errors.append(f"Mismatched closing tag </{tag_lower}> at {self.getpos()}, expected </{last_tag}> (opened at {pos})")

validator = StrictTagValidator()
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

validator.feed(content)

if validator.stack:
    for tag, pos in validator.stack:
        validator.errors.append(f"Unclosed tag <{tag}> opened at {pos}")

print(f"Tag validation errors: {len(validator.errors)}")
for err in validator.errors:
    print(f"  {err}")

if not validator.errors:
    print("HTML5 Tag hierarchy is 100% strictly balanced and valid!")
