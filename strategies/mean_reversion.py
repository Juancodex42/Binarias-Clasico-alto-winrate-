import pandas as pd
import numpy as np
from .base import BaseStrategy

class MeanReversionStrategy(BaseStrategy):
    name = "Mean Reversion"
    description = "Mean reversion strategy based on SMA and ATR filter."

    def get_params_schema(self) -> list[dict]:
        return [
            {"name": "sma_period", "type": "int", "default": 20, "min": 2, "max": 200, "step": 1, "description": "Periodo de la SMA"},
            {"name": "threshold", "type": "float", "default": 0.015, "min": 0.001, "max": 0.1, "step": 0.001, "description": "Umbral de desviacion (1.5% = 0.015)"},
            {"name": "atr_period", "type": "int", "default": 14, "min": 2, "max": 100, "step": 1, "description": "Periodo del ATR"},
            {"name": "atr_threshold_percentile", "type": "float", "default": 50, "min": 10, "max": 90, "step": 5, "description": "Percentil maximo de ATR permitido (para rango)"}
        ]

    def prepare_data(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty:
            return {}
        close = df['close']
        high = df['high']
        low = df['low']
        sma_20 = close.rolling(window=20).mean()
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr_14 = tr.rolling(window=14).mean()
        return {
            'sma_20': sma_20,
            'atr_14': atr_14,
            'orig_indices': df.index
        }

    def generate_signals(self, df: pd.DataFrame = None, params: dict = None, precomputed: dict = None, **kwargs) -> pd.Series:
        if precomputed is None and isinstance(df, dict):
            precomputed = df
            df = None

        p = params or {}
        sma_period = int(p.get("sma_period", 20))
        threshold = float(p.get("threshold", 0.015))
        atr_period = int(p.get("atr_period", 14))
        atr_percentile = float(p.get("atr_threshold_percentile", 50))
        std_devs = float(p.get("std_devs", 0.0))
        rsi_filter = bool(p.get("rsi_filter", False))
        
        if df is not None:
            close = df['close']
            high = df['high']
            low = df['low']
            orig_indices = df.index
        elif isinstance(precomputed, dict) and 'orig_indices' in precomputed:
            orig_indices = precomputed['orig_indices']
            close = precomputed.get('sma_20', pd.Series(dtype=float))
            high = close
            low = close
        else:
            return pd.Series(dtype=object)

        sma = precomputed['sma_20'] if (sma_period == 20 and isinstance(precomputed, dict) and 'sma_20' in precomputed) else close.rolling(window=sma_period).mean()
        
        if std_devs > 0:
            rolling_std = close.rolling(window=sma_period).std()
            upper_band = sma + (rolling_std * std_devs)
            lower_band = sma - (rolling_std * std_devs)
        else:
            upper_band = sma * (1 + threshold)
            lower_band = sma * (1 - threshold)
        
        if atr_period == 14 and isinstance(precomputed, dict) and 'atr_14' in precomputed:
            atr = precomputed['atr_14']
        else:
            tr1 = high - low
            tr2 = (high - close.shift(1)).abs()
            tr3 = (low - close.shift(1)).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=atr_period).mean()
        
        atr_limit = atr.rolling(window=1000, min_periods=100).quantile(atr_percentile / 100.0)
        ranging_market = atr < atr_limit
        
        if rsi_filter:
            delta = close.diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean().replace(0, np.nan)
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsi_call = rsi <= 35
            rsi_put = rsi >= 65
        else:
            rsi_call = True
            rsi_put = True
        
        signals = pd.Series(index=orig_indices, data=None, dtype=object)
        
        call_cond = (close < lower_band) & ranging_market & rsi_call
        put_cond = (close > upper_band) & ranging_market & rsi_put
        
        signals.loc[call_cond] = 'CALL'
        signals.loc[put_cond] = 'PUT'
        
        return signals

