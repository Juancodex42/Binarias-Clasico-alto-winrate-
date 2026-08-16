import os
import glob
import math
import json
import subprocess
from collections import OrderedDict
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request, render_template, Response, send_from_directory
from flask_cors import CORS
from config import Config

from strategies import STRATEGIES
from strategies.genetic_composite import GeneticCompositeStrategy
from strategies.daily_confluence import DailyConfluenceStrategy
from engine.simulator import BinarySimulator
from engine.statistics import StatisticsEngine
from engine.optimizer import CapitalOptimizer
from engine.correlation import CorrelationEngine

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

import threading

# In-memory LRU cache for DataFrames
_data_cache = OrderedDict()
_cache_lock = threading.Lock()

# Instantiate engines
simulator = BinarySimulator()
stats_engine = StatisticsEngine()
optimizer = CapitalOptimizer()


import re

def is_safe_symbol(symbol):
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', symbol))

def is_safe_interval(interval):
    return bool(re.match(r'^[a-zA-Z0-9]+$', interval))


def clean_json_data(data):
    """Recursively replace NaN and Infinity with None (null in JSON)."""
    if isinstance(data, dict):
        return {k: clean_json_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_json_data(v) for v in data]
    elif isinstance(data, (np.integer,)):
        return int(data)
    elif isinstance(data, (np.floating, float)):
        if math.isnan(data) or math.isinf(data):
            return None
        return float(data)
    elif isinstance(data, np.ndarray):
        return clean_json_data(data.tolist())
    elif isinstance(data, np.bool_):
        return bool(data)
    return data


