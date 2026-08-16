import pandas as pd
import numpy as np
from .base import BaseStrategy

class BollingerBounceStrategy(BaseStrategy):
    name = "Bollinger Bounce"
    description = "Estrategia de rebote en bandas de Bollinger."

    def get_params_schema(self) -> list[dict]:
        return [
            {"name": "bb_period", "type": "int", "default": 20, "min": 2, "max": 200, "step": 1, "description": "Periodo de Bollinger"},
            {"name": "bb_std", "type": "float", "default": 2.2, "min": 0.5, "max": 5.0, "step": 0.1, "description": "Desviacion Estandar"},
            {"name": "wick_ratio", "type": "float", "default": 0.35, "min": 0.0, "max": 0.8, "step": 0.05, "description": "Min Wick Rejection Ratio"},
            {"name": "vol_mult", "type": "float", "default": 1.3, "min": 0.0, "max": 3.0, "step": 0.1, "description": "Min Volume Multiplier"}
        ]

    def prepare_data(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty:
            return {}
        close = df['close']
        high = df['high']
        low = df['low']
        open_p = df['open']
        volume = df['volume'] if 'volume' in df.columns else pd.Series(1.0, index=df.index)

        sma = close.rolling(window=20).mean()
        std = close.rolling(window=20).std(ddof=0)
        vol_sma = volume.rolling(window=20).mean()

        candle_range = (high - low).replace(0, 1e-8)
        lower_wick_ratio = (np.minimum(open_p, close) - low) / candle_range
        upper_wick_ratio = (high - np.maximum(open_p, close)) / candle_range

        return {
            'sma_20': sma,
            'std_20': std,
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
        bb_period = int(p.get("bb_period", 20))
        bb_std = float(p.get("bb_std", 2.2))
        wick_ratio = float(p.get("wick_ratio", 0.35))
        vol_mult = float(p.get("vol_mult", 1.3))
        
        if df is not None:
            close = df['close']
            high = df['high']
            low = df['low']
            open_p = df['open']
            volume = df['volume'] if 'volume' in df.columns else pd.Series(1.0, index=df.index)

            sma = close.rolling(window=bb_period).mean() if bb_period != 20 or not isinstance(precomputed, dict) or 'sma_20' not in precomputed else precomputed['sma_20']
            std = close.rolling(window=bb_period).std(ddof=0) if bb_period != 20 or not isinstance(precomputed, dict) or 'std_20' not in precomputed else precomputed['std_20']
            
            vol_sma = precomputed['vol_sma_20'] if (isinstance(precomputed, dict) and 'vol_sma_20' in precomputed) else volume.rolling(window=20).mean()
            
            candle_range = (high - low).replace(0, 1e-8)
            lower_wick_ratio = (np.minimum(open_p, close) - low) / candle_range
            upper_wick_ratio = (high - np.maximum(open_p, close)) / candle_range
            orig_indices = df.index
        elif isinstance(precomputed, dict) and 'sma_20' in precomputed:
            sma = precomputed['sma_20']
            std = precomputed['std_20']
            lower_wick_ratio = precomputed.get('lower_wick_ratio', pd.Series(1.0, index=sma.index))
            upper_wick_ratio = precomputed.get('upper_wick_ratio', pd.Series(1.0, index=sma.index))
            vol_sma = precomputed.get('vol_sma_20', pd.Series(1.0, index=sma.index))
            volume = vol_sma
            orig_indices = precomputed.get('orig_indices')
            close = sma  # approximation for index alignment if df is missing
        else:
            return pd.Series(dtype=object)
        
        upper_band = sma + (std * bb_std)
        lower_band = sma - (std * bb_std)
        
        prev_close = close.shift(1)
        prev_lower = lower_band.shift(1)
        prev_upper = upper_band.shift(1)
        
        signals = pd.Series(index=orig_indices, data=None, dtype=object)
        
        vol_filter = (vol_mult <= 0.0) | (volume >= (vol_sma * vol_mult))
        wick_call_filter = (wick_ratio <= 0.0) | (lower_wick_ratio >= wick_ratio)
        wick_put_filter = (wick_ratio <= 0.0) | (upper_wick_ratio >= wick_ratio)

        call_cond = (prev_close <= prev_lower) & (close > lower_band) & wick_call_filter & vol_filter
        put_cond = (prev_close >= prev_upper) & (close < upper_band) & wick_put_filter & vol_filter
        
        conflict = call_cond & put_cond
        call_cond = call_cond & (~conflict)
        put_cond = put_cond & (~conflict)
        
        signals.loc[call_cond] = 'CALL'
        signals.loc[put_cond] = 'PUT'
        
        return signals
