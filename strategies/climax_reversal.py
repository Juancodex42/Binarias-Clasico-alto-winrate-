import pandas as pd
import numpy as np
from .base import BaseStrategy

class ClimaxReversalStrategy(BaseStrategy):
    name = "Multi-Candle Climax & Streak Reversal"
    description = "Agotamiento por rachas consecutivas (3-6 velas), mechas de rechazo extremas y reduccion de volumen/cuerpo en niveles clave."

    def get_params_schema(self) -> list[dict]:
        return [
            {"name": "streak_len", "type": "int", "default": 3, "min": 3, "max": 6, "description": "Consecutive Candles in Trend"},
            {"name": "wick_ratio", "type": "float", "default": 0.40, "min": 0.40, "max": 0.80, "description": "Min Climax Wick Ratio"},
            {"name": "vol_mult", "type": "float", "default": 1.8, "min": 1.0, "max": 3.0, "description": "Volume Expansion Spike"},
            {"name": "rsi_period", "type": "int", "default": 7, "min": 3, "max": 14, "description": "RSI Exhaustion Period"},
            {"name": "check_exhaustion", "type": "bool", "default": True, "description": "Require Decreasing Body Sizes"},
            {"name": "bb_period", "type": "int", "default": 20, "min": 10, "max": 50, "description": "Bollinger Filter Period"},
            {"name": "bb_std", "type": "float", "default": 2.0, "min": 1.5, "max": 3.5, "description": "Bollinger Filter Std Dev"}
        ]

    def prepare_data(self, df: pd.DataFrame) -> dict:
        if df is None or df.empty:
            return {}
        close = df['close']
        high = df['high']
        low = df['low']
        open_p = df['open']
        has_vol = ('volume' in df.columns) and (df['volume'].fillna(0).sum() > 0)
        volume = df['volume'] if 'volume' in df.columns else pd.Series(0, index=df.index)

        # Geometry
        candle_range = high - low
        body = (close - open_p).abs()
        lower_wick = np.minimum(open_p, close) - low
        upper_wick = high - np.maximum(open_p, close)

        valid_range = candle_range > 0
        lower_wick_ratio = pd.Series(np.where(valid_range, lower_wick / candle_range, 0.0), index=df.index)
        upper_wick_ratio = pd.Series(np.where(valid_range, upper_wick / candle_range, 0.0), index=df.index)
        body_ratio = pd.Series(np.where(valid_range, body / candle_range, 1.0), index=df.index)

        # Direction: 1 for bullish candle (close > open), -1 for bearish candle (close < open), 0 for flat
        direction = np.sign(close - open_p)

        from engine.indicators import compute_wilders_rsi
        rsi_7 = compute_wilders_rsi(close, 7)
        rsi_14 = compute_wilders_rsi(close, 14)
        vol_sma = volume.rolling(window=20).mean() if has_vol else pd.Series(0, index=df.index)

        # Bollinger Bands
        bb_sma = close.rolling(window=20).mean()
        bb_std_dev = close.rolling(window=20).std(ddof=0)

        return {
            'body': body,
            'candle_range': candle_range,
            'lower_wick_ratio': lower_wick_ratio,
            'upper_wick_ratio': upper_wick_ratio,
            'body_ratio': body_ratio,
            'direction': direction,
            'rsi_7': rsi_7,
            'rsi_14': rsi_14,
            'vol_sma': vol_sma,
            'bb_sma': bb_sma,
            'bb_std_dev': bb_std_dev,
            'has_vol': has_vol,
            'orig_indices': df.index
        }

    def generate_signals(self, df: pd.DataFrame = None, params: dict = None, precomputed: dict = None, **kwargs) -> pd.Series:
        if precomputed is None and isinstance(df, dict):
            precomputed = df
            df = None

        if not isinstance(precomputed, dict) or 'direction' not in precomputed:
            if df is None:
                return pd.Series(dtype=object)
            precomputed = self.prepare_data(df)

        p = params or {}
        streak_len = int(p.get("streak_len", 3))
        wick_ratio = float(p.get("wick_ratio", 0.40))
        vol_mult = float(p.get("vol_mult", 1.8))
        rsi_period = int(p.get("rsi_period", 7))
        check_exhaustion = bool(p.get("check_exhaustion", True))
        bb_period = int(p.get("bb_period", 20))
        bb_std = float(p.get("bb_std", 2.0))

        close = df['close'] if df is not None else precomputed['bb_sma']
        high = df['high'] if df is not None else close
        low = df['low'] if df is not None else close
        volume = df['volume'] if (df is not None and 'volume' in df.columns) else pd.Series(0, index=close.index)

        direction = precomputed['direction']
        body = precomputed['body']
        lower_wick_ratio = precomputed['lower_wick_ratio']
        upper_wick_ratio = precomputed['upper_wick_ratio']
        has_vol = precomputed.get('has_vol', False)

        from engine.indicators import compute_wilders_rsi
        if rsi_period == 7:
            rsi = precomputed['rsi_7']
        elif rsi_period == 14:
            rsi = precomputed['rsi_14']
        else:
            rsi = compute_wilders_rsi(close, rsi_period)

        # Count consecutive bullish/bearish candles
        # Bullish streak: last N candles (including current) had direction == 1
        bull_streak = pd.Series(True, index=close.index)
        bear_streak = pd.Series(True, index=close.index)

        for i in range(streak_len):
            bull_streak = bull_streak & (direction.shift(i) == 1)
            bear_streak = bear_streak & (direction.shift(i) == -1)

        # Body exhaustion check: body size decreasing on last 2-3 candles
        if check_exhaustion:
            exhaustion_bull = (body <= body.shift(1)) & (body.shift(1) <= body.shift(2))
            exhaustion_bear = (body <= body.shift(1)) & (body.shift(1) <= body.shift(2))
        else:
            exhaustion_bull = pd.Series(True, index=close.index)
            exhaustion_bear = pd.Series(True, index=close.index)

        # Volume expansion on climax candle
        if has_vol:
            vol_sma = precomputed.get('vol_sma', volume.rolling(window=20).mean())
            vol_spike = (vol_sma == 0) | (volume >= (vol_sma * vol_mult))
        else:
            vol_spike = pd.Series(True, index=close.index)

        # Bollinger filter: PUT near upper BB, CALL near lower BB
        if bb_period == 20:
            bb_sma = precomputed['bb_sma']
            bb_std_dev = precomputed['bb_std_dev']
        else:
            bb_sma = close.rolling(window=bb_period).mean()
            bb_std_dev = close.rolling(window=bb_period).std(ddof=0)

        bb_upper = bb_sma + (bb_std * bb_std_dev)
        bb_lower = bb_sma - (bb_std * bb_std_dev)

        put_cond = bull_streak & (upper_wick_ratio >= wick_ratio) & vol_spike & (high >= bb_upper) & (rsi >= 60.0) & exhaustion_bull
        call_cond = bear_streak & (lower_wick_ratio >= wick_ratio) & vol_spike & (low <= bb_lower) & (rsi <= 40.0) & exhaustion_bear

        call_cond = call_cond & (~call_cond.shift(1).fillna(False))
        put_cond = put_cond & (~put_cond.shift(1).fillna(False))

        conflict = call_cond & put_cond
        call_cond = call_cond & (~conflict)
        put_cond = put_cond & (~conflict)

        signals = pd.Series(index=close.index, data=None, dtype=object)
        signals.loc[call_cond] = 'CALL'
        signals.loc[put_cond] = 'PUT'

        return signals
