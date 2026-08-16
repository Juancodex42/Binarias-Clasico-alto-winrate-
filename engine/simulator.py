import pandas as pd
import numpy as np

# Tolerancia para comparaciones de precios flotantes (evita falsos TIE/WIN por errores IEEE754)
_PRICE_EPS = 1e-8

class VectorizedBinarySimulator:
    """
    Simulador Vectorizado de Alto Rendimiento para Opciones Binarias.
    Calcula la ejecucion de trades y metricas de rendimiento utilizando operaciones matriciales NumPy.
    Acelera las simulaciones en un factor de 50x-100x respecto al bucle escalar.
    """
    @staticmethod
    def run_fast(
        df: pd.DataFrame,
        signals: pd.Series,
        expiry_candles: int = 1,
        payout: float = 0.85,
        initial_capital: float = 1000.0,
        bet_fraction: float = 0.1,
        slippage_pct: float = 0.0,
        tie_rule: str = 'RETURN_STAKE'
    ) -> dict:
        if df is None or len(df) <= expiry_candles + 1 or signals is None:
            return {"summary": {"total_trades": 0, "wins": 0, "losses": 0, "ties": 0, "win_rate": 0.0, "win_rate_effective": 0.0, "expected_value_per_trade": 0.0, "net_pnl": 0.0, "max_drawdown": 0.0}}

        n = len(df)
        open_prices = df['open'].to_numpy(dtype=np.float64)
        close_prices = df['close'].to_numpy(dtype=np.float64)

        sig_arr = np.zeros(n, dtype=np.int8)
        if hasattr(signals, 'reindex'):
            sig_series = signals.reindex(df.index)
        else:
            sig_series = pd.Series(signals, index=df.index)

        sig_arr[sig_series == 'CALL'] = 1
        sig_arr[sig_series == 'PUT'] = -1

        signal_indices = np.flatnonzero(sig_arr != 0)
        if len(signal_indices) == 0:
            return {"summary": {"total_trades": 0, "wins": 0, "losses": 0, "ties": 0, "win_rate": 0.0, "win_rate_effective": 0.0, "expected_value_per_trade": 0.0, "net_pnl": 0.0, "max_drawdown": 0.0}}

        valid_indices = []
        next_allowed = 0
        for idx in signal_indices:
            if idx >= next_allowed and (idx + expiry_candles) < n:
                valid_indices.append(idx)
                next_allowed = idx + expiry_candles

        if not valid_indices:
            return {"summary": {"total_trades": 0, "wins": 0, "losses": 0, "ties": 0, "win_rate": 0.0, "win_rate_effective": 0.0, "expected_value_per_trade": 0.0, "net_pnl": 0.0, "max_drawdown": 0.0}}

        idx_arr = np.array(valid_indices, dtype=np.int64)
        sig_type = sig_arr[idx_arr]

        entry_raw = open_prices[idx_arr + 1]
        exit_raw = close_prices[idx_arr + expiry_candles]

        entry_prices = np.where(sig_type == 1, entry_raw * (1.0 + slippage_pct), entry_raw * (1.0 - slippage_pct))
        price_diff = exit_raw - entry_prices

        is_tie = np.abs(price_diff) <= _PRICE_EPS
        if tie_rule == 'LOSS':
            is_win = np.where(sig_type == 1, price_diff > _PRICE_EPS, price_diff < -_PRICE_EPS)
            is_loss = ~is_win
            is_tie = np.zeros_like(is_tie, dtype=bool)
        else:
            is_win = np.where(sig_type == 1, price_diff > _PRICE_EPS, price_diff < -_PRICE_EPS)
            is_loss = ~is_win & ~is_tie

        fixed_bet = initial_capital * bet_fraction
        pnl_vector = np.where(is_win, fixed_bet * payout, np.where(is_tie, 0.0, -fixed_bet))

        # Check for account bankruptcy (equity <= 0) and stop trade processing at ruin
        equity_curve_raw = initial_capital + np.cumsum(pnl_vector)
        ruin_idx = np.flatnonzero(equity_curve_raw <= 0)
        if len(ruin_idx) > 0:
            cut = ruin_idx[0]
            equity_before = initial_capital + (np.sum(pnl_vector[:cut]) if cut > 0 else 0.0)
            if pnl_vector[cut] < 0:
                pnl_vector[cut] = -equity_before
            elif pnl_vector[cut] > 0:
                pnl_vector[cut] = min(pnl_vector[cut], equity_before * payout)
            pnl_vector = pnl_vector[:cut + 1]
            is_win = is_win[:cut + 1]
            is_loss = is_loss[:cut + 1]
            is_tie = is_tie[:cut + 1]
            idx_arr = idx_arr[:cut + 1]

        wins = int(np.sum(is_win))
        losses = int(np.sum(is_loss))
        ties = int(np.sum(is_tie))
        total = len(idx_arr)
        decisive = wins + losses

        win_rate = float(wins / total) if total > 0 else 0.0
        win_rate_eff = float(wins / decisive) if decisive > 0 else 0.0
        p_win_total = wins / total if total > 0 else 0.0
        p_loss_total = losses / total if total > 0 else 0.0
        ev_per_trade = float((p_win_total * payout) - (p_loss_total * 1.0)) if total > 0 else 0.0

        net_pnl = float(np.sum(pnl_vector))

        equity_curve = initial_capital + np.cumsum(pnl_vector)
        equity_curve = np.insert(equity_curve, 0, initial_capital)
        peaks = np.maximum.accumulate(equity_curve)
        drawdowns = np.where(peaks > 0, (peaks - equity_curve) / peaks, 0.0)
        max_dd = float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0

        return {
            "summary": {
                "total_trades": total,
                "wins": wins,
                "losses": losses,
                "ties": ties,
                "win_rate": win_rate,
                "win_rate_effective": win_rate_eff,
                "expected_value_per_trade": ev_per_trade,
                "net_pnl": net_pnl,
                "max_drawdown": max_dd
            }
        }