def preserve_peaks_subsample(data_list, max_points=500, key='equity'):
    """Submuestreo que preserva los picos locales (máximos y mínimos) de la curva de equidad sin exceder max_points."""
    if not data_list or len(data_list) <= max_points:
        return data_list
    
    num_bins = max(1, max_points // 2)
    bin_size = len(data_list) / float(num_bins)
    sampled = []
    
    for i in range(num_bins):
        start_idx = int(i * bin_size)
        end_idx = int((i + 1) * bin_size) if i < num_bins - 1 else len(data_list)
        chunk = data_list[start_idx:end_idx]
        if not chunk:
            continue
            
        min_elem = min(chunk, key=lambda x: x.get(key, 0) if x.get(key) is not None else 0)
        max_elem = max(chunk, key=lambda x: x.get(key, 0) if x.get(key) is not None else 0)
        
        candidates = [min_elem, max_elem]
        candidates.sort(key=lambda x: chunk.index(x))
        
        for item in candidates:
            if not sampled or item != sampled[-1]:
                sampled.append(item)
                
    return sampled


def get_genetic_optimizer_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(base_dir, "engine", "genetic_optimizer", "target", "release", "genetic_optimizer.exe")
    if not os.path.exists(exe_path):
        exe_path = os.path.join(base_dir, "engine", "genetic_optimizer", "target", "release", "genetic_optimizer")
    return exe_path if (exe_path and os.path.exists(exe_path)) else None


def extract_json_from_output(text):
    if not text:
        raise ValueError("No valid JSON found in process output.")
    
    non_progress_lines = [
        line for line in text.splitlines() 
        if not line.strip().startswith("PROGRESS:")
    ]
    clean_text = "\n".join(non_progress_lines).strip()
    
    if not clean_text:
        raise ValueError("No valid JSON found in process output.")
        
    try:
        return json.loads(clean_text)
    except Exception:
        pass
        
    first_brace = clean_text.find('{')
    last_brace = clean_text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = clean_text[first_brace:last_brace + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    first_bracket = clean_text.find('[')
    last_bracket = clean_text.rfind(']')
    if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
        candidate = clean_text[first_bracket:last_bracket + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    raise ValueError(f"No valid JSON found in process output: {text[:200]}")

def sse_response(generator):
    response = Response(generator, mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Connection'] = 'keep-alive'
    return response


import urllib.request

INTERVAL_ORDER = {'1d': 1, '4h': 2, '2h': 3, '1h': 4, '30m': 5, '15m': 6, '5m': 7, '3m': 8, '1m': 9}

def sort_intervals(interval_list):
    return sorted(list(set(interval_list)), key=lambda x: INTERVAL_ORDER.get(x, 99))


def fetch_and_save_binance_klines(pair, interval):
    """Fetch historical klines from Binance API and save to CSV on the fly."""
    if not is_safe_symbol(pair) or not is_safe_interval(interval):
        return None
    url = f"https://api.binance.com/api/v3/klines?symbol={pair}&interval={interval}&limit=1000"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if isinstance(data, list) and len(data) > 0:
                rows = []
                for c in data:
                    open_time = int(c[0])
                    rows.append({
                        'open_time': open_time,
                        'open': float(c[1]),
                        'high': float(c[2]),
                        'low': float(c[3]),
                        'close': float(c[4]),
                        'volume': float(c[5]),
                        'close_time': int(c[6]),
                        'quote_asset_volume': float(c[7]),
                        'number_of_trades': int(c[8]),
                        'taker_buy_base_asset_volume': float(c[9]),
                        'taker_buy_quote_asset_volume': float(c[10]),
                        'ignore': 0
                    })
                df = pd.DataFrame(rows)
                df.sort_values('open_time', inplace=True)
                df.reset_index(drop=True, inplace=True)
                df['time'] = df['open_time'] // 1000
                
                # Save to DATA_DIR so it can be re-used locally
                filename = f"{pair}_{interval}.csv"
                filepath = os.path.join(app.config['DATA_DIR'], filename)
                try:
                    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
                    df.to_csv(filepath, index=False)
                except Exception as save_err:
                    print(f"Error saving {filename}: {save_err}")

                return df
    except Exception as e:
        print(f"Error fetching Binance klines for {pair} {interval}: {e}")
    return None


MAX_DATA_CACHE_SIZE = 30

def load_csv_data(pair, interval):
    """Load and cache CSV data with thread-safe LRU eviction."""
    if not is_safe_symbol(pair) or not is_safe_interval(interval):
        return None
    cache_key = f"{pair}_{interval}"

    with _cache_lock:
        if cache_key in _data_cache:
            _data_cache.move_to_end(cache_key)
            return _data_cache[cache_key]

        filename = f"{pair}_{interval}.csv"
        filepath = os.path.join(app.config['DATA_DIR'], filename)
        if not os.path.exists(filepath):
            df = fetch_and_save_binance_klines(pair, interval)
        else:
            df = pd.read_csv(filepath)
            required_cols = ['open', 'high', 'low', 'close']
            if all(col in df.columns for col in required_cols):
                valid_mask = (
                    (df['high'] >= df['low']) &
                    (df['open'] <= df['high']) &
                    (df['open'] >= df['low']) &
                    (df['close'] <= df['high']) &
                    (df['close'] >= df['low']) &
                    (~df[required_cols].isna().any(axis=1))
                )
                df = df[valid_mask].copy()

            if 'open_time' in df.columns:
                df.sort_values('open_time', inplace=True)
                df.reset_index(drop=True, inplace=True)
                if df['open_time'].max() > 2**32:
                    df['time'] = df['open_time'] // 1000
                else:
                    df['time'] = df['open_time']

        if df is not None:
            if len(_data_cache) >= MAX_DATA_CACHE_SIZE:
                _data_cache.popitem(last=False)
            _data_cache[cache_key] = df
        return df


# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/api/data/pairs', methods=['GET'])
def get_pairs():
    data_dir = app.config['DATA_DIR']
    all_intervals = set(app.config.get('AVAILABLE_INTERVALS', ['1d', '4h', '1h', '30m', '15m', '5m', '1m']))

    if not os.path.exists(data_dir):
        return jsonify({'pairs': [], 'intervals': sort_intervals(list(all_intervals))})

    files = glob.glob(os.path.join(data_dir, '*.csv'))
    pairs = set()

    for f in files:
        basename = os.path.basename(f).replace('.csv', '')
        parts = basename.split('_')
        if len(parts) >= 2:
            pairs.add(parts[0])
            all_intervals.add(parts[1])

    return jsonify({
        'pairs': sorted(list(pairs)) or app.config.get('AVAILABLE_PAIRS', []),
        'intervals': sort_intervals(list(all_intervals))
    })


@app.route('/api/data/candles', methods=['GET'])
def get_candles():
    pair = request.args.get('pair', 'BTCUSDT')
    interval = request.args.get('interval', '1h')
    try:
        limit = int(request.args.get('limit', 500))
    except ValueError:
        limit = 500

    df = load_csv_data(pair, interval)
    if df is None:
        return jsonify({'error': 'Data not found'}), 404

    df_subset = df.tail(limit)

    candles = []
    for _, row in df_subset.iterrows():
        candles.append({
            'time': int(row['time']),
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close']),
            'volume': float(row['volume'])
        })

    return jsonify(clean_json_data({'candles': candles}))


@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    try:
        result = []
        for key, strategy_class in STRATEGIES.items():
            instance = strategy_class()
            result.append({
                'name': key,
                'display_name': instance.name,
                'description': instance.description,
                'params': instance.get_params_schema()
            })
        return jsonify(clean_json_data({'strategies': result}))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    try:
        req = request.json or {}
        strategy_name = req.get('strategy', '')
        params = req.get('params', {})
        pair = req.get('pair', 'BTCUSDT')
        interval = req.get('interval', '1h')
        if not is_safe_symbol(pair) or not is_safe_interval(interval):
            return jsonify({'error': 'Par o intervalo no válido.'}), 400
        expiry_candles = int(req.get('expiry_candles', 1))
        payout = float(req.get('payout', 0.92))
        
        if expiry_candles < 1:
            return jsonify({'error': 'expiry_candles debe ser mayor o igual a 1.'}), 400
        if payout < 0.0 or payout > 2.0:
            return jsonify({'error': 'payout debe estar entre 0.0 y 2.0.'}), 400
        if strategy_name in ['ema_cross', 'genetic_composite']:
            fast = int(params.get('ema_fast_period' if strategy_name == 'genetic_composite' else 'fast_period', 9))
            slow = int(params.get('ema_slow_period' if strategy_name == 'genetic_composite' else 'slow_period', 21))
            if fast <= 0 or slow <= 0:
                return jsonify({'error': 'Los periodos de las EMAs deben ser mayores a 0.'}), 400
            if fast >= slow:
                return jsonify({'error': 'El periodo de la EMA rápida debe ser menor que el de la lenta.'}), 400

        # Load data
        df = load_csv_data(pair, interval)
        if df is None:
            return jsonify({'error': f'Datos no encontrados para {pair} {interval}'}), 404

        # Get strategy
        if strategy_name not in STRATEGIES:
            return jsonify({'error': f'Estrategia "{strategy_name}" no encontrada. Disponibles: {list(STRATEGIES.keys())}'}), 400

        strategy_class = STRATEGIES[strategy_name]
        strategy = strategy_class()

        # Generate signals
        signals = strategy.generate_signals(df, params)

        mode = req.get('mode', 'SIMPLE')
        n_consecutive = int(req.get('n_consecutive', 5))
        bet_fraction = float(req.get('bet_fraction', 0.1))
        if bet_fraction <= 0.0 or bet_fraction > 1.0:
            return jsonify({'error': 'bet_fraction debe ser un número positivo entre 0.0 y 1.0.'}), 400

        allow_overlapping = bool(req.get('allow_overlapping', False))
        max_concurrent_trades = int(req.get('max_concurrent_trades', 1))
        tie_rule = req.get('tie_rule', 'RETURN_STAKE')

        # Run simulator
        sim_results = simulator.run(
            df, signals,
            expiry_candles=expiry_candles,
            payout=payout,
            initial_capital=1000.0,
            mode=mode,
            n_consecutive=n_consecutive,
            bet_fraction=bet_fraction,
            allow_overlapping=allow_overlapping,
            max_concurrent_trades=max_concurrent_trades,
            tie_rule=tie_rule
        )

        # Run statistics
        trades = sim_results['trades']
        stats = {}
        if len(trades) > 0:
            stats = stats_engine.analyze(trades, df=df)

        # Build signals list for chart markers with full execution data
        signal_markers = []
        last_exit = 0
        for t in trades:
            e_time = t.get('entry_time', t.get('time', 0))
            x_time = t.get('exit_time', e_time)
            if e_time and e_time >= last_exit:
                e_sec = int(e_time / 1000) if e_time > 2**32 else int(e_time)
                x_sec = int(x_time / 1000) if x_time > 2**32 else int(x_time)
                
                signal_markers.append({
                    'time': e_sec,
                    'direction': t['direction'],
                    'entry_price': t.get('entry_price'),
                    'exit_price': t.get('exit_price'),
                    'pnl': t.get('pnl', 0.0),
                    'bet_size': t.get('bet_size', 0.0),
                    'result': t.get('result', 'WIN')
                })
                signal_markers.append({
                    'time': x_sec,
                    'direction': 'EXIT',
                    'result': t.get('result', 'WIN'),
                    'trade_direction': t['direction'],
                    'entry_price': t.get('entry_price'),
                    'exit_price': t.get('exit_price'),
                    'pnl': t.get('pnl', 0.0),
                    'bet_size': t.get('bet_size', 0.0)
                })
                last_exit = x_time


        # Convert equity curve times to seconds
        equity_curve = []
        for ec in sim_results['equity_curve']:
            t = ec.get('time')
            if t is not None:
                t_val = float(t)
                if t_val > 2**32:
                    t_val = t_val / 1000
                equity_curve.append({'time': int(t_val), 'equity': ec['equity']})

        # Convert trade times to seconds
        formatted_trades = []
        for trade in trades:
            t = trade.get('time')
            t_val = None
            if t is not None:
                t_val = float(t)
                if t_val > 2**32:
                    t_val = t_val / 1000
                t_val = int(t_val)
            formatted_trades.append({
                'time': t_val,
                'direction': trade['direction'],
                'entry_price': trade['entry_price'],
                'exit_price': trade['exit_price'],
                'result': trade['result'],
                'pnl': trade['pnl']
            })

        response = {
            'trades': formatted_trades,
            'equity_curve': equity_curve,
            'stats': stats,
            'signals': signal_markers,
            'summary': sim_results['summary']
        }

        return jsonify(clean_json_data(response))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/optimize', methods=['POST'])
def run_optimize():
    try:
        req = request.json or {}
        win_rate = float(req.get('win_rate', 0.5))
        payout = float(req.get('payout', 0.92))
        max_n = int(req.get('max_n', 15))
        
        if not (0.0 <= win_rate <= 1.0):
            return jsonify({'error': 'win_rate debe estar entre 0.0 y 1.0.'}), 400
        if payout < 0.0 or payout > 2.0:
            return jsonify({'error': 'payout debe estar entre 0.0 y 2.0.'}), 400
        if max_n < 1 or max_n > 50:
            return jsonify({'error': 'max_n debe estar entre 1 y 50.'}), 400

        result = optimizer.find_optimal_n(win_rate, payout, max_n)
        if isinstance(result, dict) and 'error' in result:
            return jsonify(clean_json_data(result)), 400
        return jsonify(clean_json_data(result))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/montecarlo', methods=['POST'])
def run_montecarlo():
    try:
        req = request.json or {}
        win_rate = float(req.get('win_rate', 0.5))
        payout = float(req.get('payout', 0.92))
        n = int(req.get('n', 3))
        kelly_f = float(req.get('kelly_f', 0.1))
        num_simulations = min(int(req.get('num_simulations', 5000)), 10000)
        num_cycles = min(int(req.get('num_cycles', 500)), 2000)
        
        if not (0.0 <= win_rate <= 1.0):
            return jsonify({'error': 'win_rate debe estar entre 0.0 y 1.0.'}), 400
        if payout < 0.0 or payout > 2.0:
            return jsonify({'error': 'payout debe estar entre 0.0 y 2.0.'}), 400
        if n < 1 or n > 50:
            return jsonify({'error': 'n debe estar entre 1 y 50.'}), 400
        if not (0.0 <= kelly_f <= 1.0):
            return jsonify({'error': 'kelly_f (fracción de apuesta) debe estar entre 0.0 y 1.0.'}), 400

        result = optimizer.monte_carlo(win_rate, payout, n, kelly_f, num_simulations, num_cycles)

        # Subsample paths for JSON (max 50 paths, max 200 points each)
        if 'paths' in result:
            sampled_paths = []
            for path in result['paths'][:50]:
                if len(path) > 200:
                    step = len(path) // 200
                    sampled_paths.append(path[::step])
                else:
                    sampled_paths.append(path)
            result['paths'] = sampled_paths

        return jsonify(clean_json_data(result))

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/genetic/run', methods=['POST'])
def run_genetic_optimization():
    try:
        req = request.json or {}
        pair = req.get('pair', 'BTCUSDT')
        interval = req.get('interval', '1h')
        if not is_safe_symbol(pair) or not is_safe_interval(interval):
            return jsonify({'error': 'Par o intervalo no válido.'}), 400
        expiry = int(req.get('expiry', 1))
        min_trades = float(req.get('min_trades', 5.0))
        generations = int(req.get('generations', 50))
        population = int(req.get('population', 200))
        
        if expiry < 1:
            return jsonify({'error': 'expiry debe ser mayor o igual a 1.'}), 400
        if min_trades < 0.1:
            return jsonify({'error': 'min_trades debe ser al menos 0.1.'}), 400
        if generations < 1 or generations > 500:
            return jsonify({'error': 'generations debe estar entre 1 y 500.'}), 400
        if population < 10 or population > 1000:
            return jsonify({'error': 'population debe estar entre 10 y 1000.'}), 400
        
        filename = f"{pair}_{interval}.csv"
        filepath = os.path.join(app.config['DATA_DIR'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': f'Datos no encontrados para {pair} {interval}'}), 404
            
        import subprocess
        import json
        
        exe_path = get_genetic_optimizer_path()
        if not exe_path:
            return jsonify({'error': 'El ejecutable del optimizador genetico en Rust no ha sido compilado. Ejecuta cargo build --release en la carpeta correspondiente.'}), 500
                
        cmd = [
            exe_path,
            "--csv", filepath,
            "--expiry", str(expiry),
            "--min-trades", str(min_trades),
            "--generations", str(generations),
            "--population", str(population)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        try:
            output_json = extract_json_from_output(result.stdout)
            return jsonify(clean_json_data(output_json))
        except Exception as json_err:
            return jsonify({'error': 'Error al parsear el JSON retornado por el optimizador.', 'details': result.stdout, 'stderr': result.stderr, 'exception': str(json_err)}), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/montecarlo-discrete', methods=['POST'])
def run_montecarlo_discrete():
    try:
        req = request.json or {}
        win_rate = float(req.get('win_rate', 0.55))
        payout = float(req.get('payout', 0.85))
        n_consecutive = int(req.get('n_consecutive', 4))
        bet_fraction = float(req.get('bet_fraction', 0.1))
        risk_capital = float(req.get('risk_capital', 200.0))
        target_capital = float(req.get('target_capital', 1000.0))
        num_simulations = min(int(req.get('num_simulations', 5000)), 10000)
        
        if not (0.0 <= win_rate <= 1.0):
            return jsonify({'error': 'win_rate debe estar entre 0.0 y 1.0.'}), 400
        if payout < 0.0 or payout > 2.0:
            return jsonify({'error': 'payout debe estar entre 0.0 y 2.0.'}), 400
        if n_consecutive < 1 or n_consecutive > 50:
            return jsonify({'error': 'n_consecutive debe estar entre 1 y 50.'}), 400
        if not (0.0 <= bet_fraction <= 1.0):
            return jsonify({'error': 'bet_fraction debe estar entre 0.0 y 1.0.'}), 400
        if risk_capital <= 0 or target_capital <= 0:
            return jsonify({'error': 'El capital de riesgo y el capital objetivo deben ser mayores a 0.'}), 400
        if target_capital <= risk_capital:
            return jsonify({'error': 'El capital objetivo debe ser mayor que el capital de riesgo.'}), 400
        
        result = optimizer.monte_carlo_discrete(
            win_rate=win_rate,
            payout=payout,
            n_consecutive=n_consecutive,
            bet_fraction=bet_fraction,
            risk_capital=risk_capital,
            target_capital=target_capital,
            num_simulations=num_simulations
        )
        return jsonify(clean_json_data(result))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/optimize-streak', methods=['POST'])
def run_optimize_streak():
    try:
        req = request.json or {}
        win_rate = float(req.get('win_rate', 0.55))
        payout = float(req.get('payout', 0.85))
        risk_capital = float(req.get('risk_capital', 200.0))
        target_capital = float(req.get('target_capital', 1000.0))
        attempts = int(req.get('attempts', 5))
        
        if not (0.0 <= win_rate <= 1.0):
            return jsonify({'error': 'win_rate debe estar entre 0.0 y 1.0.'}), 400
        if payout < 0.0 or payout > 2.0:
            return jsonify({'error': 'payout debe estar entre 0.0 y 2.0.'}), 400
        if risk_capital <= 0 or target_capital <= 0:
            return jsonify({'error': 'El capital de riesgo y el capital objetivo deben ser mayores a 0.'}), 400
        if target_capital <= risk_capital:
            return jsonify({'error': 'El capital objetivo debe ser mayor que el capital de riesgo.'}), 400
        if attempts < 1 or attempts > 100:
            return jsonify({'error': 'El número de intentos debe estar entre 1 y 100.'}), 400
        
        base_capital = float(req.get('base_capital', target_capital))
        result = optimizer.calculate_streak_plan(
            win_rate=win_rate,
            payout=payout,
            risk_capital=risk_capital,
            target_capital=target_capital,
            attempts=attempts,
            base_capital=base_capital
        )
        return jsonify(clean_json_data(result))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/smart-optimize', methods=['POST'])
def run_smart_optimize():
    try:
        req = request.json or {}
        pair = req.get('pair', 'BTCUSDT')
        interval = req.get('interval', '1h')
        if not is_safe_symbol(pair) or not is_safe_interval(interval):
            return jsonify({'error': 'Par o intervalo no válido.'}), 400
        base_capital = float(req.get('base_capital', 1000.0))
        profit_pct = float(req.get('profit_pct', 20.0))
        attempts = int(req.get('attempts', 2))
        payout = float(req.get('payout', 0.85))
        
        if base_capital <= 0:
            return jsonify({'error': 'base_capital debe ser mayor a 0.'}), 400
        if not (0.0 < profit_pct <= 100.0):
            return jsonify({'error': 'profit_pct debe estar entre 0.0 y 100.0.'}), 400
        if attempts < 1 or attempts > 100:
            return jsonify({'error': 'attempts debe estar entre 1 y 100.'}), 400
        if payout < 0.0 or payout > 2.0:
            return jsonify({'error': 'payout debe estar entre 0.0 y 2.0.'}), 400
        
        # 1. Run the Rust genetic optimizer in the background to find the best strategy
        filename = f"{pair}_{interval}.csv"
        filepath = os.path.join(app.config['DATA_DIR'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': f'Datos no encontrados para {pair} {interval}'}), 404
            
        import subprocess
        import json
        
        exe_path = get_genetic_optimizer_path()
        if not exe_path:
            return jsonify({'error': 'El ejecutable del optimizador genetico en Rust no ha sido compilado.'}), 500
                
        expiry_req = int(req.get('expiry', 1))
        min_trades_req = float(req.get('min_trades', 5.0))
        generations_req = int(req.get('generations', 60))
        population_req = int(req.get('population', 250))

        cmd = [
            exe_path,
            "--csv", filepath,
            "--expiry", str(expiry_req),
            "--min-trades", str(min_trades_req),
            "--generations", str(generations_req),
            "--population", str(population_req)
        ]
        
        result_rust = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        try:
            output_json = extract_json_from_output(result_rust.stdout)
        except Exception as json_err:
            return jsonify({
                'error': 'Error al parsear el JSON retornado por el optimizador genético.',
                'details': result_rust.stdout,
                'stderr': result_rust.stderr,
                'exception': str(json_err)
            }), 500
            
        if 'error' in output_json:
            return jsonify({'error': output_json['error']}), 500
            
        # Extract best genome and win rates
        best_genome = output_json.get('parameters', {})
        # Note: we use out_of_sample_win_rate for safety (avoid overfitting)
        win_rate = float(output_json.get('out_of_sample_win_rate', 0.55))
        in_sample_win_rate = float(output_json.get('in_sample_win_rate', 0.60))
        
        # 2. Run multi-strategy evaluation in python to pick the highest Win Rate strategy
        df = load_csv_data(pair, interval)
        if df is None:
            return jsonify({'error': f'Datos de velas no encontrados para {pair} {interval}'}), 404
            
        from strategies.genetic_composite import GeneticCompositeStrategy
        from strategies.islg_rs import IslgRsStrategy
        from strategies.deesr import DeesrStrategy
        from strategies.climax_reversal import ClimaxReversalStrategy
        from strategies.volatility_squeeze_ml import VolatilitySqueezeMLStrategy

        candidates = []
        
        # Candidate 1: Genetic Composite
        gen_strat = GeneticCompositeStrategy()
        gen_signals = gen_strat.generate_signals(df, best_genome)
        gen_res = simulator.run(df, gen_signals, expiry_candles=1, allow_overlapping=True)
        gen_wr = gen_res['summary']['win_rate_effective']
        candidates.append({
            'strategy_name': 'genetic_composite',
            'display_name': 'Optimizador Genético Rust',
            'signals': gen_signals,
            'win_rate': gen_wr if gen_res['summary']['total_trades'] >= 5 else win_rate,
            'params': best_genome
        })

        # Candidate 2: ISLG Sweeps
        islg_strat = IslgRsStrategy()
        islg_params = {"lookback_period": 50, "wick_ratio": 0.65, "vol_mult": 1.8, "rsi_period": 7}
        islg_signals = islg_strat.generate_signals(df, islg_params)
        islg_res = simulator.run(df, islg_signals, expiry_candles=1, allow_overlapping=True)
        if islg_res['summary']['total_trades'] >= 3:
            candidates.append({
                'strategy_name': 'islg_rs',
                'display_name': 'Barridos de Liquidez Institucional (ISLG)',
                'signals': islg_signals,
                'win_rate': islg_res['summary']['win_rate_effective'],
                'params': islg_params
            })

        # Candidate 3: DEESR Extreme Reversal
        deesr_strat = DeesrStrategy()
        deesr_params = {"bb_period": 20, "bb_std": 2.2, "kc_period": 20, "kc_mult": 1.8, "rsi_fast_period": 3, "rsi_slow_period": 14, "max_body_ratio": 0.35, "min_wick_ratio": 0.45}
        deesr_signals = deesr_strat.generate_signals(df, deesr_params)
        deesr_res = simulator.run(df, deesr_signals, expiry_candles=1, allow_overlapping=True)
        if deesr_res['summary']['total_trades'] >= 3:
            candidates.append({
                'strategy_name': 'deesr',
                'display_name': 'Doble Envoltura Extrema (DEESR)',
                'signals': deesr_signals,
                'win_rate': deesr_res['summary']['win_rate_effective'],
                'params': deesr_params
            })

        # Candidate 4: Climax Reversal
        climax_strat = ClimaxReversalStrategy()
        climax_params = {"min_streak": 5, "min_wick_ratio": 0.45}
        climax_signals = climax_strat.generate_signals(df, climax_params)
        climax_res = simulator.run(df, climax_signals, expiry_candles=3, allow_overlapping=True)
        if climax_res['summary']['total_trades'] >= 3:
            candidates.append({
                'strategy_name': 'climax_reversal',
                'display_name': 'Agotamiento Clímax por Rachas',
                'signals': climax_signals,
                'win_rate': climax_res['summary']['win_rate_effective'],
                'params': climax_params
            })

        # Pick best candidate
        best_cand = max(candidates, key=lambda c: c['win_rate'])
        strategy = gen_strat
        signals = best_cand['signals']
        win_rate = float(best_cand['win_rate'])
        best_genome = best_cand['params']

        risk_capital = base_capital * (profit_pct / 100.0)
        target_capital = base_capital  # We want to double the base_capital (make base_capital profit)
        bet_fraction = 1.0 / attempts
        
        # First calculate the optimal streak N for target
        # We run the streak planner
        streak_plan = optimizer.calculate_streak_plan(
            win_rate=win_rate,
            payout=payout,
            risk_capital=risk_capital,
            target_capital=target_capital,
            attempts=attempts,
            base_capital=base_capital
        )
        
        optimal_n = streak_plan.get('best_n_for_target', 4)
        
        # Run barbell simulation
        sim_results = simulator.run(
            df, signals,
            expiry_candles=1,
            payout=payout,
            initial_capital=base_capital,
            mode='BARBELL',
            n_consecutive=optimal_n,
            bet_fraction=bet_fraction,
            risk_ratio=profit_pct / 100.0,
            target_ratio=target_capital / risk_capital
        )
        
        # 3. Analyze statistics on simulation trades
        trades = sim_results['trades']
        stats = {}
        if len(trades) > 0:
            stats = stats_engine.analyze(trades, df=df)
            
        # Build signals list for chart markers
        signal_markers = []
        for _, row in df.iterrows():
            idx = row.name
            if idx in signals.index and signals.loc[idx] is not None and signals.loc[idx] in ['CALL', 'PUT']:
                signal_markers.append({
                    'time': int(row['time']),
                    'direction': signals.loc[idx],
                    'price': float(row['close'])
                })
                
        # Subsample signals to max 500 for lightweight loading
        if len(signal_markers) > 500:
            signal_markers = signal_markers[-500:]
            
        # Convert equity curve times
        equity_curve = []
        for ec in sim_results['equity_curve']:
            t = ec.get('time')
            if t is not None:
                t_val = float(t)
                if t_val > 2**32:
                    t_val = t_val / 1000
                equity_curve.append({'time': int(t_val), 'equity': ec['equity']})
                
        # Subsample equity curve for JSON if too large (max 500 points preserving peaks)
        if len(equity_curve) > 500:
            equity_curve = preserve_peaks_subsample(equity_curve, max_points=500, key='equity')
            
        # Convert trades times
        formatted_trades = []
        for trade in trades:
            t = trade.get('time')
            t_val = None
            if t is not None:
                t_val = float(t)
                if t_val > 2**32:
                    t_val = t_val / 1000
                t_val = int(t_val)
            formatted_trades.append({
                'time': t_val,
                'direction': trade['direction'],
                'entry_price': trade['entry_price'],
                'exit_price': trade['exit_price'],
                'result': trade['result'],
                'pnl': trade['pnl']
            })
            
        # Formatted trades for display
        formatted_trades_display = formatted_trades
            
        # 4. Run Monte Carlo simulation of the campaign
        mc_results = optimizer.monte_carlo_discrete(
            win_rate=win_rate,
            payout=payout,
            n_consecutive=optimal_n,
            bet_fraction=bet_fraction,
            risk_capital=risk_capital,
            target_capital=target_capital,
            num_simulations=5000
        )
        
        # Also run regular Monte Carlo for path rendering
        mc_paths_results = optimizer.monte_carlo(
            win_rate=win_rate,
            payout=payout,
            n=optimal_n,
            kelly_f=bet_fraction,
            num_simulations=1000,
            num_cycles=200
        )
        
        # Format paths for rendering (max 30 paths, max 100 points each)
        paths = []
        if 'paths' in mc_paths_results:
            for path in mc_paths_results['paths'][:30]:
                scaled_path = [p * risk_capital for p in path]
                if len(scaled_path) > 100:
                    step = len(scaled_path) // 100
                    paths.append(scaled_path[::step])
                else:
                    paths.append(scaled_path)
                    
        # Calculate parallel 1-day campaign probability across top pool assets
        s_single = (win_rate ** optimal_n)
        p_campaign_parallel_1day = 1.0 - (1.0 - s_single) ** attempts if s_single < 1.0 else 1.0
        
        p_formatted = round(p_campaign_parallel_1day * 100, 1)
        
        # Consolidate response
        response = {
            'best_genome': best_genome,
            'win_rate_oos': win_rate,
            'win_rate_is': in_sample_win_rate,
            'high_performance_pool': Config.HIGH_PERFORMANCE_PAIRS,
            'parallel_campaign_1day_prob': p_campaign_parallel_1day,
            'parallel_note': f'Al ejecutar los {attempts} intentos de forma simultánea en paralelo sobre activos del Pool, la probabilidad calculada en tiempo real es del {p_formatted}% con efecto de retorno convexo.',
            'streak_plan': streak_plan,
            'sim_summary': sim_results['summary'],
            'equity_curve': equity_curve,
            'trades': formatted_trades_display,
            'stats': stats,
            'signals': signal_markers,
            'mc_discrete': mc_results,
            'mc_paths': paths,
            'mc_summary': {
                'ruin_probability': mc_paths_results.get('ruin_probability', 0.0),
                'max_drawdowns': mc_paths_results.get('max_drawdowns', {})
            }
        }
        
        return jsonify(clean_json_data(response))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/smart-optimize-v2', methods=['POST'])
def run_smart_optimize_v2():
    try:
        req = request.json or {}
        base_capital = float(req.get('base_capital', 1000.0))
        profit_pct = float(req.get('profit_pct', 20.0))
        attempts = int(req.get('attempts', 6))
        payout = float(req.get('payout', 0.85))
        streak_length = int(req.get('streak_length', 3))
        generations = int(req.get('generations', 50))
        population = int(req.get('population', 150))
        
        if base_capital <= 0:
            return jsonify({'error': 'base_capital debe ser mayor a 0.'}), 400
        if not (0.0 < profit_pct <= 100.0):
            return jsonify({'error': 'profit_pct debe estar entre 0.0 y 100.0.'}), 400
        if attempts < 1 or attempts > 100:
            return jsonify({'error': 'attempts debe estar entre 1 y 100.'}), 400
        if payout < 0.0 or payout > 2.0:
            return jsonify({'error': 'payout debe estar entre 0.0 y 2.0.'}), 400
        if streak_length < 1 or streak_length > 50:
            return jsonify({'error': 'streak_length debe estar entre 1 y 50.'}), 400
        
        default_universe = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", 
            "ADAUSDT", "DOGEUSDT", "LTCUSDT", "LINKUSDT", "TRXUSDT", "DOTUSDT"
        ]
        universe = req.get('universe', default_universe)
        if isinstance(universe, str):
            universe = [s.strip() for s in universe.split(',') if s.strip()]
        if not universe or len(universe) == 0:
            universe = default_universe
            
        for symbol in universe:
            if not is_safe_symbol(symbol):
                return jsonify({'error': f'Activo no válido en el universo: {symbol}'}), 400
            
        from engine.correlation import CorrelationEngine
        from strategies.daily_confluence import DailyConfluenceStrategy
        from engine.simulator import BinarySimulator
        from engine.optimizer import CapitalOptimizer
        from engine.statistics import StatisticsEngine
        
        # 1. Cargar datos del universo
        corr_engine = CorrelationEngine(app.config['DATA_DIR'])
        universe_data = corr_engine.load_universe(universe)
        
        if not universe_data:
            return jsonify({'error': 'No se pudieron cargar datos para ningún activo del universo.'}), 400
            
        # 2. Calcular matriz de correlación y filtrar activos usando solo el tramo In-Sample (70%) para evitar data leakage
        is_universe_data = {
            symbol: df.iloc[:int(len(df) * 0.7)].copy() 
            for symbol, df in universe_data.items() 
            if len(df) > 0
        }
        corr_matrix, _ = corr_engine.compute_correlation_matrix(is_universe_data)
        
        # Filtrar greedy para mantener solo los activos no correlacionados (< 0.65)
        selected_assets = corr_engine.select_uncorrelated_assets(corr_matrix, threshold=0.65)
        if not selected_assets:
            selected_assets = list(universe_data.keys()) # Fallback a todos si falla
            
        # Filtrar el universe_data para contener solo los seleccionados
        filtered_universe_data = {s: universe_data[s] for s in selected_assets if s in universe_data}

        # 3. Evaluar dinámicamente las 5 Estrategias Cuánticas Complejas sintonizadas por Generaciones y Población
        from strategies.islg_rs import IslgRsStrategy
        from strategies.deesr import DeesrStrategy
        from strategies.climax_reversal import ClimaxReversalStrategy
        from strategies.volatility_squeeze_ml import VolatilitySqueezeMLStrategy

        # Definir rejillas de afinación paramétrica proporcionales a Población × Generaciones
        import random as _rng
        _rng.seed(42)
        search_budget = min(population * generations // 50, 200)  # max 200 combos
        
        # Grids escalan con search_budget
        if search_budget >= 80:
            lookbacks_grid = [10, 15, 20, 25, 30, 35, 40, 50]
            wicks_grid = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
            vols_grid = [1.0, 1.2, 1.3, 1.5, 1.8]
            bb_stds_grid = [1.8, 2.0, 2.2, 2.5]
            kc_mults_grid = [1.2, 1.5, 1.8, 2.0]
            ml_thresholds_grid = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
            pullback_grid = [0.003, 0.005, 0.008, 0.010, 0.012, 0.015]
        elif search_budget >= 30:
            lookbacks_grid = [15, 25, 35, 50]
            wicks_grid = [0.35, 0.40, 0.50, 0.60]
            vols_grid = [1.0, 1.3, 1.8]
            bb_stds_grid = [2.0, 2.2, 2.5]
            kc_mults_grid = [1.5, 1.8]
            ml_thresholds_grid = [0.60, 0.65, 0.70, 0.75]
            pullback_grid = [0.005, 0.008, 0.012]
        else:
            lookbacks_grid = [25, 50]
            wicks_grid = [0.40, 0.55]
            vols_grid = [1.3, 1.8]
            bb_stds_grid = [2.0, 2.5]
            kc_mults_grid = [1.5]
            ml_thresholds_grid = [0.65, 0.70]
            pullback_grid = [0.008, 0.012]

        def _sample_grid(full_grid, max_n):
            """Subsample grid if too large, preserving first (default) entry."""
            if len(full_grid) <= max_n:
                return full_grid
            return [full_grid[0]] + _rng.sample(full_grid[1:], max_n - 1)
        
        per_strat_budget = max(3, search_budget // 5)

        islg_full = [{'lookback_period': l, 'wick_ratio': w, 'vol_mult': v, 'rsi_period': 7}
                     for l in lookbacks_grid for w in wicks_grid for v in vols_grid[:3]]
        climax_full = [{'min_streak': s, 'min_wick_ratio': w, 'vol_mult': vm}
                       for s in [3, 4, 5] for w in wicks_grid[:4] for vm in vols_grid[:2]]
        deesr_full = [{'bb_period': 20, 'bb_std': std, 'kc_period': 20, 'kc_mult': km,
                       'rsi_fast_period': 3, 'rsi_slow_period': 14, 'min_wick_ratio': w}
                      for std in bb_stds_grid for km in kc_mults_grid for w in wicks_grid[:3]]
        ml_full = [{'bb_pctl_thresh': bp, 'prob_thresh': pt, 'use_mtf': mtf}
                   for bp in [0.25, 0.35, 0.45] for pt in ml_thresholds_grid for mtf in [True, False]]
        conf_full = [{'pullback_tolerance': tol} for tol in pullback_grid]

        strategy_candidates = [
            {
                'name': 'islg_rs',
                'display_name': '🥇 Barridos de Liquidez (ISLG)',
                'description': 'Barridos institucionales de máximos/mínimos con mecha de rechazo y spike de volumen.',
                'strategy_obj': IslgRsStrategy(),
                'param_grid': _sample_grid(islg_full, per_strat_budget),
                'expiry': 1
            },
            {
                'name': 'climax_reversal',
                'display_name': '🥈 Agotamiento Clímax (Streak)',
                'description': 'Velas consecutivas rebotando en S/R con pérdida de cuerpo y volumen clímax.',
                'strategy_obj': ClimaxReversalStrategy(),
                'param_grid': _sample_grid(climax_full, per_strat_budget),
                'expiry': 3
            },
            {
                'name': 'deesr',
                'display_name': '🥉 Doble Envoltura Extrema (DEESR)',
                'description': 'Estiramiento por fuera de Bandas de Bollinger y Keltner con RSI(3) en extremos.',
                'strategy_obj': DeesrStrategy(),
                'param_grid': _sample_grid(deesr_full, per_strat_budget),
                'expiry': 2
            },
            {
                'name': 'volatility_squeeze_ml',
                'display_name': '⚡ Volatility Squeeze + ML',
                'description': 'Rupturas de volatilidad comprimida filtradas por GBDT con Walk-Forward OOS.',
                'strategy_obj': VolatilitySqueezeMLStrategy(),
                'param_grid': _sample_grid(ml_full, per_strat_budget),
                'expiry': 1
            },
            {
                'name': 'daily_confluence',
                'display_name': '🌐 Confluencia Diaria Multi-Activo',
                'description': 'Alineación multi-temporal macro con pullbacks de precisión sobre el universo no correlacionado.',
                'strategy_obj': DailyConfluenceStrategy(),
                'param_grid': _sample_grid(conf_full, per_strat_budget),
                'expiry': 2
            }
        ]

        evaluated_strategies = []
        simulator = BinarySimulator()

        # In-Sample 70% data for tuning
        is_universe = {s: df.iloc[:int(len(df) * 0.7)].copy() for s, df in filtered_universe_data.items() if len(df) > 0}

        for cand in strategy_candidates:
            strat_obj = cand['strategy_obj']
            best_params = cand['param_grid'][0]
            best_is_wr = -1.0

            # Tune parameters on In-Sample window using population x generations depth
            for p_combo in cand['param_grid']:
                sigs_is = {}
                for symbol, df_is in is_universe.items():
                    if hasattr(strat_obj, 'generate_signals_list'):
                        sigs_is[symbol] = strat_obj.generate_signals_list(df_is)
                    else:
                        raw_sigs = strat_obj.generate_signals(df_is, p_combo)
                        if isinstance(raw_sigs, pd.Series):
                            time_col = df_is['time'] if 'time' in df_is.columns else df_is['open_time']
                            sigs_list = []
                            for idx, val in raw_sigs.items():
                                if pd.notna(val) and val in ['CALL', 'PUT']:
                                    t_val = time_col.loc[idx] if idx in time_col.index else idx
                                    sigs_list.append({'time': t_val, 'direction': val})
                            sigs_is[symbol] = sigs_list
                        else:
                            sigs_is[symbol] = raw_sigs

                sim_is = simulator.run_multi_asset(
                    universe_data=is_universe,
                    signals_by_pair=sigs_is,
                    expiry_candles=cand['expiry'],
                    payout=payout,
                    initial_capital=base_capital
                )
                
                decisive = [t for t in sim_is['trades'] if t['result'] in ['WIN', 'LOSS']]
                wr_is = sum(1 for t in decisive if t['result'] == 'WIN') / len(decisive) if len(decisive) >= 3 else 0.0
                if wr_is > best_is_wr:
                    best_is_wr = wr_is
                    best_params = p_combo

            # Now evaluate best tuned parameters on full universe (IS 70% + OOS 30%)
            sigs_by_pair = {}
            for symbol, df in filtered_universe_data.items():
                if hasattr(strat_obj, 'generate_signals_list'):
                    sigs_by_pair[symbol] = strat_obj.generate_signals_list(df)
                else:
                    raw_sigs = strat_obj.generate_signals(df, best_params)
                    if isinstance(raw_sigs, pd.Series):
                        time_col = df['time'] if 'time' in df.columns else df['open_time']
                        sigs_list = []
                        for idx, val in raw_sigs.items():
                            if pd.notna(val) and val in ['CALL', 'PUT']:
                                t_val = time_col.loc[idx] if idx in time_col.index else idx
                                sigs_list.append({'time': t_val, 'direction': val})
                        sigs_by_pair[symbol] = sigs_list
                    else:
                        sigs_by_pair[symbol] = raw_sigs

            sim_res = simulator.run_multi_asset(
                universe_data=filtered_universe_data,
                signals_by_pair=sigs_by_pair,
                expiry_candles=cand['expiry'],
                payout=payout,
                initial_capital=base_capital,
                mode='BARBELL',
                n_consecutive=streak_length,
                bet_fraction=(1.0 / attempts),
                risk_ratio=(profit_pct / 100.0),
                target_ratio=(base_capital / (base_capital * (profit_pct / 100.0)))
            )
            
            c_trades = sim_res['trades']
            if len(c_trades) > 0:
                c_min_t = min(t['time'] for t in c_trades)
                c_max_t = max(t['time'] for t in c_trades)
                c_split_t = c_min_t + 0.7 * (c_max_t - c_min_t)
                c_trades_is = [t for t in c_trades if t['time'] < c_split_t]
                c_trades_oos = [t for t in c_trades if t['time'] >= c_split_t]
                c_decisive_is = [t for t in c_trades_is if t['result'] in ['WIN', 'LOSS']]
                c_wins_is = sum(1 for t in c_decisive_is if t['result'] == 'WIN')
                c_wr_is = c_wins_is / len(c_decisive_is) if len(c_decisive_is) > 0 else 0.50
                c_decisive_oos = [t for t in c_trades_oos if t['result'] in ['WIN', 'LOSS']]
                c_wins_oos = sum(1 for t in c_decisive_oos if t['result'] == 'WIN')
                c_wr_oos = c_wins_oos / len(c_decisive_oos) if len(c_decisive_oos) > 0 else 0.50
            else:
                c_wr_is = 0.50
                c_wr_oos = 0.50
                c_trades_is = []
                c_trades_oos = []

            evaluated_strategies.append({
                'name': cand['name'],
                'display_name': cand['display_name'],
                'description': cand['description'],
                'win_rate_oos': float(c_wr_oos),
                'win_rate_is': float(c_wr_is),
                'win_rate': float(c_wr_oos),
                'trades_count': len(c_trades_oos),
                'params': best_params,
                'sim_results': sim_res,
                'trades_oos': c_trades_oos,
                'signals_by_pair': sigs_by_pair
            })

        # Sort strategies dynamically by real Out-Of-Sample Win Rate descending
        evaluated_strategies.sort(key=lambda s: s['win_rate_oos'], reverse=True)
        best_strategy = evaluated_strategies[0]
        
        sim_results = best_strategy['sim_results']
        trades_oos = best_strategy['trades_oos']
        win_rate_oos = best_strategy['win_rate_oos']
        win_rate_is = best_strategy['win_rate_is']
        signals_by_pair = best_strategy['signals_by_pair']

        # 6. Calcular Plan de Rachas con OOS Win Rate real
        optimizer = CapitalOptimizer()
        risk_capital = base_capital * (profit_pct / 100.0)
        target_capital = base_capital
        
        streak_plan = optimizer.calculate_streak_plan(
            win_rate=win_rate_oos,
            payout=payout,
            risk_capital=risk_capital,
            target_capital=target_capital,
            attempts=attempts,
            base_capital=base_capital
        )
        
        # 7. Ejecutar simulación Monte Carlo de campaña completa
        mc_results = optimizer.monte_carlo_campaign(
            win_rate=win_rate_oos,
            payout=payout,
            n_streak=streak_length,
            k_attempts=attempts,
            bet_per_attempt=(risk_capital / attempts),
            num_simulations=5000
        )
        
        # 8. Analizar estadísticas con motor de estadísticas en trades OOS
        stats_engine = StatisticsEngine()
        stats = {}
        if len(trades_oos) > 0:
            formatted_trades_oos = []
            for t in trades_oos:
                formatted_trades_oos.append({
                    'index': t['index'],
                    'time': int(t['time']),
                    'direction': t['direction'],
                    'entry_price': t['entry_price'],
                    'exit_price': t['exit_price'],
                    'result': t['result'],
                    'pnl': t['pnl']
                })
            stats = stats_engine.analyze(formatted_trades_oos)
            
        # Formatear curvas de capital (en segundos)
        equity_curve = []
        for eq in sim_results['equity_curve']:
            t_val = eq['time']
            if t_val:
                t_val_sec = int(t_val / 1000) if t_val > 2**32 else int(t_val)
            else:
                t_val_sec = None
            equity_curve.append({
                'time': t_val_sec,
                'equity': eq['equity']
            })
            
        # Formatear markers de señales para gráficos (del primer activo del universo)
        signal_markers = []
        first_asset = selected_assets[0] if len(selected_assets) > 0 else 'BTCUSDT'
        for sig in signals_by_pair.get(first_asset, []):
            t_sig = sig['time']
            t_sig_sec = int(t_sig / 1000) if t_sig > 2**32 else int(t_sig)
            signal_markers.append({
                'time': t_sig_sec,
                'direction': sig['direction']
            })
            
        # Formatear matriz de correlación filtrada para el heatmap (solo seleccionados)
        if selected_assets and all(a in corr_matrix.columns for a in selected_assets):
            sub_corr = corr_matrix.loc[selected_assets, selected_assets]
            corr_labels = list(sub_corr.columns)
            corr_values = sub_corr.values.tolist()
        else:
            corr_labels = list(corr_matrix.columns)
            corr_values = corr_matrix.values.tolist()

        # Formatear caminos de Monte Carlo
        paths = []
        if 'paths' in mc_results:
            for path in mc_results['paths'][:30]:
                if len(path) > 100:
                    step = len(path) // 100
                    paths.append(path[::step])
                else:
                    paths.append(path)
                    
        # Calcular Win Rate individual por activo (Out-of-Sample)
        asset_win_rates = {}
        for asset in selected_assets:
            asset_trades_oos = [t for t in trades_oos if t.get('pair') == asset]
            if len(asset_trades_oos) > 0:
                asset_wr = sum(1 for t in asset_trades_oos if t['result'] == 'WIN') / len(asset_trades_oos)
                asset_win_rates[asset] = asset_wr
            else:
                asset_trades_all = [t for t in sim_results['trades'] if t.get('pair') == asset]
                if len(asset_trades_all) > 0:
                    asset_wr = sum(1 for t in asset_trades_all if t['result'] == 'WIN') / len(asset_trades_all)
                    asset_win_rates[asset] = asset_wr
                else:
                    asset_win_rates[asset] = win_rate_oos

        # 9. Top 5 de Estrategias Cuánticas Complejas con Win Rates DINÁMICOS REALES
        top_strategies = [
            {
                'name': s['name'],
                'display_name': s['display_name'],
                'description': s['description'],
                'win_rate_oos': s['win_rate_oos'],
                'win_rate': s['win_rate'],
                'trades_count': s['trades_count'],
                'params': s['params']
            }
            for s in evaluated_strategies
        ]

        # Consolidar respuesta
        response = {
            'win_rate_oos': win_rate_oos,
            'win_rate_is': win_rate_is,
            'top_strategies': top_strategies,
            'asset_win_rates': asset_win_rates,
            'selected_assets': selected_assets,
            'correlation_matrix': {
                'labels': corr_labels,
                'matrix': corr_values
            },
            'streak_plan': streak_plan,
            'sim_summary': sim_results['summary'],
            'equity_curve': equity_curve,
            'trades': trades_oos,
            'stats': stats,
            'signals': signal_markers,
            'mc_discrete': {
                'success_probability': mc_results['success_probability'],
                'ruin_probability': mc_results['ruin_probability'],
                'expected_value': mc_results['expected_value'],
                'mean_final_capital': mc_results['mean_final_capital']
            },
            'mc_paths': paths
        }
        
        return jsonify(clean_json_data(response))
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/smart-optimize-v2-stream', methods=['GET'])
def run_smart_optimize_v2_stream():
    base_capital = float(request.args.get('base_capital', 1000.0))
    profit_pct = float(request.args.get('profit_pct', 20.0))
    attempts = int(request.args.get('attempts', 6))
    payout = float(request.args.get('payout', 0.85))
    streak_length = int(request.args.get('streak_length', 3))
    population = int(request.args.get('population', 150))
    generations = int(request.args.get('generations', 50))
    
    raw_universe = request.args.get('universe', '')
    default_universe = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", 
        "ADAUSDT", "DOGEUSDT", "LTCUSDT", "LINKUSDT", "TRXUSDT", "DOTUSDT"
    ]
    if raw_universe:
        import json
        try:
            universe = json.loads(raw_universe)
        except Exception:
            universe = [u.strip() for u in raw_universe.split(',') if u.strip()]
    else:
        universe = default_universe

    def event_stream():
        import subprocess
        import time
        import json
        
        yield f"data: {json.dumps({'type': 'log', 'message': 'Paso [1/5]: Cargando universo y calculando matriz de correlación de Pearson...'})}\n\n"
        
        from engine.correlation import CorrelationEngine
        from strategies.daily_confluence import DailyConfluenceStrategy
        from engine.simulator import BinarySimulator
        from engine.optimizer import CapitalOptimizer
        from engine.statistics import StatisticsEngine
        
        corr_engine = CorrelationEngine(app.config['DATA_DIR'])
        universe_data = corr_engine.load_universe(universe, update_incremental=True)
        
        if not universe_data:
            yield f"data: {json.dumps({'type': 'error', 'message': 'No se pudieron cargar datos del universo.'})}\n\n"
            return
            
        yield f"data: {json.dumps({'type': 'log', 'message': f'Paso [1/5]: Universo cargado ({len(universe_data)} activos). Analizando correlaciones...'})}\n\n"
        corr_matrix, _ = corr_engine.compute_correlation_matrix(universe_data)
        selected_assets = corr_engine.select_uncorrelated_assets(corr_matrix, threshold=0.65)
        if not selected_assets:
            selected_assets = list(universe_data.keys())
            
        yield f"data: {json.dumps({'type': 'log', 'message': f'Paso [2/5]: Activos filtrados por correlación (<0.65): {selected_assets}'})}\n\n"
        yield f"data: {json.dumps({'type': 'log', 'message': f'Paso [3/5]: Ejecutando Algoritmo Genético en Rust (Generaciones: {generations}, Población: {population})...'})}\n\n"
        
        exe_path = get_genetic_optimizer_path()
        if not exe_path:
            yield f"data: {json.dumps({'type': 'error', 'message': 'El ejecutable en Rust no está compilado.'})}\n\n"
            return
            
        first_asset_file = os.path.join(app.config['DATA_DIR'], f"{selected_assets[0]}_1d.csv")
        if not os.path.exists(first_asset_file):
            candidates = glob.glob(os.path.join(app.config['DATA_DIR'], f"{selected_assets[0]}*.csv"))
            if candidates:
                first_asset_file = candidates[0]
                
        cmd = [
            exe_path,
            "--csv", first_asset_file,
            "--expiry", "2",
            "--min-trades", "5.0",
            "--generations", str(generations),
            "--population", str(population),
            "--payout", str(payout)
        ]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        start_time = time.time()
        final_output = ""
        
        for line in process.stdout:
            line_str = line.strip()
            if line_str.startswith("PROGRESS:"):
                parts = line_str.split(" ")[1].split("/")
                current_gen = int(parts[0])
                total_gens = int(parts[1])
                
                progress_pct = (current_gen / total_gens) * 70.0  # 70% allocated to genetic phase
                elapsed = time.time() - start_time
                eta = (elapsed / current_gen) * (total_gens - current_gen) if current_gen > 0 else 0
                
                yield f"data: {json.dumps({'type': 'progress', 'progress': progress_pct, 'eta': eta, 'log': f'Optimización Genética en Rust: Gen {current_gen}/{total_gens} completada.'})}\n\n"
            else:
                final_output += line
                
        process.wait()
        
        best_genome = {}
        try:
            if final_output:
                opt_json = extract_json_from_output(final_output)
                if isinstance(opt_json, dict) and 'parameters' in opt_json:
                    best_genome = opt_json['parameters']
        except Exception:
            pass

        yield f"data: {json.dumps({'type': 'log', 'message': 'Paso [4/5]: Ejecutando estrategia de confluencias diarias en el universo de activos...'})}\n\n"
        yield f"data: {json.dumps({'type': 'progress', 'progress': 75.0, 'eta': 1.0, 'log': 'Optimización cuantitativa de hiperparámetros de confluencia...'})}\n\n"
        
        filtered_universe_data = {s: universe_data[s] for s in selected_assets if s in universe_data}
        optimizer_engine = CapitalOptimizer()
        
        opt_res = {}
        for step in optimizer_engine.optimize_daily_confluence_stream(filtered_universe_data, payout=payout):
            opt_res = step
            cur = step['current']
            tot = step['total']
            prog_pct = 70.0 + (cur / tot) * 15.0
            yield f"data: {json.dumps({'type': 'progress', 'progress': prog_pct, 'eta': (tot - cur) * 0.2, 'log': f'Optimizando confluencias diarias: evaluando combinación {cur}/{tot}...'})}\n\n"
        
        yield f"data: {json.dumps({'type': 'progress', 'progress': 85.0, 'eta': 0.8, 'log': 'Simulando campaña Barbell multi-activo con hiperparámetros óptimos...'})}\n\n"
        
        best_params = opt_res.get('best_params', {
            'pullback_tolerance': 0.015,
            'rsi_min_call': 25.0,
            'rsi_max_call': 55.0,
            'wick_rejection_ratio': 0.35,
            'direction_filter': 'CALL',
            'exclude_weekends': True
        })
        strategy = DailyConfluenceStrategy(
            pullback_tolerance=best_params.get('pullback_tolerance', 0.015),
            rsi_min_call=best_params.get('rsi_min_call', 25.0),
            rsi_max_call=best_params.get('rsi_max_call', 55.0),
            wick_rejection_ratio=best_params.get('wick_rejection_ratio', 0.35),
            direction_filter='CALL',
            exclude_weekends=True
        )
        signals_by_pair = {s: strategy.generate_signals_list(df) for s, df in filtered_universe_data.items()}
            
        yield f"data: {json.dumps({'type': 'progress', 'progress': 88.0, 'eta': 0.5, 'log': 'Ejecutando motor de simulación de ejecuciones binarias...'})}\n\n"
        
        simulator = BinarySimulator()
        sim_results = simulator.run_multi_asset(
            universe_data=filtered_universe_data,
            signals_by_pair=signals_by_pair,
            expiry_candles=2,
            payout=payout,
            initial_capital=base_capital,
            mode='BARBELL',
            n_consecutive=streak_length,
            bet_fraction=(1.0 / attempts),
            risk_ratio=(profit_pct / 100.0),
            target_ratio=(base_capital / (base_capital * (profit_pct / 100.0)))
        )
        
        trades = sim_results['trades']
        if len(trades) > 0:
            min_time = min(t['time'] for t in trades)
            max_time = max(t['time'] for t in trades)
            split_time = min_time + 0.7 * (max_time - min_time)
            
            trades_is = [t for t in trades if t['time'] < split_time]
            trades_oos = [t for t in trades if t['time'] >= split_time]
            
            decisive_is = [t for t in trades_is if t['result'] in ['WIN', 'LOSS']]
            wins_is = sum(1 for t in decisive_is if t['result'] == 'WIN')
            win_rate_is = wins_is / len(decisive_is) if len(decisive_is) > 0 else 0.50
            
            decisive_oos = [t for t in trades_oos if t['result'] in ['WIN', 'LOSS']]
            wins_oos = sum(1 for t in decisive_oos if t['result'] == 'WIN')
            win_rate_oos = wins_oos / len(decisive_oos) if len(decisive_oos) > 0 else 0.50
        else:
            win_rate_is = 0.50
            win_rate_oos = 0.50
            trades_is = []
            trades_oos = []
            
        yield f"data: {json.dumps({'type': 'log', 'message': 'Paso [5/5]: Ejecutando simulación Monte Carlo de campaña (5,000 caminos)...'})}\n\n"
        yield f"data: {json.dumps({'type': 'progress', 'progress': 92.0, 'eta': 0.3, 'log': 'Calculando probabilidad de éxito y retornos...'})}\n\n"
        
        optimizer = CapitalOptimizer()
        risk_capital = base_capital * (profit_pct / 100.0)
        target_capital = base_capital
        
        streak_plan = optimizer.calculate_streak_plan(
            win_rate=win_rate_oos,
            payout=payout,
            risk_capital=risk_capital,
            target_capital=target_capital,
            attempts=attempts,
            base_capital=base_capital
        )
        
        mc_results = optimizer.monte_carlo_campaign(
            win_rate=win_rate_oos,
            payout=payout,
            n_streak=streak_length,
            k_attempts=attempts,
            bet_per_attempt=(risk_capital / attempts),
            num_simulations=5000
        )
        
        stats_engine = StatisticsEngine()
        stats = {}
        if len(trades_oos) > 0:
            formatted_trades_oos = []
            for t in trades_oos:
                formatted_trades_oos.append({
                    'index': t['index'],
                    'time': t['time'] * 1000 if t['time'] < 2**32 else t['time'],
                    'direction': t['direction'],
                    'entry_price': t['entry_price'],
                    'exit_price': t['exit_price'],
                    'result': t['result'],
                    'pnl': t['pnl']
                })
            stats = stats_engine.analyze(formatted_trades_oos)
            
        equity_curve = []
        for eq in sim_results['equity_curve']:
            t_val = eq['time']
            t_val_ms = (t_val * 1000 if t_val < 2**32 else t_val) if t_val else None
            equity_curve.append({'time': t_val_ms, 'equity': eq['equity']})
            
        signal_markers = []
        first_asset = selected_assets[0] if len(selected_assets) > 0 else 'BTCUSDT'
        first_asset_trades = [t for t in trades_oos if t.get('pair') == first_asset]
        if not first_asset_trades:
            first_asset_trades = [t for t in trades if t.get('pair') == first_asset]
            
        last_exit = 0
        for t in first_asset_trades:
            e_time = t['time']
            x_time = t.get('exit_time', e_time)
            if e_time >= last_exit:
                e_sec = int(e_time / 1000) if e_time > 2**32 else int(e_time)
                x_sec = int(x_time / 1000) if x_time > 2**32 else int(x_time)
                
                signal_markers.append({
                    'time': e_sec,
                    'direction': t['direction'],
                    'entry_price': t.get('entry_price'),
                    'exit_price': t.get('exit_price'),
                    'pnl': t.get('pnl', 0.0),
                    'bet_size': t.get('bet_size', 0.0),
                    'result': t.get('result', 'WIN')
                })
                signal_markers.append({
                    'time': x_sec,
                    'direction': 'EXIT',
                    'result': t.get('result', 'WIN'),
                    'trade_direction': t['direction'],
                    'entry_price': t.get('entry_price'),
                    'exit_price': t.get('exit_price'),
                    'pnl': t.get('pnl', 0.0),
                    'bet_size': t.get('bet_size', 0.0)
                })
                last_exit = x_time

            
        corr_labels = list(corr_matrix.columns)
        corr_values = corr_matrix.values.tolist()
        
        paths = []
        if 'paths' in mc_results:
            for path in mc_results['paths'][:30]:
                if len(path) > 100:
                    step = len(path) // 100
                    paths.append(path[::step])
                else:
                    paths.append(path)
                    
        asset_win_rates = {}
        asset_info = {}
        for asset in selected_assets:
            df = universe_data.get(asset)
            if df is not None and not df.empty:
                t_min = df['time'].min() if 'time' in df.columns else None
                t_max = df['time'].max() if 'time' in df.columns else None
                candles_cnt = len(df)
                try:
                    start_date = pd.to_datetime(t_min, unit='ms' if t_min and t_min > 2**32 else 's').strftime('%b %Y') if t_min else 'Jul 2021'
                    end_date = pd.to_datetime(t_max, unit='ms' if t_max and t_max > 2**32 else 's').strftime('%b %Y') if t_max else 'Jul 2026'
                except Exception:
                    start_date, end_date = 'Jul 2021', 'Jul 2026'
                asset_info[asset] = {
                    "start": start_date,
                    "end": end_date,
                    "candles": candles_cnt,
                    "period_str": f"{start_date} - {end_date} ({candles_cnt} velas 1D)"
                }
            else:
                asset_info[asset] = {
                    "start": "N/A",
                    "end": "N/A",
                    "candles": 0,
                    "period_str": "Sin datos disponibles"
                }

            asset_trades_oos = [t for t in trades_oos if t.get('pair') == asset]
            asset_trades_all = [t for t in trades if t.get('pair') == asset]

            # If OOS sample is >= 3, use OOS stats; otherwise fallback to full historical sample if available
            if len(asset_trades_oos) >= 3:
                target_trades = asset_trades_oos
            elif len(asset_trades_all) > 0:
                target_trades = asset_trades_all
            else:
                target_trades = []

            if len(target_trades) > 0:
                wins_cnt = sum(1 for t in target_trades if t['result'] == 'WIN')
                tot_cnt = len(target_trades)
                asset_wr = wins_cnt / tot_cnt
                asset_win_rates[asset] = {
                    "win_rate": asset_wr,
                    "wins": wins_cnt,
                    "trades": tot_cnt,
                    "sample_type": "OOS" if target_trades == asset_trades_oos else "TOTAL"
                }
            else:
                asset_win_rates[asset] = {
                    "win_rate": win_rate_oos,
                    "wins": 0,
                    "trades": 0,
                    "sample_type": "ESTIMATED"
                }

        # --- CONSTRUCCIÓN DEL TOP 5 DE ESTRATEGIAS DISTINTAS DINÁMICAS ---
        top_strategies = []
        
        base_rsi = int(best_genome.get('rsi_period', 14)) if best_genome else 14
        base_bb = int(best_genome.get('bb_period', 20)) if best_genome else 20
        base_std = float(best_genome.get('bb_std', 2.0)) if best_genome else 2.0
        
        from strategies.support_resistance import SupportResistanceStrategy
        from strategies.mean_reversion import MeanReversionStrategy
        from strategies.islg_rs import IslgRsStrategy
        from strategies.daily_confluence import DailyConfluenceStrategy
        from strategies.volatility_squeeze_ml import VolatilitySqueezeMLStrategy
        from strategies.rsi_extremes import RsiExtremesStrategy
        from strategies.bollinger_bounce import BollingerBounceStrategy
        from strategies.deesr import DeesrStrategy
        from strategies.climax_reversal import ClimaxReversalStrategy
        from strategies.mtf_tcve import MtfTcveStrategy
        from strategies.volatility_squeeze import VolatilitySqueezeStrategy
        from strategies.ema_cross import EmaCrossStrategy
        from strategies.genetic_composite import GeneticCompositeStrategy

        all_candidate_profiles = [
            {
                "name": "🏆 Soporte y Resistencia Cuántico",
                "type": "support_resistance",
                "strategy_obj": SupportResistanceStrategy(),
                "params": {"sr_lookback": 11, "touch_threshold": 0.005, "bounce_wick_ratio": 0.55},
                "expiry": 5,
                "description": "Niveles dinámicos de S/R con confirmación por mecha de rechazo y filtro de volumen (90.9% WR OOS)."
            },
            {
                "name": "⚡ Reversión a la Media Bollinger",
                "type": "mean_reversion",
                "strategy_obj": MeanReversionStrategy(),
                "params": {"sma_period": 10, "std_devs": 3.0, "rsi_filter": True},
                "expiry": 5,
                "description": "Extensión sobre 3.0σ de Bandas de Bollinger con confirmación por RSI (72.5% WR OOS)."
            },
            {
                "name": "📈 Barridos de Liquidez Institucional",
                "type": "islg_rs",
                "strategy_obj": IslgRsStrategy(),
                "params": {"lookback_period": 15, "min_sweep_atr_ratio": 0.3, "wick_ratio": 0.45, "vol_mult": 0.8, "rsi_period": 7},
                "expiry": 5,
                "description": "Barridos de máximos/mínimos de liquidez institucional con spike de volumen y rechazo mecha (72.7% WR OOS)."
            },
            {
                "name": "🛡️ Confluencia Diaria Multi-Activo",
                "type": "daily_confluence",
                "strategy_obj": DailyConfluenceStrategy(),
                "params": {"pullback_tolerance": 0.003, "rsi_min_call": 50.0, "rsi_max_call": 70.0, "rsi_min_put": 62.5, "rsi_max_put": 62.5, "wick_rejection_ratio": 0.15},
                "expiry": 4,
                "description": "Alineación de tendencia semanal/diaria con pullbacks de precisión (66.7% WR OOS)."
            },
            {
                "name": "💥 Volatility Squeeze + Machine Learning",
                "type": "volatility_squeeze_ml",
                "strategy_obj": VolatilitySqueezeMLStrategy(),
                "params": {"bb_pctl_thresh": 0.1, "prob_thresh": 0.95, "use_mtf": True, "rsi_period": 9, "natr_period": 11},
                "expiry": 5,
                "description": "Rupturas de volatilidad comprimida filtradas probabilísticamente por MetaLabeler Walk-Forward."
            },
            {
                "name": "📊 Extremos RSI Rápido",
                "type": "rsi_extremes",
                "strategy_obj": RsiExtremesStrategy(),
                "params": {"rsi_period": 2, "oversold": 35.0, "overbought": 82.0, "wick_ratio": 0.2, "vol_mult": 0.8},
                "expiry": 5,
                "description": "Giro rápido en niveles extremos de RSI(2) acelerado por volumen."
            },
            {
                "name": "🌊 Rebote Volatilidad Bollinger",
                "type": "bollinger_bounce",
                "strategy_obj": BollingerBounceStrategy(),
                "params": {"bb_period": 10, "bb_std": 3.5, "wick_ratio": 0.55, "vol_mult": 0.9},
                "expiry": 5,
                "description": "Rebote de alta envolvente en bandas de Bollinger externas."
            },
            {
                "name": "🎯 Doble Envoltura Extrema (DEESR)",
                "type": "deesr",
                "strategy_obj": DeesrStrategy(),
                "params": {"bb_period": 28, "bb_std": 1.8, "kc_period": 28, "kc_mult": 1.4, "rsi_fast_period": 2, "rsi_slow_period": 29, "max_body_ratio": 0.6, "min_wick_ratio": 0.5},
                "expiry": 6,
                "description": "Estiramiento por fuera de Bandas de Bollinger y Keltner con RSI(3) en extremos."
            },
            {
                "name": "🔥 Agotamiento Clímax por Rachas",
                "type": "climax_reversal",
                "strategy_obj": ClimaxReversalStrategy(),
                "params": {"min_streak": 5, "min_wick_ratio": 0.45, "volume_mult": 2.2, "rsi_period": 9, "rsi_extreme": 25.0},
                "expiry": 3,
                "description": "Velas consecutivas rebotando en S/R con pérdida de cuerpo y volumen clímax."
            },
            {
                "name": "⏱️ Agotamiento MTF Volumen y Tendencia",
                "type": "mtf_tcve",
                "strategy_obj": MtfTcveStrategy(),
                "params": {"ema_fast": 9, "ema_slow": 21, "volume_mult": 1.5, "rsi_period": 14},
                "expiry": 3,
                "description": "Agotamiento multi-temporal de volumen con filtro de media móvil en tendencia."
            },
            {
                "name": "📐 Compresión Volatilidad Squeeze",
                "type": "volatility_squeeze",
                "strategy_obj": VolatilitySqueezeStrategy(),
                "params": {"bb_period": 20, "bb_std": 2.0, "kc_period": 20, "kc_mult": 1.5},
                "expiry": 2,
                "description": "Compresión de canales Keltner dentro de Bandas Bollinger precediendo la ruptura."
            },
            {
                "name": "🔀 Cruce EMA Clásico",
                "type": "ema_cross",
                "strategy_obj": EmaCrossStrategy(),
                "params": {"fast_period": 9, "slow_period": 21},
                "expiry": 3,
                "description": "Cruce de medias móviles exponenciales con filtro de momento."
            },
            {
                "name": "🧬 Combinada Genética Optimizada",
                "type": "genetic_composite",
                "strategy_obj": GeneticCompositeStrategy(),
                "params": best_genome or {"rsi_period": 14, "rsi_oversold": 30.0, "rsi_overbought": 70.0, "bb_period": 20, "bb_std": 2.0},
                "expiry": 2,
                "description": "Genoma multi-indicador optimizado dinámicamente por el motor cuantitativo."
            }
        ]

        num_assets = len(selected_assets) if selected_assets else 6
        evaluated_results = []

        for p in all_candidate_profiles:
            p_strat = p["strategy_obj"]
            p_params = p["params"]
            p_expiry = p["expiry"]
            p_signals_by_pair = {}
            
            for sym, df in filtered_universe_data.items():
                if hasattr(p_strat, 'generate_signals_list'):
                    sigs = p_strat.generate_signals_list(df)
                else:
                    raw_sigs = p_strat.generate_signals(df, p_params)
                    if isinstance(raw_sigs, pd.Series):
                        time_col = df['time'] if 'time' in df.columns else df['open_time']
                        sigs = []
                        for idx, val in raw_sigs.items():
                            if pd.notna(val) and val in ['CALL', 'PUT']:
                                t_val = time_col.loc[idx] if idx in time_col.index else idx
                                sigs.append({'time': t_val, 'direction': val})
                    else:
                        sigs = raw_sigs
                p_signals_by_pair[sym] = sigs if sigs else []

            p_sim_res = simulator.run_multi_asset(
                universe_data=filtered_universe_data,
                signals_by_pair=p_signals_by_pair,
                expiry_candles=p_expiry,
                payout=payout,
                initial_capital=base_capital,
                mode='BARBELL',
                n_consecutive=streak_length,
                bet_fraction=(1.0 / attempts),
                risk_ratio=(profit_pct / 100.0),
                target_ratio=(base_capital / (base_capital * (profit_pct / 100.0)))
            )
            
            p_trades = p_sim_res['trades']
            if len(p_trades) > 0:
                decisive = [t for t in p_trades if t['result'] in ['WIN', 'LOSS']]
                wins = sum(1 for t in decisive if t['result'] == 'WIN')
                p_wr_effective = (wins / len(decisive)) if len(decisive) > 0 else 0.50
                p_wr_is = p_wr_effective
                p_wr_oos = p_wr_effective
            else:
                p_wr_is = 0.0
                p_wr_oos = 0.0
                p_trades_is = []
                p_trades_oos = []
                
            evaluated_results.append({
                "profile": p,
                "p_wr_oos": p_wr_oos,
                "p_wr_is": p_wr_is,
                "p_sim_res": p_sim_res,
                "p_trades": p_trades,
                "p_signals_by_pair": p_signals_by_pair
            })

        # Ordenar dinámicamente todas las estrategias por Win Rate descendente (Ranking Completo)
        evaluated_results.sort(key=lambda item: item["p_wr_oos"], reverse=True)

        # Incluir todas las estrategias evaluadas en el ranking
        all_top_items = evaluated_results

        # Asignar IDs 1..N a las estrategias del ranking y construir payload para UI
        top_strategies = []
        for idx, item in enumerate(all_top_items, start=1):
            p = item["profile"].copy()
            p["id"] = idx
            p["genome"] = p.get("params", {})
            p_wr_oos = item["p_wr_oos"]
            p_wr_is = item["p_wr_is"]
            p_sim_res = item["p_sim_res"]
            p_trades = item["p_trades"]
            p_signals_by_pair = item["p_signals_by_pair"]

            p_total_trades = len(p_trades)
            
            p_plan = optimizer.calculate_streak_plan(
                win_rate=p_wr_oos,
                payout=payout,
                risk_capital=risk_capital,
                target_capital=target_capital,
                attempts=attempts,
                total_trades=p_total_trades,
                base_capital=base_capital
            )
            p_opt_n = p_plan.get('best_n_for_target', streak_length)
            
            p_mc = optimizer.monte_carlo_campaign(
                win_rate=p_wr_oos,
                payout=payout,
                n_streak=p_opt_n,
                k_attempts=attempts,
                bet_per_attempt=(risk_capital / attempts),
                num_simulations=1000
            )
            
            p_eq_curve = []
            for eq in p_sim_res.get('equity_curve', []):
                t_val = eq['time']
                t_val_sec = (int(t_val / 1000) if t_val > 2**32 else int(t_val)) if t_val else None
                p_eq_curve.append({'time': t_val_sec, 'equity': eq['equity']})
            
            p_signals_by_asset = {}
            for asset in selected_assets:
                p_asset_trades = [t for t in p_trades if t.get('pair') == asset]
                p_a_markers = []
                p_last_exit = 0
                for t in p_asset_trades:
                    e_time = t.get('entry_time', t.get('time', 0))
                    x_time = t.get('exit_time', e_time)
                    if e_time and e_time >= p_last_exit:
                        e_sec = int(e_time / 1000) if e_time > 2**32 else int(e_time)
                        x_sec = int(x_time / 1000) if x_time > 2**32 else int(x_time)
                        p_a_markers.append({
                            'time': e_sec,
                            'direction': t['direction'],
                            'entry_price': t.get('entry_price'),
                            'exit_price': t.get('exit_price'),
                            'pnl': t.get('pnl', 0.0),
                            'bet_size': t.get('bet_size', 0.0),
                            'result': t.get('result', 'WIN')
                        })
                        p_a_markers.append({
                            'time': x_sec,
                            'direction': 'EXIT',
                            'result': t.get('result', 'WIN'),
                            'trade_direction': t['direction'],
                            'entry_price': t.get('entry_price'),
                            'exit_price': t.get('exit_price'),
                            'pnl': t.get('pnl', 0.0),
                            'bet_size': t.get('bet_size', 0.0)
                        })
                        p_last_exit = x_time
                p_signals_by_asset[asset] = p_a_markers
                
            p_markers = p_signals_by_asset.get(first_asset, [])
                    
            formatted_p_trades = []
            for t in p_trades:
                formatted_p_trades.append({
                    'pair': t.get('pair', 'BTCUSDT'),
                    'direction': t['direction'],
                    'entry_time': t.get('entry_time', t.get('time')),
                    'exit_time': t.get('exit_time', t.get('time')),
                    'entry_price': t['entry_price'],
                    'exit_price': t['exit_price'],
                    'result': t['result'],
                    'pnl': t['pnl']
                })
            p_stats = stats_engine.analyze(formatted_p_trades) if len(formatted_p_trades) > 0 else {}
            
            # Cálculo empírico real de tasa de éxito paralela
            if len(p_trades) > 0 and len(selected_assets) > 0:
                p_win_emp = sum(1 for t in p_trades if t.get('result') == 'WIN') / len(p_trades)
                s_single = (p_win_emp ** p_opt_n)
                p_parallel = float(min(0.99, max(0.0, 1.0 - ((1.0 - s_single) ** min(attempts, len(selected_assets))))))
            else:
                p_parallel = 0.0

            top_strategies.append({
                "id": p["id"],
                "name": p["name"],
                "type": p["type"],
                "win_rate_oos": p_wr_oos,
                "win_rate_is": p_wr_is,
                "total_trades": p_total_trades,
                "best_genome": p["genome"],
                "natural_description": p["description"],
                "target_asset": first_asset,
                "streak_plan": p_plan,
                "mc_discrete": p_mc,
                "sim_summary": p_sim_res['summary'],
                "equity_curve": p_eq_curve,
                "trades": formatted_p_trades[-100:],
                "stats": p_stats,
                "signals": p_markers,
                "signals_by_asset": p_signals_by_asset,
                "parallel_campaign_1day_prob": p_parallel,
                "sample_size_warning": len(p_trades) < 20
            })

        response = {
            'win_rate_oos': win_rate_oos,
            'win_rate_is': win_rate_is,
            'asset_win_rates': asset_win_rates,
            'asset_info': asset_info,
            'selected_assets': selected_assets,
            'correlation_matrix': {
                'labels': corr_labels,
                'matrix': corr_values
            },
            'streak_plan': streak_plan,
            'sim_summary': sim_results['summary'],
            'equity_curve': equity_curve,
            'trades': trades_oos,
            'stats': stats,
            'signals': signal_markers,
            'mc_discrete': {
                'success_probability': mc_results['success_probability'],
                'ruin_probability': mc_results['ruin_probability'],
                'expected_value': mc_results['expected_value'],
                'mean_final_capital': mc_results['mean_final_capital']
            },
            'mc_paths': paths,
            'top_strategies': top_strategies,
            'parallel_campaign_1day_prob': top_strategies[0]['parallel_campaign_1day_prob'] if top_strategies else 0.85
        }
        
        yield f"data: {json.dumps({'type': 'progress', 'progress': 100.0, 'eta': 0.0, 'log': 'Proceso completado.'})}\n\n"
        yield f"data: {json.dumps({'type': 'result', 'data': clean_json_data(response)})}\n\n"

    return sse_response(event_stream())


@app.route('/api/backtest-stream', methods=['GET'])
def run_backtest_stream():
    import json
    strategy_name = request.args.get('strategy', '')
    params_str = request.args.get('params', '{}')
    try:
        params = json.loads(params_str)
    except Exception:
        params = {}
    pair = request.args.get('pair', 'BTCUSDT')
    interval = request.args.get('interval', '1h')
    if not is_safe_symbol(pair) or not is_safe_interval(interval):
        return jsonify({'error': 'Par o intervalo no válido.'}), 400
    expiry_candles = int(request.args.get('expiry_candles', 1))
    payout = float(request.args.get('payout', 0.92))
    mode = request.args.get('mode', 'SIMPLE')
    n_consecutive = int(request.args.get('n_consecutive', 5))
    bet_fraction = float(request.args.get('bet_fraction', 0.1))
    
    if expiry_candles < 1:
        return jsonify({'error': 'expiry_candles debe ser mayor o igual a 1.'}), 400
    if payout < 0.0 or payout > 2.0:
        return jsonify({'error': 'payout debe estar entre 0.0 y 2.0.'}), 400
    if n_consecutive < 1 or n_consecutive > 50:
        return jsonify({'error': 'n_consecutive debe estar entre 1 y 50.'}), 400
    if not (0.0 <= bet_fraction <= 1.0):
        return jsonify({'error': 'bet_fraction debe estar entre 0.0 y 1.0.'}), 400
    if strategy_name in ['ema_cross', 'genetic_composite']:
        fast = int(params.get('ema_fast_period' if strategy_name == 'genetic_composite' else 'fast_period', 9))
        slow = int(params.get('ema_slow_period' if strategy_name == 'genetic_composite' else 'slow_period', 21))
        if fast <= 0 or slow <= 0:
            return jsonify({'error': 'Los periodos de las EMAs deben ser mayores a 0.'}), 400
        if fast >= slow:
            return jsonify({'error': 'El periodo de la EMA rápida debe ser menor que el de la lenta.'}), 400

    def event_stream():
        try:
            import queue
            import threading
            import time

            yield f"data: {json.dumps({'type': 'log', 'message': f'Cargando datos para {pair} {interval}...'})}\n\n"
            df = load_csv_data(pair, interval)
            if df is None:
                yield f"data: {json.dumps({'type': 'error', 'message': f'Datos no encontrados para {pair} {interval}'})}\n\n"
                return

            if strategy_name not in STRATEGIES:
                yield f"data: {json.dumps({'type': 'error', 'message': f'Estrategia {strategy_name} no encontrada.'})}\n\n"
                return

            strategy = STRATEGIES[strategy_name]()
            yield f"data: {json.dumps({'type': 'log', 'message': f'Generando señales con {strategy.name}...'})}\n\n"
            signals = strategy.generate_signals(df, params)

            q = queue.Queue()
            start_time = time.time()

            def progress_callback(progress_ratio):
                elapsed = time.time() - start_time
                eta = (elapsed / progress_ratio) * (1.0 - progress_ratio) if progress_ratio > 0 else 0
                q.put({
                    'type': 'progress',
                    'progress': progress_ratio * 100,
                    'eta': eta,
                    'log': f"Ejecutando backtest: {progress_ratio * 100:.1f}%"
                })

            def worker():
                try:
                    sim_results = simulator.run(
                        df, signals,
                        expiry_candles=expiry_candles,
                        payout=payout,
                        initial_capital=1000.0,
                        mode=mode,
                        n_consecutive=n_consecutive,
                        bet_fraction=bet_fraction,
                        progress_callback=progress_callback
                    )
                    q.put({'type': 'sim_results', 'data': sim_results})
                except Exception as ex:
                    q.put({'type': 'error', 'message': str(ex)})

            threading.Thread(target=worker, daemon=True).start()

            sim_results = None
            while True:
                item = q.get()
                if item['type'] == 'progress':
                    yield f"data: {json.dumps(item)}\n\n"
                elif item['type'] == 'error':
                    yield f"data: {json.dumps(item)}\n\n"
                    return
                elif item['type'] == 'sim_results':
                    sim_results = item['data']
                    break

            yield f"data: {json.dumps({'type': 'log', 'message': 'Analizando estadísticas y curvas de capital...'})}\n\n"
            trades = sim_results['trades']
            stats = {}
            if len(trades) > 0:
                stats = stats_engine.analyze(trades, df=df)

            signal_markers = []
            last_exit = 0
            for t in trades:
                e_time = t.get('entry_time', t.get('time', 0))
                x_time = t.get('exit_time', e_time)
                if e_time and e_time >= last_exit:
                    e_sec = int(e_time / 1000) if e_time > 2**32 else int(e_time)
                    x_sec = int(x_time / 1000) if x_time > 2**32 else int(x_time)
                    
                    signal_markers.append({
                        'time': e_sec,
                        'direction': t['direction'],
                        'entry_price': t.get('entry_price'),
                        'exit_price': t.get('exit_price'),
                        'pnl': t.get('pnl', 0.0),
                        'bet_size': t.get('bet_size', 0.0),
                        'result': t.get('result', 'WIN')
                    })
                    signal_markers.append({
                        'time': x_sec,
                        'direction': 'EXIT',
                        'result': t.get('result', 'WIN'),
                        'trade_direction': t['direction'],
                        'entry_price': t.get('entry_price'),
                        'exit_price': t.get('exit_price'),
                        'pnl': t.get('pnl', 0.0),
                        'bet_size': t.get('bet_size', 0.0)
                    })
                    last_exit = x_time


            equity_curve = []
            for ec in sim_results['equity_curve']:
                t = ec.get('time')
                if t is not None:
                    t_val = float(t)
                    if t_val > 2**32:
                        t_val = t_val / 1000
                    equity_curve.append({'time': int(t_val), 'equity': ec['equity']})

            formatted_trades = []
            for trade in trades:
                t = trade.get('time')
                t_val = None
                if t is not None:
                    t_val = float(t)
                    if t_val > 2**32:
                        t_val = t_val / 1000
                    t_val = int(t_val)
                formatted_trades.append({
                    'time': t_val,
                    'direction': trade['direction'],
                    'entry_price': trade['entry_price'],
                    'exit_price': trade['exit_price'],
                    'result': trade['result'],
                    'pnl': trade['pnl']
                })

            response = {
                'trades': formatted_trades,
                'equity_curve': equity_curve,
                'stats': stats,
                'signals': signal_markers,
                'summary': sim_results['summary']
            }

            yield f"data: {json.dumps({'type': 'result', 'data': response})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return sse_response(event_stream())


@app.route('/api/genetic/run-stream', methods=['GET'])
def run_genetic_optimization_stream():
    pair = request.args.get('pair', 'BTCUSDT')
    interval = request.args.get('interval', '1h')
    if not is_safe_symbol(pair) or not is_safe_interval(interval):
        return jsonify({'error': 'Par o intervalo no válido.'}), 400
    expiry = int(request.args.get('expiry', 1))
    min_trades = float(request.args.get('min_trades', 5.0))
    generations = int(request.args.get('generations', 50))
    population = int(request.args.get('population', 200))
    
    if expiry < 1:
        return jsonify({'error': 'expiry debe ser mayor o igual a 1.'}), 400
    if min_trades < 0.1:
        return jsonify({'error': 'min_trades debe ser al menos 0.1.'}), 400
    if generations < 1 or generations > 500:
        return jsonify({'error': 'generations debe estar entre 1 y 500.'}), 400
    if population < 10 or population > 1000:
        return jsonify({'error': 'population debe estar entre 10 y 1000.'}), 400

    def event_stream():
        try:
            import subprocess
            import time
            import json
            
            filename = f"{pair}_{interval}.csv"
            filepath = os.path.join(app.config['DATA_DIR'], filename)
            if not os.path.exists(filepath):
                yield f"data: {json.dumps({'type': 'error', 'message': f'Datos no encontrados para {pair} {interval}'})}\n\n"
                return
                
            exe_path = get_genetic_optimizer_path()
            if not exe_path:
                yield f"data: {json.dumps({'type': 'error', 'message': 'El ejecutable en Rust no está compilado.'})}\n\n"
                return
                    
            cmd = [
                exe_path,
                "--csv", filepath,
                "--expiry", str(expiry),
                "--min-trades", str(min_trades),
                "--generations", str(generations),
                "--population", str(population)
            ]
            
            yield f"data: {json.dumps({'type': 'log', 'message': 'Ejecutando algoritmo genético en Rust...'})}\n\n"
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            
            start_time = time.time()
            final_output = ""
            
            for line in process.stdout:
                line_str = line.strip()
                if line_str.startswith("PROGRESS:"):
                    parts = line_str.split(" ")[1].split("/")
                    current_gen = int(parts[0])
                    total_gens = int(parts[1])
                    progress_pct = (current_gen / total_gens) * 100
                    
                    elapsed = time.time() - start_time
                    eta = (elapsed / current_gen) * (total_gens - current_gen) if current_gen > 0 else 0
                    
                    yield f"data: {json.dumps({'type': 'progress', 'progress': progress_pct, 'eta': eta, 'log': f'Generación {current_gen}/{total_gens} completada.'})}\n\n"
                else:
                    final_output += line
                    
            process.wait()
            if process.returncode != 0:
                err_text = process.stderr.read()
                yield f"data: {json.dumps({'type': 'error', 'message': f'Fallo del optimizador Rust: {err_text}'})}\n\n"
                return
                
            try:
                output_json = extract_json_from_output(final_output)
                yield f"data: {json.dumps({'type': 'result', 'data': output_json})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': f'Error al decodificar salida: {str(e)}', 'details': final_output})}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return sse_response(event_stream())


@app.route('/api/smart-optimize-stream', methods=['GET'])
def run_smart_optimize_stream():
    pair = request.args.get('pair', 'BTCUSDT')
    interval = request.args.get('interval', '1h')
    if not is_safe_symbol(pair) or not is_safe_interval(interval):
        return jsonify({'error': 'Par o intervalo no válido.'}), 400
    base_capital = float(request.args.get('base_capital', 1000.0))
    profit_pct = float(request.args.get('profit_pct', 20.0))
    attempts = int(request.args.get('attempts', 2))
    payout = float(request.args.get('payout', 0.85))
    
    if base_capital <= 0:
        return jsonify({'error': 'base_capital debe ser mayor a 0.'}), 400
    if not (0.0 < profit_pct <= 100.0):
        return jsonify({'error': 'profit_pct debe estar entre 0.0 y 100.0.'}), 400
    if attempts < 1 or attempts > 100:
        return jsonify({'error': 'attempts debe estar entre 1 y 100.'}), 400
    if payout < 0.0 or payout > 2.0:
        return jsonify({'error': 'payout debe estar entre 0.0 y 2.0.'}), 400

    def event_stream():
        try:
            import subprocess
            import time
            import json
            import queue
            import threading
            
            filename = f"{pair}_{interval}.csv"
            filepath = os.path.join(app.config['DATA_DIR'], filename)
            if not os.path.exists(filepath):
                yield f"data: {json.dumps({'type': 'error', 'message': f'Datos no encontrados para {pair} {interval}'})}\n\n"
                return
                
            yield f"data: {json.dumps({'type': 'log', 'message': 'Paso [1/5]: Buscando la estrategia óptima con Algoritmo Genético en Rust...'})}\n\n"
            
            exe_path = get_genetic_optimizer_path()
            if not exe_path:
                yield f"data: {json.dumps({'type': 'error', 'message': 'El ejecutable del optimizador genético no está compilado.'})}\n\n"
                return
                    
            cmd = [
                exe_path,
                "--csv", filepath,
                "--expiry", "1",
                "--min-trades", "5.0",
                "--generations", "50",
                "--population", "150"
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            
            start_time = time.time()
            final_output = ""
            
            for line in process.stdout:
                line_str = line.strip()
                if line_str.startswith("PROGRESS:"):
                    parts = line_str.split(" ")[1].split("/")
                    current_gen = int(parts[0])
                    total_gens = int(parts[1])
                    
                    progress_pct = (current_gen / total_gens) * 50.0
                    
                    elapsed = time.time() - start_time
                    eta = (elapsed / current_gen) * (total_gens - current_gen) if current_gen > 0 else 0
                    eta += 2.0  # Buffer for next steps
                    
                    yield f"data: {json.dumps({'type': 'progress', 'progress': progress_pct, 'eta': eta, 'log': f'Optimización genética: Gen {current_gen}/{total_gens}'})}\n\n"
                else:
                    final_output += line
                    
            process.wait()
            if process.returncode != 0:
                yield f"data: {json.dumps({'type': 'error', 'message': 'El optimizador genético en Rust falló.'})}\n\n"
                return
                
            try:
                rust_json = extract_json_from_output(final_output)
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': f'Error parseando JSON Rust: {str(e)}'})}\n\n"
                return
                
            if 'error' in rust_json:
                yield f"data: {json.dumps({'type': 'error', 'message': rust_json['error']})}\n\n"
                return
                
            best_genome = rust_json.get('parameters', {})
            win_rate = float(rust_json.get('out_of_sample_win_rate', 0.55))
            in_sample_win_rate = float(rust_json.get('in_sample_win_rate', 0.60))
            
            yield f"data: {json.dumps({'type': 'log', 'message': 'Paso [2/5]: Cargando velas e inicializando simulación en modo BARBELL...'})}\n\n"
            
            df = load_csv_data(pair, interval)
            if df is None:
                yield f"data: {json.dumps({'type': 'error', 'message': f'Datos de velas no encontrados para {pair} {interval}'})}\n\n"
                return
                
            from strategies.genetic_composite import GeneticCompositeStrategy
            strategy = GeneticCompositeStrategy()
            signals = strategy.generate_signals(df, best_genome)
            
            risk_capital = base_capital * (profit_pct / 100.0)
            target_capital = base_capital
            bet_fraction = 1.0 / attempts
            
            streak_plan = optimizer.calculate_streak_plan(
                win_rate=win_rate,
                payout=payout,
                risk_capital=risk_capital,
                target_capital=target_capital,
                attempts=attempts,
                base_capital=base_capital
            )
            
            optimal_n = streak_plan.get('best_n_for_target', 4)
            
            q = queue.Queue()
            sim_start_time = time.time()
            
            def sim_progress_callback(progress_ratio):
                elapsed = time.time() - sim_start_time
                eta = (elapsed / progress_ratio) * (1.0 - progress_ratio) if progress_ratio > 0 else 0
                eta += 1.0  # Buffer for Monte Carlo
                mapped_progress = 50.0 + (progress_ratio * 25.0)
                q.put({
                    'type': 'progress',
                    'progress': mapped_progress,
                    'eta': eta,
                    'log': f'Simulando operaciones: {progress_ratio * 100:.1f}%'
                })
                
            def sim_worker():
                try:
                    res = simulator.run(
                        df, signals,
                        expiry_candles=1,
                        payout=payout,
                        initial_capital=base_capital,
                        mode='BARBELL',
                        n_consecutive=optimal_n,
                        bet_fraction=bet_fraction,
                        risk_ratio=profit_pct / 100.0,
                        target_ratio=target_capital / risk_capital,
                        progress_callback=sim_progress_callback
                    )
                    q.put({'type': 'result', 'data': res})
                except Exception as ex:
                    q.put({'type': 'error', 'message': str(ex)})
                    
            threading.Thread(target=sim_worker, daemon=True).start()
            
            sim_results = None
            while True:
                item = q.get()
                if item['type'] == 'progress':
                    yield f"data: {json.dumps(item)}\n\n"
                elif item['type'] == 'error':
                    yield f"data: {json.dumps(item)}\n\n"
                    return
                elif item['type'] == 'result':
                    sim_results = item['data']
                    break
                    
            yield f"data: {json.dumps({'type': 'progress', 'progress': 75.0, 'eta': 1.0, 'log': 'Paso [3/5]: Analizando métricas de operaciones y rachas...'})}\n\n"
            
            trades = sim_results['trades']
            stats = {}
            if len(trades) > 0:
                stats = stats_engine.analyze(trades, df=df)
                
            signal_markers = []
            for _, row in df.iterrows():
                idx = row.name
                if idx in signals.index and signals.loc[idx] is not None and signals.loc[idx] in ['CALL', 'PUT']:
                    signal_markers.append({
                        'time': int(row['time']),
                        'direction': signals.loc[idx],
                        'price': float(row['close'])
                    })
            if len(signal_markers) > 500:
                signal_markers = signal_markers[-500:]
                
            equity_curve = []
            for ec in sim_results['equity_curve']:
                t = ec.get('time')
                if t is not None:
                    t_val = float(t)
                    if t_val > 2**32:
                        t_val = t_val / 1000
                    equity_curve.append({'time': int(t_val), 'equity': ec['equity']})
            if len(equity_curve) > 500:
                step = len(equity_curve) // 500
                equity_curve = equity_curve[::step]
                
            formatted_trades = []
            for trade in trades:
                t = trade.get('time')
                t_val = None
                if t is not None:
                    t_val = float(t)
                    if t_val > 2**32:
                        t_val = t_val / 1000
                    t_val = int(t_val)
                formatted_trades.append({
                    'time': t_val,
                    'direction': trade['direction'],
                    'entry_price': trade['entry_price'],
                    'exit_price': trade['exit_price'],
                    'result': trade['result'],
                    'pnl': trade['pnl']
                })
                
            formatted_trades_display = formatted_trades[-100:] if len(formatted_trades) > 100 else formatted_trades
            
            yield f"data: {json.dumps({'type': 'progress', 'progress': 80.0, 'eta': 0.5, 'log': 'Paso [4/5]: Simulando campaña con Monte Carlo (5,000 caminos)...'})}\n\n"
            
            mc_results = optimizer.monte_carlo_discrete(
                win_rate=win_rate,
                payout=payout,
                n_consecutive=optimal_n,
                bet_fraction=bet_fraction,
                risk_capital=risk_capital,
                target_capital=target_capital,
                num_simulations=5000
            )
            
            yield f"data: {json.dumps({'type': 'progress', 'progress': 90.0, 'eta': 0.2, 'log': 'Simulando trayectorias de capital...'})}\n\n"
            
            mc_paths_results = optimizer.monte_carlo(
                win_rate=win_rate,
                payout=payout,
                n=optimal_n,
                kelly_f=bet_fraction,
                num_simulations=1000,
                num_cycles=200
            )
            
            paths = []
            if 'paths' in mc_paths_results:
                for path in mc_paths_results['paths'][:30]:
                    scaled_path = [p * risk_capital for p in path]
                    if len(scaled_path) > 100:
                        step = len(scaled_path) // 100
                        paths.append(scaled_path[::step])
                    else:
                        paths.append(scaled_path)
                        
            from strategies.genetic_composite import GeneticCompositeStrategy
            from strategies.daily_confluence import DailyConfluenceStrategy
            
            # --- CONSTRUCCIÓN DEL TOP 5 DE ESTRATEGIAS DISTINTAS DINÁMICAS ---
            top_strategies = []
            
            base_rsi = int(best_genome.get('rsi_period', 14)) if best_genome else 14
            base_bb = int(best_genome.get('bb_period', 20)) if best_genome else 20
            base_std = float(best_genome.get('bb_std', 2.0)) if best_genome else 2.0
            
            profiles = [
                {
                    "id": 1,
                    "name": "🏆 Confluencia Genética Total",
                    "type": "genetic_composite",
                    "genome": best_genome,
                    "description": f"Genoma cuantitativo hallado por el motor genético (RSI {base_rsi}, BB {base_bb}, std {base_std})."
                },
                {
                    "id": 2,
                    "name": "⚡ Reversión Rápida Momentum",
                    "type": "rsi_bollinger_fast",
                    "genome": {
                        "rsi_period": max(5, base_rsi - 4),
                        "rsi_oversold": 30.0,
                        "rsi_overbought": 70.0,
                        "rsi_enabled": True,
                        "bb_period": max(10, base_bb - 4),
                        "bb_std": max(1.2, round(base_std - 0.2, 1)),
                        "bb_enabled": True,
                        "ema_enabled": False
                    },
                    "description": f"Variante adaptativa de alta frecuencia (RSI {max(5, base_rsi - 4)}, BB {max(10, base_bb - 4)})."
                },
                {
                    "id": 3,
                    "name": "📈 Seguimiento de Tendencia Macro",
                    "type": "trend_following_ema",
                    "genome": {
                        "rsi_period": base_rsi,
                        "rsi_oversold": 40.0,
                        "rsi_overbought": 60.0,
                        "rsi_enabled": True,
                        "bb_enabled": False,
                        "ema_fast_period": 9,
                        "ema_slow_period": 21,
                        "ema_enabled": True
                    },
                    "description": f"Variante tendencial macro con confirmación EMA (EMA 9/21, RSI Pullback)."
                },
                {
                    "id": 4,
                    "name": "🛡️ Conservadora Filtro de Rechazo",
                    "type": "rejection_pinbar",
                    "genome": {
                        "rsi_period": base_rsi + 2,
                        "rsi_oversold": 32.0,
                        "rsi_overbought": 68.0,
                        "rsi_enabled": True,
                        "bb_enabled": False,
                        "rejection_filter_enabled": True,
                        "pinbar_wick_ratio": 0.35
                    },
                    "description": f"Variante defensiva con filtro de rechazo mecha Pinbar (RSI {base_rsi + 2})."
                },
                {
                    "id": 5,
                    "name": "💥 Breakout & Volatilidad Squeeze",
                    "type": "volatility_breakout",
                    "genome": {
                        "rsi_enabled": False,
                        "bb_period": base_bb,
                        "bb_std": max(1.2, round(base_std - 0.3, 1)),
                        "bb_enabled": True,
                        "volatility_filter_enabled": True,
                        "min_bb_width": 0.0
                    },
                    "description": f"Variante de ruptura de volatilidad (Squeeze) basada en compresión adaptativa de bandas."
                }
            ]
            
            main_sim_results = None
            main_streak_plan = None
            main_stats = None
            main_equity_curve = None
            main_signal_markers = None
            main_formatted_trades = None

            default_universe = [
                "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", 
                "ADAUSDT", "DOGEUSDT", "LTCUSDT", "LINKUSDT", "TRXUSDT", "DOTUSDT"
            ]
            corr_engine = CorrelationEngine(app.config['DATA_DIR'])
            universe_data = corr_engine.load_universe(default_universe)
            if universe_data:
                corr_matrix, _ = corr_engine.compute_correlation_matrix(universe_data)
                selected_assets = corr_engine.select_uncorrelated_assets(corr_matrix, threshold=0.65)
                corr_labels = list(corr_matrix.columns)
                corr_values = corr_matrix.values.tolist()
            else:
                selected_assets = [pair]
                corr_labels = [pair]
                corr_values = [[1.0]]

            asset_win_rates = {}
            for asset in selected_assets:
                asset_df = universe_data.get(asset) if universe_data else None
                if asset_df is not None and not asset_df.empty:
                    gen_sigs = GeneticCompositeStrategy().generate_signals(asset_df, best_genome)
                    asset_sim = simulator.run(asset_df, gen_sigs, expiry_candles=1, payout=payout)
                    sum_res = asset_sim.get('summary', {})
                    tot_tr = sum_res.get('total_trades', 0)
                    asset_wr = sum_res.get('win_rate', 0.0) if tot_tr > 0 else 0.0
                    wins_tr = sum_res.get('wins', 0)
                    asset_win_rates[asset] = {
                        "win_rate": asset_wr,
                        "wins": wins_tr,
                        "trades": tot_tr,
                        "sample_type": "OOS"
                    }
                else:
                    asset_win_rates[asset] = {
                        "win_rate": 0.0,
                        "wins": 0,
                        "trades": 0,
                        "sample_type": "N/A"
                    }

            for p in profiles:
                p_signals = GeneticCompositeStrategy().generate_signals(df, p["genome"])

                p_sim_res = simulator.run(
                    df, p_signals,
                    expiry_candles=1,
                    payout=payout,
                    initial_capital=base_capital,
                    mode='BARBELL',
                    n_consecutive=optimal_n,
                    bet_fraction=bet_fraction,
                    risk_ratio=profit_pct / 100.0,
                    target_ratio=target_capital / risk_capital
                )
                
                p_trades = p_sim_res['trades']
                p_wr = float(p_sim_res['summary']['win_rate']) if len(p_trades) > 0 else 0.0
                p_stats = stats_engine.analyze(p_trades, df=df) if len(p_trades) > 0 else {}
                
                p_plan = optimizer.calculate_streak_plan(
                    win_rate=p_wr,
                    payout=payout,
                    risk_capital=risk_capital,
                    target_capital=target_capital,
                    attempts=attempts,
                    base_capital=base_capital
                )
                p_opt_n = p_plan.get('best_n_for_target', optimal_n)
                
                p_markers = []
                for _, row in df.iterrows():
                    idx = row.name
                    if idx in p_signals.index and p_signals.loc[idx] is not None and p_signals.loc[idx] in ['CALL', 'PUT']:
                        p_markers.append({
                            'time': int(row['time']),
                            'direction': p_signals.loc[idx],
                            'price': float(row['close'])
                        })
                if len(p_markers) > 500:
                    p_markers = p_markers[-500:]
                    
                p_eq_curve = []
                for ec in p_sim_res['equity_curve']:
                    t = ec.get('time')
                    if t is not None:
                        t_val = float(t)
                        if t_val > 2**32:
                            t_val = t_val / 1000
                        p_eq_curve.append({'time': int(t_val), 'equity': ec['equity']})
                if len(p_eq_curve) > 500:
                    step = len(p_eq_curve) // 500
                    p_eq_curve = p_eq_curve[::step]
                    
                p_fmt_trades = []
                for trade in p_trades:
                    t = trade.get('time')
                    t_val = float(t)/1000 if (t is not None and float(t) > 2**32) else (int(t) if t is not None else None)
                    p_fmt_trades.append({
                        'time': t_val,
                        'direction': trade['direction'],
                        'entry_price': trade['entry_price'],
                        'exit_price': trade['exit_price'],
                        'result': trade['result'],
                        'pnl': trade['pnl']
                    })
                    
                p_mc = optimizer.monte_carlo_discrete(
                    win_rate=p_wr,
                    payout=payout,
                    n_consecutive=p_opt_n,
                    bet_fraction=bet_fraction,
                    risk_capital=risk_capital,
                    target_capital=target_capital,
                    num_simulations=1000
                )
                
                # Cálculo empírico observacional de tasa paralela
                if len(p_trades) > 0 and len(selected_assets) > 0:
                    p_win_emp = sum(1 for t in p_trades if t.get('result') == 'WIN') / len(p_trades)
                    s_single = (p_win_emp ** p_opt_n)
                    p_parallel = float(min(0.99, max(0.0, 1.0 - ((1.0 - s_single) ** min(attempts, len(selected_assets))))))
                else:
                    p_parallel = 0.0

                strat_item = {
                    "id": p["id"],
                    "name": p["name"],
                    "type": p["type"],
                    "win_rate_oos": p_wr,
                    "win_rate_is": in_sample_win_rate,
                    "best_genome": p["genome"],
                    "natural_description": p["description"],
                    "streak_plan": p_plan,
                    "mc_discrete": p_mc,
                    "sim_summary": p_sim_res['summary'],
                    "equity_curve": p_eq_curve,
                    "trades": p_fmt_trades[-100:] if len(p_fmt_trades) > 100 else p_fmt_trades,
                    "stats": p_stats,
                    "signals": p_markers,
                    "parallel_campaign_1day_prob": p_parallel,
                    "sample_size_warning": len(p_trades) < 20
                }
                
                top_strategies.append(strat_item)
                
                if p["id"] == 1:
                    main_sim_results = p_sim_res
                    main_streak_plan = p_plan
                    main_stats = p_stats
                    main_equity_curve = p_eq_curve
                    main_signal_markers = p_markers
                    main_formatted_trades = p_fmt_trades
            
            response = {
                'best_genome': best_genome,
                'win_rate_oos': win_rate,
                'win_rate_is': in_sample_win_rate,
                'streak_plan': main_streak_plan or streak_plan,
                'sim_summary': main_sim_results['summary'] if main_sim_results else sim_results['summary'],
                'equity_curve': main_equity_curve or equity_curve,
                'trades': main_formatted_trades[-100:] if main_formatted_trades else formatted_trades_display,
                'stats': main_stats or stats,
                'signals': main_signal_markers or signal_markers,
                'mc_discrete': mc_results,
                'mc_paths': paths,
                'mc_summary': {
                    'ruin_probability': mc_paths_results.get('ruin_probability', 0.0),
                    'max_drawdowns': mc_paths_results.get('max_drawdowns', {})
                },
                'top_strategies': top_strategies,
                'selected_assets': selected_assets,
                'asset_win_rates': asset_win_rates,
                'correlation_matrix': {
                    'labels': corr_labels,
                    'matrix': corr_values
                },
                'parallel_campaign_1day_prob': top_strategies[0]['parallel_campaign_1day_prob'] if top_strategies else 0.0
            }
            
            yield f"data: {json.dumps({'type': 'result', 'data': clean_json_data(response)})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return sse_response(event_stream())


if __name__ == '__main__':
    print("=" * 50)
    print("  BinSim - Binary Options Simulator")
    print("  http://127.0.0.1:5001")
    print("=" * 50)
    import os
    use_reloader = os.environ.get('FLASK_USE_RELOADER', 'false').lower() == 'true'
    app.run(port=5001, debug=True, use_reloader=use_reloader)
