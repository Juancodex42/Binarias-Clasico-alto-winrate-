import pandas as pd
import numpy as np
from .base import BaseStrategy

class IslgRsStrategy(BaseStrategy):
    name = "Institutional Swing Liquidity Grab Sweep"
    description = "Barrido de liquidez institucional en swing highs/lows con rechazo mecha y volumen."

    def get_params_schema(self) -> list[dict]:
        return [
            {"name": "lookback_period", "type": "int", "default": 50, "min": 20, "max": 100, "description": "Swing Lookback Period"},
            {"name": "min_sweep_atr_ratio", "type": "float", "default": 0.10, "min": 0.05, "max": 0.50, "step": 0.05, "description": "Min Sweep Depth in ATR"},
            {"name": "wick_ratio", "type": "float", "default": 0.45, "min": 0.30, "max": 0.85, "description": "Min Wick Ratio"},
            {"name": "vol_mult", "type": "float", "default": 1.3, "min": 1.0, "max": 3.0, "description": "Volume Spike Multiplier"},
            {"name": "rsi_period", "type": "int", "default": 7, "min": 3, "max": 14, "description": "RSI Period"},
            {"name": "rsi_upper", "type": "float", "default": 62.0, "min": 55.0, "max": 85.0, "description": "RSI Upper Overbought Threshold"},
            {"name": "rsi_lower", "type": "float", "default": 38.0, "min": 15.0, "max": 45.0, "description": "RSI Lower Oversold Threshold"},
            {"name": "use_session_filter", "type": "bool", "default": False, "description": "Filter Active Trading Hours (7-20 UTC)"}
        ]

    def prepare_data(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty:
            return {}
        close = df['close']
        high = df['high']
        low = df['low']
        has_vol = ('volume' in df.columns) and (df['volume'].fillna(0).sum() > 0)
        volume = df['volume'] if 'volume' in df.columns else pd.Series(0, index=df.index)
        
        # ATR 14
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        
        from engine.indicators import compute_wilders_rsi
        rsi_7 = compute_wilders_rsi(close, 7)
        rsi_14 = compute_wilders_rsi(close, 14)
        vol_sma = volume.rolling(window=20).mean() if has_vol else pd.Series(0, index=df.index)
        
        # Datetime for session filter
        hours = None
        if 'open_time' in df.columns:
            try:
                dt_series = pd.to_datetime(df['open_time'], unit='s', errors='coerce')
                hours = dt_series.dt.hour
            except Exception:
                pass
        elif 'datetime' in df.columns:
            try:
                dt_series = pd.to_datetime(df['datetime'], errors='coerce')
                hours = dt_series.dt.hour
            except Exception:
                pass

        return {
            'atr_14': atr,
            'rsi_7': rsi_7,
            'rsi_14': rsi_14,
            'vol_sma': vol_sma,
            'has_vol': has_vol,
            'hours': hours,
            'orig_indices': df.index
        }

    def generate_signals(self, df: pd.DataFrame = None, params: dict = None, precomputed: dict = None, **kwargs) -> pd.Series:
        if precomputed is None and isinstance(df, dict):
            precomputed = df
            df = None

        if not isinstance(precomputed, dict) or 'atr_14' not in precomputed:
            if df is None:
                return pd.Series(dtype=object)
            precomputed = self.prepare_data(df)

        p = params or {}
        lookback = int(p.get("lookback_period", 50))
        sweep_ratio = float(p.get("min_sweep_atr_ratio", 0.10))
        wick_ratio = float(p.get("wick_ratio", 0.45))
        vol_mult = float(p.get("vol_mult", 1.3))
        rsi_period = int(p.get("rsi_period", 7))
        rsi_upper = float(p.get("rsi_upper", 62.0))
        rsi_lower = float(p.get("rsi_lower", 38.0))
        use_session_filter = bool(p.get("use_session_filter", False))
        
        close = df['close'] if df is not None else precomputed['atr_14']
        high = df['high'] if df is not None else close
        low = df['low'] if df is not None else close
        open_p = df['open'] if df is not None else close
        volume = df['volume'] if (df is not None and 'volume' in df.columns) else pd.Series(0, index=close.index)
        
        atr = precomputed['atr_14']
        
        # Rolling Swing Levels (excluding current bar)
        swing_high = high.shift(1).rolling(window=lookback).max()
        swing_low = low.shift(1).rolling(window=lookback).min()
        
        # Candle Geometry
        candle_range = high - low
        lower_wick = np.minimum(open_p, close) - low
        upper_wick = high - np.maximum(open_p, close)
        
        valid_range = candle_range > 0
        lower_wick_ratio = pd.Series(np.where(valid_range, lower_wick / candle_range, 0.0), index=close.index)
        upper_wick_ratio = pd.Series(np.where(valid_range, upper_wick / candle_range, 0.0), index=close.index)
        
        from engine.indicators import compute_wilders_rsi
        if rsi_period == 7:
            rsi = precomputed['rsi_7']
        elif rsi_period == 14:
            rsi = precomputed['rsi_14']
        else:
            rsi = compute_wilders_rsi(close, rsi_period)
        
        has_vol = precomputed.get('has_vol', False)
        if has_vol:
            vol_sma = precomputed.get('vol_sma', volume.rolling(window=20).mean())
            vol_spike = (vol_sma == 0) | (volume >= (vol_sma * vol_mult))
        else:
            vol_spike = pd.Series(True, index=close.index)

        session_ok = pd.Series(True, index=close.index)
        if use_session_filter and precomputed.get('hours') is not None:
            hours = precomputed['hours']
            session_ok = (hours >= 7) & (hours <= 20)

        put_sweep = (high > swing_high) & ((high - swing_high) >= (sweep_ratio * atr)) & (close <= (swing_high + 0.05 * atr)) & (upper_wick_ratio >= wick_ratio) & vol_spike & (rsi >= rsi_upper) & session_ok
        call_sweep = (low < swing_low) & ((swing_low - low) >= (sweep_ratio * atr)) & (close >= (swing_low - 0.05 * atr)) & (lower_wick_ratio >= wick_ratio) & vol_spike & (rsi <= rsi_lower) & session_ok
        
        call_sweep = call_sweep & (~call_sweep.shift(1).fillna(False))
        put_sweep = put_sweep & (~put_sweep.shift(1).fillna(False))
        
        conflict = call_sweep & put_sweep
        call_sweep = call_sweep & (~conflict)
        put_sweep = put_sweep & (~conflict)

        signals = pd.Series(index=close.index, data=None, dtype=object)
        signals.loc[call_sweep] = 'CALL'
        signals.loc[put_sweep] = 'PUT'
        
        return signals
