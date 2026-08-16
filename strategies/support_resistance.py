import pandas as pd
import numpy as np
from .base import BaseStrategy

class SupportResistanceStrategy(BaseStrategy):
    name = "Support/Resistance"
    description = "Estrategia de rebote en soportes y resistencias."

    def get_params_schema(self) -> list[dict]:
        return [
            {"name": "lookback", "type": "int", "default": 50, "min": 10, "max": 500, "step": 5, "description": "Periodo de busqueda de S/R"},
            {"name": "proximity", "type": "float", "default": 0.003, "min": 0.0001, "max": 0.05, "step": 0.0001, "description": "Proximidad (0.3% = 0.003)"}
        ]

    def prepare_data(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty:
            return {}
        high = df['high']
        low = df['low']
        rolling_high = high.rolling(window=50).max().shift(1)
        rolling_low = low.rolling(window=50).min().shift(1)
        return {
            'rolling_high_50': rolling_high,
            'rolling_low_50': rolling_low,
            'orig_indices': df.index
        }

    def generate_signals(self, df: pd.DataFrame = None, params: dict = None, precomputed: dict = None, **kwargs) -> pd.Series:
        if precomputed is None and isinstance(df, dict):
            precomputed = df
            df = None

        p = params or {}
        lookback = int(p.get("lookback", p.get("sr_lookback", 50)))
        proximity = float(p.get("proximity", p.get("touch_threshold", 0.003)))
        wick_ratio = float(p.get("bounce_wick_ratio", 0.0))
        
        if df is not None:
            high = df['high']
            low = df['low']
            close = df['close']
            open_p = df['open']
            orig_indices = df.index
            if lookback == 50 and isinstance(precomputed, dict) and 'rolling_high_50' in precomputed:
                rolling_high = precomputed['rolling_high_50']
                rolling_low = precomputed['rolling_low_50']
            else:
                rolling_high = high.rolling(window=lookback).max().shift(1)
                rolling_low = low.rolling(window=lookback).min().shift(1)
        elif isinstance(precomputed, dict) and 'rolling_high_50' in precomputed:
            rolling_high = precomputed['rolling_high_50']
            rolling_low = precomputed['rolling_low_50']
            orig_indices = precomputed.get('orig_indices')
            close = rolling_high
            high = rolling_high
            low = rolling_low
            open_p = rolling_high
        else:
            return pd.Series(dtype=object)
        
        signals = pd.Series(index=orig_indices, data=None, dtype=object)
        
        candle_range = (high - low).replace(0, np.nan)
        lower_wick = (np.minimum(open_p, close) - low) / candle_range
        upper_wick = (high - np.maximum(open_p, close)) / candle_range
        
        call_cond = (low <= rolling_low * (1 + proximity)) & (close > rolling_low) & (close.diff() > 0)
        put_cond = (high >= rolling_high * (1 - proximity)) & (close < rolling_high) & (close.diff() < 0)
        
        if wick_ratio > 0:
            call_cond = call_cond & (lower_wick >= wick_ratio)
            put_cond = put_cond & (upper_wick >= wick_ratio)
        
        conflict = call_cond & put_cond
        call_cond = call_cond & (~conflict)
        put_cond = put_cond & (~conflict)
        
        signals.loc[call_cond] = 'CALL'
        signals.loc[put_cond] = 'PUT'
        
        return signals

