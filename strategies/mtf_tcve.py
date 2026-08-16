import pandas as pd
import numpy as np
from .base import BaseStrategy

class MtfTcveStrategy(BaseStrategy):
    name = "MTF Trend Volume Exhaustion"
    description = "Confluencia MTF, rechazo de mecha y agotamiento de volumen."

    def get_params_schema(self) -> list[dict]:
        return [
            {"name": "htf_multiplier", "type": "int", "default": 5, "min": 2, "max": 15, "description": "Resample MTF Multiplier"},
            {"name": "htf_ema_fast", "type": "int", "default": 20, "min": 5, "max": 50, "description": "HTF Fast EMA"},
            {"name": "htf_ema_slow", "type": "int", "default": 50, "min": 20, "max": 100, "description": "HTF Slow EMA"},
            {"name": "bb_period", "type": "int", "default": 20, "min": 10, "max": 50, "description": "Bollinger Period"},
            {"name": "bb_std", "type": "float", "default": 2.0, "min": 1.5, "max": 3.5, "description": "Bollinger Std Dev"},
            {"name": "wick_ratio", "type": "float", "default": 0.35, "min": 0.20, "max": 0.75, "description": "Min Wick Rejection Ratio"},
            {"name": "vol_mult", "type": "float", "default": 1.3, "min": 1.0, "max": 3.0, "description": "Volume Spike Multiplier"},
            {"name": "rsi_period", "type": "int", "default": 7, "min": 3, "max": 14, "description": "RSI Period"},
            {"name": "rsi_oversold", "type": "float", "default": 25.0, "min": 10.0, "max": 35.0, "description": "RSI Oversold"},
            {"name": "rsi_overbought", "type": "float", "default": 75.0, "min": 65.0, "max": 90.0, "description": "RSI Overbought"}
        ]

    def prepare_data(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty:
            return {}
        close = df['close']
        has_vol = ('volume' in df.columns) and (df['volume'].fillna(0).sum() > 0)
        volume = df['volume'] if 'volume' in df.columns else pd.Series(0, index=df.index)
        
        from engine.indicators import compute_ema, compute_wilders_rsi
        ema_20 = compute_ema(close, 20)
        ema_50 = compute_ema(close, 50)
        rsi = compute_wilders_rsi(close, 7)
        vol_sma = volume.rolling(window=20).mean() if has_vol else pd.Series(0, index=df.index)
        
        return {
            'ema_20': ema_20,
            'ema_50': ema_50,
            'rsi_7': rsi,
            'vol_sma': vol_sma,
            'has_vol': has_vol,
            'orig_indices': df.index
        }

    def generate_signals(self, df: pd.DataFrame = None, params: dict = None, precomputed: dict = None, **kwargs) -> pd.Series:
        if precomputed is None and isinstance(df, dict):
            precomputed = df
            df = None

        if not isinstance(precomputed, dict) or 'ema_20' not in precomputed:
            if df is None:
                return pd.Series(dtype=object)
            precomputed = self.prepare_data(df)

        p = params or {}
        bb_period = int(p.get("bb_period", 20))
        bb_std = float(p.get("bb_std", 2.0))
        wick_ratio = float(p.get("wick_ratio", 0.35))
        vol_mult = float(p.get("vol_mult", 1.3))
        rsi_period = int(p.get("rsi_period", 7))
        rsi_oversold = float(p.get("rsi_oversold", 25.0))
        rsi_overbought = float(p.get("rsi_overbought", 75.0))
        
        close = df['close']
        high = df['high']
        low = df['low']
        open_p = df['open']
        volume = df['volume'] if 'volume' in df.columns else pd.Series(0, index=df.index)
        
        from engine.indicators import compute_ema, compute_wilders_rsi
        ema_20 = precomputed['ema_20']
        ema_50 = precomputed['ema_50']
        
        ema_trend_call = (ema_20 > ema_50) & (ema_20.diff() > 0)
        ema_trend_put = (ema_20 < ema_50) & (ema_20.diff() < 0)
        
        bb_sma = close.rolling(window=bb_period).mean()
        bb_sigma = close.rolling(window=bb_period).std(ddof=0)
        bb_lower = bb_sma - (bb_std * bb_sigma)
        bb_upper = bb_sma + (bb_std * bb_sigma)
        
        rsi = precomputed['rsi_7'] if rsi_period == 7 else compute_wilders_rsi(close, rsi_period)
        
        has_vol = precomputed.get('has_vol', False)
        if has_vol:
            vol_sma = precomputed.get('vol_sma', volume.rolling(window=20).mean())
            vol_climax = (vol_sma == 0) | (volume >= (vol_sma * vol_mult))
        else:
            vol_climax = pd.Series(True, index=df.index)
        
        candle_range = high - low
        lower_wick = np.minimum(open_p, close) - low
        upper_wick = high - np.maximum(open_p, close)
        
        valid_range = candle_range > 0
        lower_wick_ratio = np.where(valid_range, lower_wick / candle_range, 0.0)
        upper_wick_ratio = np.where(valid_range, upper_wick / candle_range, 0.0)
        
        call_cond = ema_trend_call & (low <= bb_lower) & (rsi <= rsi_oversold) & (lower_wick_ratio >= wick_ratio) & vol_climax
        put_cond = ema_trend_put & (high >= bb_upper) & (rsi >= rsi_overbought) & (upper_wick_ratio >= wick_ratio) & vol_climax
        
        call_cond = call_cond & (~call_cond.shift(1).fillna(False))
        put_cond = put_cond & (~put_cond.shift(1).fillna(False))
        
        conflict = call_cond & put_cond
        call_cond = call_cond & (~conflict)
        put_cond = put_cond & (~conflict)

        signals = pd.Series(index=df.index, data=None, dtype=object)
        signals.loc[call_cond] = 'CALL'
        signals.loc[put_cond] = 'PUT'
        
        return signals