class BinarySimulator:
    def run(self, df: pd.DataFrame, signals: pd.Series, expiry_candles: int = 1, payout: float = 0.92, initial_capital: float = 1000.0, mode: str = 'SIMPLE', n_consecutive: int = 5, bet_fraction: float = 0.1, risk_ratio: float = 0.20, target_ratio: float = 5.0, slippage_pct: float = 0.0, allow_overlapping: bool = False, max_concurrent_trades: int = 1, tie_rule: str = 'RETURN_STAKE', progress_callback = None):
        """
        df: DataFrame with OHLCV
        signals: Series from strategy (CALL/PUT/None)
        expiry_candles: how many candles until expiry
        payout: win payout multiplier (0.92 = 92%)
        allow_overlapping: if True, allow opening new trades while previous position is active (SIMPLE mode)
        max_concurrent_trades: max active trades allowed simultaneously when allow_overlapping is True
        tie_rule: 'RETURN_STAKE' (Quotex/IQ Option refund PnL=0) or 'LOSS' (Deriv loss PnL=-bet)
        
        Returns dict with:
        - trades: list of dicts
        - equity_curve: list of dicts
        - summary: dict
        """
        trades = []
        equity_curve = []
        
        if len(df) > 1:
            candle_duration = int(df.iloc[1]['open_time'] - df.iloc[0]['open_time'])
        else:
            candle_duration = 86400
            
        if mode == 'BARBELL':
            arb_base = initial_capital
            risk_cap = arb_base * risk_ratio
            target_capital = risk_cap * target_ratio
            consecutive_wins = 0
            current_equity = arb_base
        else:
            current_equity = initial_capital
            base_capital = initial_capital
            consecutive_wins = 0
            fixed_bet = initial_capital * bet_fraction
            
        equity_curve.append({"index": -1, "time": df['open_time'].iloc[0] if len(df) else None, "equity": current_equity})
        
        trade_indices = signals.dropna().index
        
        active_positions = []
        next_allowed_entry_idx = 0
        
        for idx in trade_indices:
            signal = signals.loc[idx]
            if signal not in ['CALL', 'PUT']:
                continue
                
            entry_idx = df.index.get_loc(idx)
            if progress_callback:
                progress_callback(entry_idx / len(df))
                
            # Clean expired positions for overlapping check
            active_positions = [pos for pos in active_positions if pos['exit_idx'] > entry_idx]

            if not allow_overlapping or mode in ['REINVESTMENT', 'BARBELL']:
                if entry_idx < next_allowed_entry_idx:
                    continue  # Skip signal because current contract is still active
            else:
                if len(active_positions) >= max_concurrent_trades:
                    continue  # Reached max concurrent positions limit
                
            exit_idx = entry_idx + expiry_candles

            if exit_idx >= len(df):
                break
                
            # Correct look-ahead timing bias & execution price:
            # Entry execution is at the open of entry_idx + 1 (when close[entry_idx] is known)
            entry_price_raw = float(df.iloc[entry_idx + 1]['open'])
            entry_time = int(df.iloc[entry_idx + 1]['open_time'])
                
            # Aplicar slippage al precio de entrada según la dirección de la orden
            if signal == 'CALL':
                entry_price = entry_price_raw * (1.0 + slippage_pct)
            else:
                entry_price = entry_price_raw * (1.0 - slippage_pct)

            exit_price = float(df.iloc[exit_idx]['close'])
                
            # Exit execution is at the close of exit_idx, which is the open of exit_idx + 1
            if exit_idx + 1 < len(df):
                exit_time = int(df.iloc[exit_idx + 1]['open_time'])
            else:
                exit_time = int(df.iloc[exit_idx]['open_time']) + candle_duration
            
            if mode == 'BARBELL':
                initial_cycle_risk = arb_base * risk_ratio
                bet_size = (initial_cycle_risk * bet_fraction) * ((1.0 + payout) ** consecutive_wins)
                if bet_size > risk_cap:
                    bet_size = risk_cap
            elif mode == 'REINVESTMENT':
                bet_size = (base_capital * bet_fraction) * ((1.0 + payout) ** consecutive_wins)
            else:
                bet_size = fixed_bet
                
            if mode != 'BARBELL' and bet_size > current_equity:
                bet_size = current_equity
                
            # --- Clasificación WIN / TIE / LOSS con tolerancia épsilon ---
            price_diff = exit_price - entry_price
            is_tie = abs(price_diff) <= _PRICE_EPS
            is_win = False
            
            if is_tie and tie_rule == 'LOSS':
                is_win = False
                is_tie = False  # Deriv counts tie as LOSS
            elif not is_tie:
                if signal == 'CALL' and price_diff > 0:
                    is_win = True
                elif signal == 'PUT' and price_diff < 0:
                    is_win = True

            pnl = 0
            if is_tie:
                # Empate: broker devuelve capital arriesgado → PnL = 0, equity no cambia
                result_label = 'TIE'
            elif is_win:
                pnl = bet_size * payout
                result_label = 'WIN'
                if mode == 'BARBELL':
                    risk_cap += pnl
                    consecutive_wins += 1
                    if risk_cap >= target_capital:
                        # Exito del ciclo: consolidar ganancias en el core de arbitraje
                        arb_base += (risk_cap - initial_cycle_risk)
                        risk_cap = arb_base * risk_ratio
                        target_capital = risk_cap * target_ratio
                        consecutive_wins = 0
                    current_equity = arb_base + (risk_cap - (arb_base * risk_ratio))
                else:
                    current_equity += pnl
                    if mode == 'REINVESTMENT':
                        consecutive_wins += 1
                        if consecutive_wins >= n_consecutive:
                            base_capital = current_equity
                            consecutive_wins = 0
            else:
                pnl = -bet_size
                result_label = 'LOSS'
                if mode == 'BARBELL':
                    risk_cap -= bet_size
                    consecutive_wins = 0
                    if risk_cap <= 0.0001:
                        # NOTA: Estrategia de reabastecimiento por ganancias externas de Arbitraje P2P (Diseño intencional del usuario).
                        # El capital consumido del ciclo se reabastece desde el flujo de caja del arbitraje P2P.
                        if arb_base < initial_capital:
                            arb_base = initial_capital
                        risk_cap = arb_base * risk_ratio
                        target_capital = risk_cap * target_ratio
                        current_equity = arb_base
                    else:
                        current_equity = arb_base + (risk_cap - (arb_base * risk_ratio))
                else:
                    current_equity += pnl
                    if mode == 'REINVESTMENT':
                        consecutive_wins = 0
                        base_capital = current_equity

            if current_equity <= 0:
                current_equity = 0

            trades.append({
                "index": entry_idx,
                "time": entry_time,
                "exit_idx": exit_idx,
                "exit_time": exit_time,
                "direction": signal,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "result": result_label,
                "pnl": pnl,
                "bet_size": bet_size
            })
            
            equity_curve.append({
                "index": exit_idx,
                "time": exit_time,
                "equity": current_equity
            })
            
            active_positions.append({"exit_idx": exit_idx})
            next_allowed_entry_idx = exit_idx
            
            if current_equity <= 0:
                break
                
        wins = sum(1 for t in trades if t['result'] == 'WIN')
        losses = sum(1 for t in trades if t['result'] == 'LOSS')
        ties = sum(1 for t in trades if t['result'] == 'TIE')
        total = len(trades)
        decisive = wins + losses  # Operaciones con resultado definitivo (excluye empates)

        # Win Rate Bruto: include empates en el denominador
        win_rate = wins / total if total > 0 else 0
        # Win Rate Efectivo: excluye empates del denominador (métrica de calidad real)
        win_rate_effective = wins / decisive if decisive > 0 else 0
        # Expectativa Matemática por operación (en términos de fracción de apuesta)
        # E = p_win * payout - p_loss * 1.0  (normalizado; TIE = 0)
        p_win_total = wins / total if total > 0 else 0
        p_loss_total = losses / total if total > 0 else 0
        expected_value_per_trade = (p_win_total * payout) - (p_loss_total * 1.0)

        net_pnl = sum(t['pnl'] for t in trades)

        eq_vals = [e['equity'] for e in equity_curve]
        peak = initial_capital
        max_dd = 0
        for eq in eq_vals:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd

        summary = {
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "win_rate": win_rate,
            "win_rate_effective": win_rate_effective,
            "expected_value_per_trade": expected_value_per_trade,
            "net_pnl": net_pnl,
            "max_drawdown": max_dd
        }
        
        return {
            "trades": trades,
            "equity_curve": equity_curve,
            "summary": summary
        }

    def run_multi_asset(self, universe_data: dict, signals_by_pair: dict, expiry_candles: int = 2, payout: float = 0.85, initial_capital: float = 1000.0, mode: str = 'SIMPLE', n_consecutive: int = 3, bet_fraction: float = 0.166, risk_ratio: float = 0.20, target_ratio: float = 5.0, slippage_pct: float = 0.0, tie_rule: str = 'RETURN_STAKE'):
        """
        universe_data: dict of {symbol: DataFrame}
        signals_by_pair: dict of {symbol: list of signals}
        """
        # 1. Obtener la secuencia cronológica de operaciones
        raw_trades = []
        for symbol, signals in signals_by_pair.items():
            df = universe_data.get(symbol)
            if df is None or len(df) == 0:
                continue
            
            # Indexar df por open_time para búsqueda rápida
            time_col = df['open_time']
            if time_col.max() > 2**32:
                df_times = (time_col // 1000).tolist()
            else:
                df_times = time_col.tolist()
                
            time_to_idx = {t: idx for idx, t in enumerate(df_times)}
            
            df_open = df['open'].to_numpy()
            df_close = df['close'].to_numpy()
            df_open_time = df['open_time'].to_numpy()
            n_df = len(df)
            
            if n_df > 1:
                candle_duration = int(df_open_time[1] - df_open_time[0])
            else:
                candle_duration = 86400 * 1000 if time_col.max() > 2**32 else 86400
            
            for sig in signals:
                sig_time = sig['time']
                if sig_time > 2**32:
                    sig_time = sig_time // 1000
                if sig_time not in time_to_idx:
                    continue
                
                entry_idx = time_to_idx[sig_time]
                exit_idx = entry_idx + expiry_candles
                
                if exit_idx >= n_df:
                    continue
                    
                direction = sig['direction']
                
                entry_price_raw = float(df_open[entry_idx + 1])
                entry_time = int(df_open_time[entry_idx + 1])
                if entry_time > 2**32:
                    entry_time = entry_time // 1000
                    
                if direction == 'CALL':
                    entry_price = entry_price_raw * (1.0 + slippage_pct)
                else:
                    entry_price = entry_price_raw * (1.0 - slippage_pct)

                exit_price = float(df_close[exit_idx])
                    
                if exit_idx + 1 < n_df:
                    exit_time = int(df_open_time[exit_idx + 1])
                else:
                    norm_duration = candle_duration // 1000 if (time_col.max() > 2**32 or candle_duration >= 1000) else candle_duration
                    exit_time = entry_time + int(expiry_candles * norm_duration)
                if exit_time > 2**32:
                    exit_time = exit_time // 1000
                
                # --- Clasificación WIN / TIE / LOSS con tolerancia épsilon ---
                price_diff = exit_price - entry_price
                is_tie = abs(price_diff) <= _PRICE_EPS
                is_win = False
                if is_tie and tie_rule == 'LOSS':
                    is_win = False
                    is_tie = False
                elif not is_tie:
                    if direction == 'CALL' and price_diff > 0:
                        is_win = True
                    elif direction == 'PUT' and price_diff < 0:
                        is_win = True

                raw_trades.append({
                    'pair': symbol,
                    'direction': direction,
                    'entry_time': entry_time,
                    'exit_time': exit_time,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'result': 'WIN' if is_win else ('TIE' if is_tie else 'LOSS'),
                    'is_win': is_win,
                    'is_tie': is_tie,
                    'index': entry_idx
                })
                
        # Asignar un ID único a cada trade para poder rastrearlo en el simulador de eventos discretos
        for idx, rt in enumerate(raw_trades):
            rt['id'] = idx
            
        # 2. Generar eventos discretos de entrada y salida
        events = []
        for rt in raw_trades:
            events.append({
                'type': 'entry',
                'time': rt['entry_time'],
                'trade': rt
            })
            events.append({
                'type': 'exit',
                'time': rt['exit_time'],
                'trade': rt
            })
            
        # Ordenar cronológicamente. Si los tiempos coinciden, procesar 'exit' primero
        events.sort(key=lambda x: (x['time'], 0 if x['type'] == 'exit' else 1))
        
        # 3. Inicializar variables de simulación según el modo
        trades = []
        equity_curve = []
        next_allowed_time_by_pair = {}
        
        from engine.correlation import CorrelationEngine
        
        # Obtenemos la lista de pares del universo para inicializar estados específicos por activo
        all_pairs = list(signals_by_pair.keys())
        
        if mode == 'BARBELL':
            # Standalone safe_core variable to track safe capital (conserves equity)
            safe_core = initial_capital * (1.0 - risk_ratio)
            risk_cap = initial_capital * risk_ratio
            attempts = int(round(1.0 / bet_fraction)) if bet_fraction > 0 else 1
            bet_per_attempt = risk_cap / attempts
            
            # Inicializar los intentos independientes (balas)
            bullets = [{
                'capital': bet_per_attempt,
                'consecutive_wins': 0,
                'active_trade_id': None
            } for _ in range(attempts)]
            
            current_equity = initial_capital
        elif mode == 'REINVESTMENT':
            current_equity = initial_capital
            consecutive_wins_by_pair = {p: 0 for p in all_pairs}
            base_capital_by_pair = {p: initial_capital for p in all_pairs}
        else: # SIMPLE
            current_equity = initial_capital
            fixed_bet = initial_capital * bet_fraction
            
        if len(events) > 0:
            first_time = events[0]['time']
        else:
            first_time = None
            
        equity_curve.append({"time": first_time, "equity": current_equity})
        
        # Mapeo de ejecuciones por clase de activo por día para evitar más de 1 trade por categoría por día
        classes_executed_by_day = {}

        # 4. Loop principal del motor de eventos discretos
        for event in events:
            t = event['trade']
            pair = t['pair']
            event_type = event['type']
            
            if event_type == 'entry':
                # Evitar tomar otra operación en el mismo par si ya hay una activa
                if pair in next_allowed_time_by_pair and event['time'] < next_allowed_time_by_pair[pair]:
                    continue
                    
                # Filtro Inter-Clase: Evitar más de 1 trade de la misma categoría de activo el mismo día
                trade_day = pd.to_datetime(event['time'], unit='s' if event['time'] < 2**32 else 'ms').strftime('%Y-%m-%d')
                pair_class = CorrelationEngine.get_asset_class(pair)
                executed_classes = classes_executed_by_day.get(trade_day, set())
                if pair_class in executed_classes:
                    continue # Bloquear señal duplicada de la misma clase el mismo día
                    
                # Si no hay solapamiento, proceder según el modo
                if mode == 'BARBELL':
                    # Buscar una bala libre y con capital disponible, priorizando la que tiene mayor racha activa
                    available_bullets = [b for b in bullets if b['active_trade_id'] is None and b['capital'] > 0]
                    if len(available_bullets) == 0:
                        continue # No hay balas disponibles, se ignora la señal
                        
                    available_bullets.sort(key=lambda b: b['consecutive_wins'], reverse=True)
                    bullet = available_bullets[0]
                    
                    # Asignar trade a esta bala
                    bullet_idx = bullets.index(bullet)
                    t['assigned_bullet_idx'] = bullet_idx
                    bullet['active_trade_id'] = t['id']
                    
                    # En modo Barbell, la apuesta es todo el capital acumulado en esa bala
                    bet_size = bullet['capital']
                    t['bet_size'] = bet_size
                    
                elif mode == 'REINVESTMENT':
                    wins = consecutive_wins_by_pair.get(pair, 0)
                    base_cap = base_capital_by_pair.get(pair, current_equity)
                    bet_size = (base_cap * bet_fraction) * ((1.0 + payout) ** wins)
                    
                    if bet_size > current_equity:
                        bet_size = current_equity
                        
                    t['bet_size'] = bet_size
                    t['is_active'] = True
                    
                else: # SIMPLE
                    bet_size = fixed_bet
                    if bet_size > current_equity:
                        bet_size = current_equity
                        
                    t['bet_size'] = bet_size
                    t['is_active'] = True
                    
                # Registrar el bloqueo temporal para este par y la clase de activo para este día
                next_allowed_time_by_pair[pair] = t['exit_time']
                if trade_day not in classes_executed_by_day:
                    classes_executed_by_day[trade_day] = set()
                classes_executed_by_day[trade_day].add(pair_class)
                
            elif event_type == 'exit':
                # Validar que el trade haya sido activado/asignado antes de procesar cualquier resultado
                if mode == 'BARBELL' and t.get('assigned_bullet_idx') is None:
                    continue
                if mode != 'BARBELL' and not t.get('is_active', False):
                    continue

                # Procesar la salida del trade
                pnl = 0
                is_win = t['is_win']
                is_tie = t.get('is_tie', False)
                bet_size = t.get('bet_size', 0)

                if is_tie:
                    if mode == 'BARBELL':
                        bullet_idx = t.get('assigned_bullet_idx')
                        if bullet_idx is not None and 0 <= bullet_idx < len(bullets):
                            bullets[bullet_idx]['active_trade_id'] = None
                            if bullets[bullet_idx].get('pending_reset'):
                                bullets[bullet_idx]['capital'] = bullets[bullet_idx].pop('next_capital', bet_per_attempt)
                                bullets[bullet_idx]['consecutive_wins'] = 0
                                bullets[bullet_idx]['pending_reset'] = False
                    # Empate: broker devuelve capital, sin movimiento de equity ni contadores
                    trades.append({
                        'pair': pair,
                        'time': t['entry_time'],
                        'exit_time': event['time'],
                        'direction': t['direction'],
                        'entry_price': t['entry_price'],
                        'exit_price': t['exit_price'],
                        'result': 'TIE',
                        'pnl': 0.0,
                        'bet_size': bet_size,
                        'index': t['index']
                    })
                    equity_curve.append({'time': event['time'], 'equity': current_equity})
                    continue
                
                if mode == 'BARBELL':
                    bullet_idx = t.get('assigned_bullet_idx')
                    bullet = bullets[bullet_idx]
                    
                    if is_win:
                        pnl = bet_size * payout
                        bullet['capital'] += pnl
                        bullet['consecutive_wins'] += 1
                        bullet['active_trade_id'] = None
                        
                        # Si completa la racha, éxito de la campaña Barbell: consolidar ganancias en el núcleo seguro
                        if bullet['consecutive_wins'] >= n_consecutive:
                            # 1. Sumar todo el capital acumulado por la bala victoriosa al safe_core permanente
                            safe_core += bullet['capital']
                            
                            # 2. Recalcular el nuevo presupuesto de riesgo para la siguiente campaña (20% de la nueva base)
                            risk_cap = safe_core * risk_ratio
                            bet_per_attempt = risk_cap / attempts
                            
                            # 3. Reiniciar in-place las balas para la nueva campaña sin corromper trades en vuelo
                            for b in bullets:
                                if b['active_trade_id'] is None:
                                    b['capital'] = bet_per_attempt
                                    b['consecutive_wins'] = 0
                                    b['pending_reset'] = False
                                else:
                                    b['pending_reset'] = True
                                    b['next_capital'] = bet_per_attempt
                    else:
                        pnl = -bet_size
                        bullet['capital'] = 0
                        bullet['consecutive_wins'] = 0
                        bullet['active_trade_id'] = None
                        
                        # Verificar si todas las balas de la campaña están destruidas
                        all_ruined = all(b['capital'] <= 0.0001 and b['active_trade_id'] is None for b in bullets)
                        if all_ruined:
                            if safe_core < initial_capital * (1.0 - risk_ratio):
                                safe_core = initial_capital * (1.0 - risk_ratio)
                            
                            risk_cap = initial_capital * risk_ratio
                            bet_per_attempt = risk_cap / attempts
                            
                            # Iniciar una nueva campaña reabastecida por arbitraje externo
                            for b in bullets:
                                if b['active_trade_id'] is None:
                                    b['capital'] = bet_per_attempt
                                    b['consecutive_wins'] = 0
                                    b['pending_reset'] = False
                                else:
                                    b['pending_reset'] = True
                                    b['next_capital'] = bet_per_attempt
                                    
                    if bullet.get('pending_reset'):
                        if is_win:
                            safe_core += pnl
                        bullet['capital'] = bullet.pop('next_capital', bet_per_attempt)
                        bullet['consecutive_wins'] = 0
                        bullet['pending_reset'] = False

                    # Actualizar equidad actual
                    active_bullets_cap = sum(b['capital'] for b in bullets if not b.get('pending_reset'))
                    current_equity = safe_core + active_bullets_cap
                    
                elif mode == 'REINVESTMENT':
                    if is_win:
                        pnl = bet_size * payout
                        current_equity += pnl
                        consecutive_wins_by_pair[pair] += 1
                        
                        if consecutive_wins_by_pair[pair] >= n_consecutive:
                            consecutive_wins_by_pair[pair] = 0
                            base_capital_by_pair[pair] = base_capital_by_pair[pair] + pnl
                    else:
                        pnl = -bet_size
                        current_equity += pnl
                        consecutive_wins_by_pair[pair] = 0
                        base_capital_by_pair[pair] = max(0, base_capital_by_pair[pair] + pnl)
                        
                else: # SIMPLE
                    if is_win:
                        pnl = bet_size * payout
                    else:
                        pnl = -bet_size
                    current_equity += pnl
                    
                # Registrar el trade finalizado y agregar a la curva de equidad
                trades.append({
                    'pair': pair,
                    'time': t['entry_time'],
                    'exit_time': event['time'],
                    'direction': t['direction'],
                    'entry_price': t['entry_price'],
                    'exit_price': t['exit_price'],
                    'result': 'WIN' if is_win else 'LOSS',
                    'pnl': pnl,
                    'bet_size': bet_size,
                    'index': t['index']
                })
                
                equity_curve.append({
                    'time': event['time'],
                    'equity': current_equity
                })
                
                if current_equity <= 0:
                    break
                    
        # Calcular estadísticas generales del backtest
        wins = sum(1 for t in trades if t['result'] == 'WIN')
        losses = sum(1 for t in trades if t['result'] == 'LOSS')
        ties = sum(1 for t in trades if t['result'] == 'TIE')
        total = len(trades)
        decisive = wins + losses

        win_rate = wins / total if total > 0 else 0
        win_rate_effective = wins / decisive if decisive > 0 else 0
        p_win_total = wins / total if total > 0 else 0
        p_loss_total = losses / total if total > 0 else 0
        expected_value_per_trade = (p_win_total * payout) - (p_loss_total * 1.0)
        net_pnl = sum(t['pnl'] for t in trades)

        eq_vals = [e['equity'] for e in equity_curve]
        peak = initial_capital
        max_dd = 0
        for eq in eq_vals:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd

        summary = {
            "total_trades": total,
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "win_rate": win_rate,
            "win_rate_effective": win_rate_effective,
            "expected_value_per_trade": expected_value_per_trade,
            "net_pnl": net_pnl,
            "max_drawdown": max_dd
        }
        
        return {
            "trades": trades,
            "equity_curve": equity_curve,
            "summary": summary
        }
