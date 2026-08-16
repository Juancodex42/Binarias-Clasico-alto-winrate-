import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

with open('templates/index.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

contract_ids = [
    # Header & Modes
    'mode-smart', 'mode-advanced',
    # Smart Mode Form Controls
    'smart-preset-select', 'smart-streak-length', 'smart-base-capital',
    'smart-profit-pct', 'smart-risk-capital', 'smart-attempts', 'smart-payout',
    'smart-generations', 'smart-population', 'btn-smart-run',
    # Smart Mode Telemetry & Output
    'smart-console-box', 'smart-progress-bar-fill', 'smart-console-logs',
    'smart-top-5-box', 'smart-top-5-list', 'smart-rec-content',
    'smart-ladder-content', 'smart-selected-assets-table', 'smart-selected-assets-body',
    'smart-markov-table', 'smart-markov-explanation', 'smart-asset-selector',
    'smart-tv-chart', 'smart-tv-chart-empty', 'smart-equity-chart-canvas',
    'smart-mc-chart-canvas', 'smart-correlation-canvas',
    # Advanced Mode Controls & Panels
    'pair-selector', 'interval-selector', 'source-selector', 'live-badge',
    'live-badge-text', 'tv-chart', 'chart-loader', 'backtest-form',
    'run-backtest-btn', 'save-backtest-btn', 'strategy-selector', 'dynamic-params',
    'expiry-candles', 'payout', 'backtest-n-consecutive', 'backtest-cycle-prob',
    'backtest-bet-fraction', 'optimize-genetic-btn', 'gen-generations',
    'gen-population', 'gen-min-trades', 'genetic-progress-fill',
    'genetic-progress-text', 'genetic-progress-eta', 'genetic-feedback',
    'backtest-progress-fill', 'stat-winrate', 'stat-trades', 'stat-pnl',
    'stat-mw', 'stat-ml', 'equity-chart', 'trades-table', 'btn-clear-history',
    'history-list', 'saved-list', 'autocorr-chart', 'streaks-chart', 'hourly-chart',
    'cond-probs', 'market-state-chart', 'markov-table', 'opt-winrate', 'opt-payout',
    'opt-base-capital', 'opt-profit-pct', 'opt-risk-capital', 'opt-target-capital',
    'opt-attempts', 'btn-calc-streak', 'streak-progress-fill',
    'streak-recommendation-content', 'bet-ladder-container',
    'streak-alternatives-table', 'mc-chart',
    # Additional key buttons and sections
    'btn-resultados', 'btn-estadisticas', 'btn-optimizador',
    'dashboard', 'backtest', 'resultados', 'estadisticas', 'optimizador',
    'smart-dashboard', 'sec-strategy', 'sec-barbell', 'sec-genetic'
]

print(f"Verifying {len(contract_ids)} contract IDs against templates/index.html:")
missing = []
for cid in contract_ids:
    elem = soup.find(id=cid)
    if not elem:
        missing.append(cid)
    else:
        # print ok
        pass

if missing:
    print(f"FAILED: Missing contract IDs: {missing}")
    sys.exit(1)
else:
    print(f"SUCCESS: All {len(contract_ids)} contract IDs are present in templates/index.html!")

# Verify classes
classes = [
    'tabs-nav', 'asset-wr-badge', 'badge-quant', 'rust-engine-pill', 'pulse-dot'
]
for c in classes:
    elems = soup.find_all(class_=c)
    print(f"Class '{c}': found {len(elems)} elements.")
    if len(elems) == 0:
        print(f"FAILED: Class '{c}' not found!")
        sys.exit(1)
