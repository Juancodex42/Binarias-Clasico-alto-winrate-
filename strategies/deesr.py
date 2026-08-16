import pandas as pd
import numpy as np
from .base import BaseStrategy

class DeesrStrategy(BaseStrategy):
    name = "Dual Extreme Envelope Stretch Reversal"
    description = "Doble ruptura Bollinger/Keltner, RSI extremo dual y compresion de cuerpo."

    def get_params_schema(self) -> list[dict]:
        return [
            {"name": "bb_period", "type": "int", "default": 20, "min": 10, "max": 50, "description": "Bollinger Period"},
            {"name": "bb_std", "type": "float", "default": 2.0, "min": 2.0, "max": 3.5, "description": "Bollinger Std Dev"},
            {"name": "kc_period", "type": "int", "default": 20, "min": 10, "max": 50, "description": "Keltner Period"},
            {"name": "kc_mult", "type": "float", "default": 1.5, "min": 1.5, "max": 3.0, "description": "Keltner Multiplier"},
            {"name": "rsi_fast_period", "type": "int", "default": 3, "min": 2, "max": 5, "description": "Fast RSI Period"},
            {"name": "rsi_slow_period", "type": "int", "default": 14, "min": 7, "max": 21, "description": "Slow RSI Period"},
            {"name": "max_body_ratio", "type": "float", "default": 0.45, "min": 0.15, "max": 0.60, "description": "Max Body Ratio"},
            {"name": "min_wick_ratio", "type": "float", "default": 0.35, "min": 0.20, "max": 0.75, "description": "Min Wick Ratio"}
        ]

    def prepare_data(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty:
            return {}
        close = df['close']
        high = df['high']
        low = df['low']
        open_p = df['open']
        has_vol = ('volume' in df.columns) and (df['volume'].fillna(0).sum() > 0)
        
        from engine.indicators import compute_ema, compute_wilders_rsi
        
        # Bollinger Bands
        bb_sma = close.rolling(window=20).mean()
        bb_sigma = close.rolling(window=20).std(ddof=0)
        
        # Keltner Channels
        kc_ema = compute_ema(close, 20)
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr_20 = tr.rolling(window=20).mean()
        
        # RSIs
        rsi_fast = compute_wilders_rsi(close, 3)
        rsi_slow = compute_wilders_rsi(close, 14)
        
        # Geometry
        candle_range = high - low
        body = (close - open_p).abs()
        lower_wick = np.minimum(open_p, close) - low
        upper_wick = high - np.maximum(open_p, close)
        
        valid_range = candle_range > 0
        body_ratio = pd.Series(np.where(valid_range, body / candle_range, 1.0), index=df.index)
        lower_wick_ratio = pd.Series(np.where(valid_range, lower_wick / candle_range, 0.0), index=df.index)
        upper_wick_ratio = pd.Series(np.where(valid_range, upper_wick / candle_range, 0.0), index=df.index)
        
        return {
            'bb_sma': bb_sma,
            'bb_sigma': bb_sigma,
            'kc_ema': kc_ema,
            'atr_20': atr_20,
            'rsi_fast': rsi_fast,
            'rsi_slow': rsi_slow,
            'body_ratio': body_ratio,
            'lower_wick_ratio': lower_wick_ratio,
            'upper_wick_ratio': upper_wick_ratio,
            'has_vol': has_vol,
            'orig_indices': df.index
        }

    def generate_signals(self, df: pd.DataFrame = None, params: dict = None, precomputed: dict = None, **kwargs) -> pd.Series:
        if precomputed is None and isinstance(df, dict):
            precomputed = df
            df = None

        if not isinstance(precomputed, dict) or 'rsi_fast' not in precomputed:
            if df is None:
                return pd.Series(dtype=object)
            precomputed = self.prepare_data(df)
            
        p = params or {}
        bb_period = int(p.get("bb_period", 20))
        bb_std = float(p.get("bb_std", 2.0))
        kc_period = int(p.get("kc_period", 20))
        kc_mult = float(p.get("kc_mult", 1.5))
        rsi_fast_p = int(p.get("rsi_fast_period", 3))
        rsi_slow_p = int(p.get("rsi_slow_period", 14))
        max_body_ratio = float(p.get("max_body_ratio", 0.45))
        min_wick_ratio = float(p.get("min_wick_ratio", 0.35))
        
        close = df['close'] if df is not None else precomputed['bb_sma']
        high = df['high'] if df is not None else close
        low = df['low'] if df is not None else close
        
        from engine.indicators import compute_ema, compute_wilders_rsi
        if bb_period == 20 and bb_std == 2.5:
            bb_sma = precomputed['bb_sma']
            bb_lower = bb_sma - (bb_std * precomputed['bb_sigma'])
            bb_upper = bb_sma + (bb_std * precomputed['bb_sigma'])
        else:
            bb_sma = close.rolling(window=bb_period).mean()
            bb_sigma = close.rolling(window=bb_period).std(ddof=0)
            bb_lower = bb_sma - (bb_std * bb_sigma)
            bb_upper = bb_sma + (bb_std * bb_sigma)

        if kc_period == 20 and kc_mult == 2.0:
            kc_ema = precomputed['kc_ema']
            kc_lower = kc_ema - (kc_mult * precomputed['atr_20'])
            kc_upper = kc_ema + (kc_mult * precomputed['atr_20'])
        else:
            kc_ema = compute_ema(close, kc_period)
            tr1 = high - low
            tr2 = (high - close.shift(1)).abs()
            tr3 = (low - close.shift(1)).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=kc_period).mean()
            kc_lower = kc_ema - (kc_mult * atr)
            kc_upper = kc_ema + (kc_mult * atr)

        rsi_fast = precomputed['rsi_fast'] if rsi_fast_p == 3 else compute_wilders_rsi(close, rsi_fast_p)
        rsi_slow = precomputed['rsi_slow'] if rsi_slow_p == 14 else compute_wilders_rsi(close, rsi_slow_p)
        
        body_ratio = precomputed['body_ratio']
        lower_wick_ratio = precomputed['lower_wick_ratio']
        upper_wick_ratio = precomputed['upper_wick_ratio']
        orig_indices = precomputed.get('orig_indices', close.index)
        
        call_cond = (close <= bb_lower) & (low <= kc_lower) & (rsi_fast <= 25.0) & (rsi_slow <= 40.0) & (body_ratio <= max_body_ratio) & (lower_wick_ratio >= min_wick_ratio)
        put_cond = (close >= bb_upper) & (high >= kc_upper) & (rsi_fast >= 75.0) & (rsi_slow >= 60.0) & (body_ratio <= max_body_ratio) & (upper_wick_ratio >= min_wick_ratio)
        
        call_cond = call_cond & (~call_cond.shift(1).fillna(False))
        put_cond = put_cond & (~put_cond.shift(1).fillna(False))
        
        conflict = call_cond & put_cond
        call_cond = call_cond & (~conflict)
        put_cond = put_cond & (~conflict)

        signals = pd.Series(index=orig_indices, data=None, dtype=object)
        signals.loc[call_cond] = 'CALL'
        signals.loc[put_cond] = 'PUT'
        
        return signals
