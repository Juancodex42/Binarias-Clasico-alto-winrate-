import pandas as pd
import numpy as np
from .base import BaseStrategy

class GeneticCompositeStrategy(BaseStrategy):
    name = "Estrategia Genetica Combinada"
    description = "Estrategia combinada multi-indicador optimizada por el motor genetico en Rust."

    def get_params_schema(self) -> list[dict]:
        return [
            {"name": "rsi_period", "type": "int", "default": 14, "min": 2, "max": 100, "step": 1, "description": "RSI Period"},
            {"name": "rsi_oversold", "type": "float", "default": 30.0, "min": 5.0, "max": 50.0, "step": 0.5, "description": "RSI Oversold"},
            {"name": "rsi_overbought", "type": "float", "default": 70.0, "min": 50.0, "max": 95.0, "step": 0.5, "description": "RSI Overbought"},
            {"name": "rsi_enabled", "type": "bool", "default": True, "description": "RSI Habilitado"},
            
            {"name": "bb_period", "type": "int", "default": 20, "min": 5, "max": 150, "step": 1, "description": "Bollinger Period"},
            {"name": "bb_std", "type": "float", "default": 2.0, "min": 0.5, "max": 5.0, "step": 0.1, "description": "Bollinger Std Dev"},
            {"name": "bb_enabled", "type": "bool", "default": True, "description": "Bollinger Habilitado"},
            
            {"name": "ema_fast_period", "type": "int", "default": 9, "min": 2, "max": 50, "step": 1, "description": "EMA Fast Period"},
            {"name": "ema_slow_period", "type": "int", "default": 21, "min": 5, "max": 200, "step": 1, "description": "EMA Slow Period"},
            {"name": "ema_enabled", "type": "bool", "default": False, "description": "EMA Cross Habilitado"},

            {"name": "htf_ema_period", "type": "int", "default": 100, "min": 20, "max": 250, "step": 1, "description": "HTF EMA Period"},
            {"name": "htf_ema_enabled", "type": "bool", "default": False, "description": "HTF Trend Filter Habilitado"}
        ]

    def prepare_data(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty:
            return {}
        from engine.indicators import compute_ema, compute_wilders_rsi
        close = df['close']
        has_vol = ('volume' in df.columns) and (df['volume'].fillna(0).sum() > 0)
        
        rsi_14 = compute_wilders_rsi(close, 14)
        bb_sma = close.rolling(window=20).mean()
        bb_std = close.rolling(window=20).std(ddof=0)
        ema_9 = compute_ema(close, 9)
        ema_21 = compute_ema(close, 21)
        ema_100 = compute_ema(close, 100)
        
        return {
            'rsi_14': rsi_14,
            'bb_sma': bb_sma,
            'bb_std': bb_std,
            'ema_9': ema_9,
            'ema_21': ema_21,
            'ema_100': ema_100,
            'has_vol': has_vol,
            'orig_indices': df.index
        }

    def generate_signals(self, df: pd.DataFrame = None, params: dict = None, precomputed: dict = None, **kwargs) -> pd.Series:
        if precomputed is None and isinstance(df, dict):
            precomputed = df
            df = None

        p = params or {}
        rsi_period = int(p.get("rsi_period", 14))
        rsi_oversold = float(p.get("rsi_oversold", 30.0))
        rsi_overbought = float(p.get("rsi_overbought", 70.0))
        rsi_enabled = bool(p.get("rsi_enabled", True))
        
        bb_period = int(p.get("bb_period", 20))
        bb_std = float(p.get("bb_std", 2.0))
        bb_enabled = bool(p.get("bb_enabled", True))
        
        ema_fast_period = int(p.get("ema_fast_period", 9))
        ema_slow_period = int(p.get("ema_slow_period", 21))
        ema_enabled = bool(p.get("ema_enabled", False))

        htf_ema_period = int(p.get("htf_ema_period", 100))
        htf_ema_enabled = bool(p.get("htf_ema_enabled", False))
        
        if df is not None:
            close = df['close']
            orig_indices = df.index
        elif isinstance(precomputed, dict) and 'orig_indices' in precomputed:
            orig_indices = precomputed['orig_indices']
            close = precomputed.get('bb_sma', pd.Series(dtype=float))
        else:
            return pd.Series(dtype=object)
            
        from engine.indicators import compute_ema, compute_wilders_rsi

        # 1. RSI
        rsi_call = pd.Series(True, index=orig_indices)
        rsi_put = pd.Series(True, index=orig_indices)
        if rsi_enabled:
            rsi = precomputed['rsi_14'] if (rsi_period == 14 and isinstance(precomputed, dict) and 'rsi_14' in precomputed) else compute_wilders_rsi(close, rsi_period)
            prev_rsi = rsi.shift(1)
            if not bb_enabled and not ema_enabled:
                rsi_call = (prev_rsi <= rsi_oversold) & (rsi > prev_rsi)
                rsi_put = (prev_rsi >= rsi_overbought) & (rsi < prev_rsi)
            else:
                rsi_call = rsi <= rsi_oversold
                rsi_put = rsi >= rsi_overbought
            
        # 2. Bollinger Bands
        bb_call = pd.Series(True, index=orig_indices)
        bb_put = pd.Series(True, index=orig_indices)
        if bb_enabled:
            if bb_period == 20 and bb_std == 2.0 and isinstance(precomputed, dict) and 'bb_sma' in precomputed:
                sma = precomputed['bb_sma']
                std = precomputed['bb_std']
            else:
                sma = close.rolling(window=bb_period).mean()
                std = close.rolling(window=bb_period).std(ddof=0)
            upper_band = sma + (std * bb_std)
            lower_band = sma - (std * bb_std)
            
            prev_close = close.shift(1)
            prev_lower = lower_band.shift(1)
            prev_upper = upper_band.shift(1)
            
            if bool(p.get("volatility_filter_enabled", False)) and not rsi_enabled:
                bb_call = (close > upper_band) & (prev_close <= prev_upper)
                bb_put = (close < lower_band) & (prev_close >= prev_lower)
            else:
                bb_call = (prev_close >= prev_lower) & (close < lower_band)
                bb_put = (prev_close <= prev_upper) & (close > upper_band)
            
        # 3. EMA Cross / Trend Pullback
        ema_call = pd.Series(True, index=orig_indices)
        ema_put = pd.Series(True, index=orig_indices)
        if ema_enabled:
            ema_f = precomputed['ema_9'] if (ema_fast_period == 9 and isinstance(precomputed, dict) and 'ema_9' in precomputed) else compute_ema(close, ema_fast_period)
            ema_s = precomputed['ema_21'] if (ema_slow_period == 21 and isinstance(precomputed, dict) and 'ema_21' in precomputed) else compute_ema(close, ema_slow_period)
            prev_f = ema_f.shift(1)
            prev_s = ema_s.shift(1)
            
            if rsi_enabled:
                ema_call = (ema_f > ema_s) & (rsi <= rsi_oversold)
                ema_put = (ema_f < ema_s) & (rsi >= rsi_overbought)
            else:
                ema_call = (prev_f <= prev_s) & (ema_f > ema_s)
                ema_put = (prev_f >= prev_s) & (ema_f < ema_s)
            
        # 4. Pinbar Rejection
        call_cond = pd.Series(True, index=orig_indices)
        put_cond = pd.Series(True, index=orig_indices)
        
        if rsi_enabled:
            call_cond = call_cond & rsi_call
            put_cond = put_cond & rsi_put
        if bb_enabled:
            call_cond = call_cond & bb_call
            put_cond = put_cond & bb_put
        if ema_enabled:
            call_cond = call_cond & ema_call
            put_cond = put_cond & ema_put

        if bool(p.get("rejection_filter_enabled", False)) and df is not None:
            high = df['high']
            low = df['low']
            open_p = df['open']
            candle_range = high - low
            upper_wick = high - np.maximum(open_p, close)
            lower_wick = np.minimum(open_p, close) - low
            wick_ratio = float(p.get("pinbar_wick_ratio", 0.35))
            
            pin_bull = (candle_range > 0) & ((lower_wick / candle_range) >= wick_ratio)
            pin_bear = (candle_range > 0) & ((upper_wick / candle_range) >= wick_ratio)
            
            call_cond = call_cond & pin_bull
            put_cond = put_cond & pin_bear

        # 5. Volatility Squeeze
        if bool(p.get("volatility_filter_enabled", False)) and bb_enabled:
            sma = close.rolling(window=bb_period).mean()
            std = close.rolling(window=bb_period).std(ddof=0)
            upper_band = sma + (std * bb_std)
            lower_band = sma - (std * bb_std)
            bb_width = (upper_band - lower_band) / close
            
            threshold = float(p.get("min_bb_width", 0.0))
            if threshold > 0.0:
                squeeze_active = bb_width <= threshold
            else:
                rolling_q30 = bb_width.rolling(window=100, min_periods=20).quantile(0.30)
                squeeze_active = bb_width <= rolling_q30.fillna(bb_width.quantile(0.30))
            
            if bb_enabled and rsi_enabled:
                sqz_call = ~squeeze_active
                sqz_put = ~squeeze_active
            else:
                prev_sqz = squeeze_active.shift(1).fillna(False)
                open_p = df['open'] if df is not None else close
                sqz_call = prev_sqz & (close > open_p)
                sqz_put = prev_sqz & (close < open_p)
            
            call_cond = call_cond & sqz_call
            put_cond = put_cond & sqz_put

        # 6. HTF Trend Alignment Filter
        if htf_ema_enabled:
            htf_ema = precomputed['ema_100'] if (htf_ema_period == 100 and isinstance(precomputed, dict) and 'ema_100' in precomputed) else compute_ema(close, htf_ema_period)
            call_cond = call_cond & (close > htf_ema)
            put_cond = put_cond & (close < htf_ema)

        # Anti-streak edge trigger
        call_cond = call_cond & (~call_cond.shift(1).fillna(False))
        put_cond = put_cond & (~put_cond.shift(1).fillna(False))

        conflict = call_cond & put_cond
        call_cond = call_cond & (~conflict)
        put_cond = put_cond & (~conflict)

        signals = pd.Series(index=orig_indices, data=None, dtype=object)
        
        if not rsi_enabled and not bb_enabled and not ema_enabled and not p.get("rejection_filter_enabled") and not p.get("volatility_filter_enabled") and not htf_ema_enabled:
            return signals
            
        signals.loc[call_cond] = 'CALL'
        signals.loc[put_cond] = 'PUT'
        
        return signals

    def generate_signals_list(self, df: pd.DataFrame = None, params: dict = None, precomputed: dict = None) -> list[dict]:
        p = params or {}
        series = self.generate_signals(df=df, params=p, precomputed=precomputed)
        signals_list = []
        if df is not None:
            for idx in series.dropna().index:
                val = series.loc[idx]
                if val in ['CALL', 'PUT']:
                    row = df.loc[idx]
                    sig_time = int(row['open_time'] / 1000) if row['open_time'] > 2**32 else int(row['open_time'])
                    signals_list.append({
                        'time': sig_time,
                        'direction': val,
                        'price': float(row['close'])
                    })
        return signals_list
