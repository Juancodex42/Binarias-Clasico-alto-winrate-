import sys
import os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')

import app

client = app.app.test_client()
response = client.get('/')

print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.content_type}")
print(f"Data Length (bytes): {len(response.data)}")

assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
assert b'<!DOCTYPE html>' in response.data
assert b'Binarias Simulator' in response.data
assert b'QUANT TERMINAL PRO' in response.data
assert b'Inter:wght' in response.data
assert b'JetBrains+Mono:wght' in response.data
assert b'smart-dashboard' in response.data
assert b'btn-smart-run' in response.data
assert b'smart-preset-select' in response.data
assert b'smart-correlation-canvas' in response.data
assert b'smart-equity-chart-canvas' in response.data
assert b'smart-mc-chart-canvas' in response.data
assert b'smart-tv-chart' in response.data
assert b'smart-markov-table' in response.data
assert b'/static/js/charts.js' in response.data
assert b'/static/js/app.js' in response.data

print("ALL FLASK RENDER ASSERTIONS PASSED!")
