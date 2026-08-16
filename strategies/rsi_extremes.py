import pandas as pd
import numpy as np
from .base import BaseStrategy

class RsiExtremesStrategy(BaseStrategy):
    name = "RSI Extremes"
    description = "Estrategia de niveles extremos de RSI."

    def get_params_schema(self) -> list[dict]:
        return [
            {"name": "rsi_period", "type": "int", "default": 14, "min": 2, "max": 100, "step": 1, "description": "Periodo del RSI"},
            {"name": "oversold", "type": "float", "default": 25, "min": 10, "max": 50, "step": 1, "description": "Nivel de sobreventa"},
            {"name": "overbought", "type": "float", "default": 75, "min": 50, "max": 90, "step": 1, "description": "Nivel de sobrecompra"},
            {"name": "wick_ratio", "type": "float", "default": 0.35, "min": 0.0, "max": 0.8, "step": 0.05, "description": "Min Wick Rejection Ratio"},
            {"name": "vol_mult", "type": "float", "default": 1.3, "min": 0.0, "max": 3.0, "step": 0.1, "description": "Min Volume Multiplier"}
        ]

    def prepare_data(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty:
            return {}
        from engine.indicators import compute_wilders_rsi
        close = df['close']
        high = df['high']
        low = df['low']
        open_p = df['open']
        volume = df['volume'] if 'volume' in df.columns else pd.Series(1.0, index=df.index)

        rsi_14 = compute_wilders_rsi(close, 14)
        vol_sma = volume.rolling(window=20).mean()

        candle_range = (high - low).replace(0, 1e-8)
        lower_wick_ratio = (np.minimum(open_p, close) - low) / candle_range
        upper_wick_ratio = (high - np.maximum(open_p, close)) / candle_range

        return {
            'rsi_14': rsi_14,
            'vol_sma_20': vol_sma,
            'lower_wick_ratio': lower_wick_ratio,
            'upper_wick_ratio': upper_wick_ratio,
            'orig_indices': df.index
        }

    def generate_signals(self, df: pd.DataFrame = None, params: dict = None, precomputed: dict = None, **kwargs) -> pd.Series:
        if precomputed is None and isinstance(df, dict):
            precomputed = df
            df = None

        p = params or {}
        rsi_period = int(p.get("rsi_period", 14))
        oversold = float(p.get("oversold", 25))
        overbought = float(p.get("overbought", 75))
        wick_ratio = float(p.get("wick_ratio", 0.35))
        vol_mult = float(p.get("vol_mult", 1.3))
        
        from engine.indicators import compute_wilders_rsi
        if df is not None:
            close = df['close']
            high = df['high']
            low = df['low']
            open_p = df['open']
            volume = df['volume'] if 'volume' in df.columns else pd.Series(1.0, index=df.index)

            orig_indices = df.index
            rsi = precomputed['rsi_14'] if (rsi_period == 14 and isinstance(precomputed, dict) and 'rsi_14' in precomputed) else compute_wilders_rsi(close, rsi_period)
            vol_sma = precomputed['vol_sma_20'] if (isinstance(precomputed, dict) and 'vol_sma_20' in precomputed) else volume.rolling(window=20).mean()
            
            candle_range = (high - low).replace(0, 1e-8)
            lower_wick_ratio = (np.minimum(open_p, close) - low) / candle_range
            upper_wick_ratio = (high - np.maximum(open_p, close)) / candle_range
        elif isinstance(precomputed, dict) and 'rsi_14' in precomputed:
            rsi = precomputed['rsi_14']
            lower_wick_ratio = precomputed.get('lower_wick_ratio', pd.Series(1.0, index=rsi.index))
            upper_wick_ratio = precomputed.get('upper_wick_ratio', pd.Series(1.0, index=rsi.index))
            vol_sma = precomputed.get('vol_sma_20', pd.Series(1.0, index=rsi.index))
            volume = vol_sma
            orig_indices = precomputed.get('orig_indices')
        else:
            return pd.Series(dtype=object)
        
        signals = pd.Series(index=orig_indices, data=None, dtype=object)
        
        vol_filter = (vol_mult <= 0.0) | (volume >= (vol_sma * vol_mult))
        wick_call_filter = (wick_ratio <= 0.0) | (lower_wick_ratio >= wick_ratio)
        wick_put_filter = (wick_ratio <= 0.0) | (upper_wick_ratio >= wick_ratio)

        call_cond = (rsi < oversold) & wick_call_filter & vol_filter
        put_cond = (rsi > overbought) & wick_put_filter & vol_filter
        
        conflict = call_cond & put_cond
        call_cond = call_cond & (~conflict)
        put_cond = put_cond & (~conflict)
        
        signals.loc[call_cond] = 'CALL'
        signals.loc[put_cond] = 'PUT'
        
        return signals
