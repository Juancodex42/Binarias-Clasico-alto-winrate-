import pandas as pd
import numpy as np
from .base import BaseStrategy

class DailyConfluenceStrategy(BaseStrategy):
    name = "Confluencia Diaria Multi-Activo"
    description = "Estrategia de alta probabilidad basada en confluencia EMA Semanal/Diaria, RSI y filtro de mechas."

    def get_params_schema(self) -> list[dict]:
        return [
            {"name": "ema_weekly_period", "type": "int", "default": 20, "min": 5, "max": 100, "description": "Periodo EMA Semanal"},
            {"name": "ema_daily_period", "type": "int", "default": 20, "min": 5, "max": 100, "description": "Periodo EMA Diario"},
            {"name": "rsi_period", "type": "int", "default": 14, "min": 2, "max": 30, "description": "Periodo RSI"},
            {"name": "pullback_tolerance", "type": "float", "default": 0.012, "min": 0.001, "max": 0.05, "description": "Tolerancia Pullback"},
            {"name": "rsi_min_call", "type": "float", "default": 20.0, "min": 10.0, "max": 50.0, "description": "RSI Mínimo CALL"},
            {"name": "rsi_max_call", "type": "float", "default": 60.0, "min": 30.0, "max": 70.0, "description": "RSI Máximo CALL"},
            {"name": "rsi_min_put", "type": "float", "default": 40.0, "min": 30.0, "max": 70.0, "description": "RSI Mínimo PUT"},
            {"name": "rsi_max_put", "type": "float", "default": 80.0, "min": 50.0, "max": 90.0, "description": "RSI Máximo PUT"},
            {"name": "wick_rejection_ratio", "type": "float", "default": 0.25, "min": 0.1, "max": 0.8, "description": "Ratio Mínimo Rechazo Mecha"}
        ]

    def __init__(self, ema_weekly_period=20, ema_daily_period=20, rsi_period=14, volume_period=20, pullback_tolerance=0.012, rsi_min_call=20.0, rsi_max_call=60.0, rsi_min_put=40.0, rsi_max_put=80.0, wick_rejection_ratio=0.25, direction_filter='BOTH', exclude_weekends=True, allowed_days=None):
        self.ema_weekly_period = ema_weekly_period
        self.ema_daily_period = ema_daily_period
        self.rsi_period = rsi_period
        self.volume_period = volume_period
        self.pullback_tolerance = pullback_tolerance
        self.rsi_min_call = rsi_min_call
        self.rsi_max_call = rsi_max_call
        self.rsi_min_put = rsi_min_put
        self.rsi_max_put = rsi_max_put
        self.wick_rejection_ratio = wick_rejection_ratio
        self.direction_filter = direction_filter.upper() if isinstance(direction_filter, str) else 'BOTH'
        self.exclude_weekends = exclude_weekends
        self.allowed_days = allowed_days if allowed_days is not None else [0, 1, 2, 3, 4]

    def _resample_to_weekly(self, df_daily: pd.DataFrame) -> pd.DataFrame:
        df = df_daily.copy()
        if 'open_time' not in df.columns:
            return pd.DataFrame()
        if df['open_time'].max() > 2**32:
            df['datetime'] = pd.to_datetime(df['open_time'], unit='ms')
        else:
            df['datetime'] = pd.to_datetime(df['open_time'], unit='s')
        
        df.set_index('datetime', inplace=True)
        agg_dict = {
            'open_time': 'first',
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last'
        }
        if 'volume' in df.columns:
            agg_dict['volume'] = 'sum'
            
        df_weekly = df.resample('W-MON').agg(agg_dict)
        df_weekly.dropna(subset=['close'], inplace=True)
        df_weekly.reset_index(inplace=True)
        return df_weekly

    def prepare_data(self, df_daily: pd.DataFrame) -> dict:
        if df_daily is None or df_daily.empty:
            return {}
            
        df = df_daily.copy()
        df['_orig_idx_'] = df_daily.index
        if df['open_time'].max() > 2**32:
            df['datetime'] = pd.to_datetime(df['open_time'], unit='ms')
        else:
            df['datetime'] = pd.to_datetime(df['open_time'], unit='s')
            
        close = df['close']
        has_vol = ('volume' in df.columns) and (df['volume'].fillna(0).sum() > 0)
        volume = df['volume'] if 'volume' in df.columns else pd.Series(0, index=df.index)
        
        from engine.indicators import compute_ema, compute_wilders_rsi
        df['ema_daily'] = compute_ema(close, self.ema_daily_period)
        df['rsi_daily'] = compute_wilders_rsi(close, self.rsi_period)
        df['rsi_fast'] = compute_wilders_rsi(close, 3)
        df['vol_sma'] = volume.rolling(window=self.volume_period).mean() if has_vol else pd.Series(0, index=df.index)
        
        df_weekly = self._resample_to_weekly(df_daily)
        if not df_weekly.empty:
            df_weekly['ema_weekly'] = compute_ema(df_weekly['close'], self.ema_weekly_period)
            df_weekly['ema_weekly_dir'] = df_weekly['ema_weekly'].diff()
            
            is_ms = df_weekly['open_time'].max() > 2**32
            offset = 7 * 24 * 60 * 60 * 1000 if is_ms else 7 * 24 * 60 * 60
            df_weekly['completion_time'] = (df_weekly['open_time'] + offset).astype('int64')
            df['open_time'] = df['open_time'].astype('int64')
            
            df.sort_values('open_time', inplace=True)
            df_weekly.sort_values('completion_time', inplace=True)
            
            df_merged = pd.merge_asof(
                df,
                df_weekly[['completion_time', 'ema_weekly', 'ema_weekly_dir', 'close']],
                left_on='open_time',
                right_on='completion_time',
                direction='backward',
                suffixes=('', '_weekly')
            )
            df_merged.sort_values('_orig_idx_', inplace=True)
        else:
            df_merged = df.copy()
            df_merged['ema_weekly'] = np.nan
            df_merged['ema_weekly_dir'] = np.nan
            df_merged['close_weekly'] = np.nan

        high = df_merged['high']
        low = df_merged['low']
        tr1 = high - low
        tr2 = (high - df_merged['close'].shift(1)).abs()
        tr3 = (low - df_merged['close'].shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df_merged['atr_14'] = tr.rolling(window=14).mean()
        
        records = df_merged.to_dict('records')
        return {
            'df_merged': df_merged,
            'records': records,
            'orig_indices': df_daily.index,
            'has_vol': has_vol
        }

    def generate_signals(self, df_daily: pd.DataFrame = None, params: dict = None, precomputed: dict = None, as_list: bool = False, **kwargs) -> pd.Series | list[dict]:
        # Handle positional or kwargs precomputed passing
        if precomputed is None and isinstance(df_daily, dict):
            precomputed = df_daily
            df_daily = None

        if not isinstance(precomputed, dict) or 'df_merged' not in precomputed or 'orig_indices' not in precomputed:
            if df_daily is None:
                return [] if as_list else pd.Series(dtype=object)
            precomputed = self.prepare_data(df_daily)
            
        df_m = precomputed['df_merged']
        orig_indices = precomputed['orig_indices']
        has_vol = precomputed.get('has_vol', True)
        
        p = params or {}
        pullback_tol_param = float(p.get("pullback_tolerance", self.pullback_tolerance))
        rsi_min_call = float(p.get("rsi_min_call", self.rsi_min_call))
        rsi_max_call = float(p.get("rsi_max_call", self.rsi_max_call))
        rsi_min_put = float(p.get("rsi_min_put", self.rsi_min_put))
        rsi_max_put = float(p.get("rsi_max_put", self.rsi_max_put))
        wick_rejection_min = float(p.get("wick_rejection_ratio", self.wick_rejection_ratio))
        put_wick_min = float(p.get("put_wick_rejection_ratio", wick_rejection_min))
        regime_min_move = float(p.get("regime_min_move", 0.002))
        direction_filter = p.get("direction_filter", self.direction_filter)
        if isinstance(direction_filter, str):
            direction_filter = direction_filter.upper()

        warmup_period = max(14, min(60, len(df_m) // 3)) if len(df_m) < 180 else 60
        warmup_mask = np.arange(len(df_m)) >= warmup_period
        
        close = df_m['close']
        open_p = df_m['open']
        high = df_m['high']
        low = df_m['low']
        ema_d = df_m['ema_daily']
        rsi_d = df_m['rsi_daily']
        rsi_f = df_m.get('rsi_fast', pd.Series(np.nan, index=df_m.index))
        ema_w = df_m.get('ema_weekly', pd.Series(np.nan, index=df_m.index))
        ema_w_dir = df_m.get('ema_weekly_dir', pd.Series(np.nan, index=df_m.index))
        close_w = df_m.get('close_weekly', pd.Series(np.nan, index=df_m.index))
        atr = df_m.get('atr_14', pd.Series(np.nan, index=df_m.index))
        
        # 1. Weekly Trend
        weekly_bull = (close_w > ema_w) & (ema_w_dir > 0)
        weekly_bear = (close_w < ema_w) & (ema_w_dir < 0)
        
        # 2. Regime Move
        if regime_min_move > 0:
            ema_prev = ema_w.shift(28)
            regime_move = (ema_w - ema_prev).abs() / ema_prev
            regime_valid = (ema_prev > 0) & (regime_move >= regime_min_move)
        else:
            regime_valid = pd.Series(True, index=df_m.index)
            
        # 3. Dynamic Pullback Tolerance
        dynamic_tol = np.where((atr.notna()) & (atr > 0) & (close > 0), np.maximum(pullback_tol_param, (atr / close) * 0.5), pullback_tol_param)
        pullback_call = (low <= ema_d * (1 + dynamic_tol)) & (close >= ema_d * (1 - dynamic_tol))
        pullback_put = (high >= ema_d * (1 - dynamic_tol)) & (close <= ema_d * (1 + dynamic_tol))
        
        # 4. Dual RSI Filters
        rsi_call = (rsi_d >= rsi_min_call) & (rsi_d <= rsi_max_call)
        rsi_put = (rsi_d >= rsi_min_put) & (rsi_d <= rsi_max_put)
        if rsi_f.notna().any():
            rsi_call = rsi_call & (rsi_f <= 50.0)
            rsi_put = rsi_put & (rsi_f >= 50.0)
            
        # 5. Volume Filter (Safe 0-Volume Fallback)
        if has_vol and 'vol_sma' in df_m.columns:
            vol_sma = df_m['vol_sma']
            vol_low = (vol_sma == 0) | (df_m['volume'] < vol_sma)
        else:
            vol_low = pd.Series(True, index=df_m.index)
            
        # 6. Candle Wicks & Geometry
        candle_range = high - low
        lower_wick = np.minimum(open_p, close) - low
        upper_wick = high - np.maximum(open_p, close)
        body_ratio = (close - open_p).abs() / np.maximum(candle_range, 1e-8)
        
        valid_range = candle_range > 0
        wick_rejection_call = np.where(valid_range, (lower_wick / candle_range) >= wick_rejection_min, True)
        wick_rejection_put = np.where(valid_range, (upper_wick / candle_range) >= put_wick_min, True)
        body_ok = np.where(valid_range, body_ratio <= 0.45, True)
        dir_close_call = np.where(valid_range, close >= open_p, True)
        dir_close_put = np.where(valid_range, close <= open_p, True)
        
        # 7. Day of Week / Weekend Exclusion
        open_t = df_m['open_time']
        is_ms = open_t.max() > 2**32
        sig_timestamps = np.where(is_ms, open_t // 1000, open_t)
        dt_series = pd.to_datetime(sig_timestamps, unit='s', utc=True)
        day_of_week = pd.Series(dt_series, index=df_m.index).dt.tz_convert('America/New_York').dt.weekday
        
        if self.allowed_days is not None:
            day_valid = day_of_week.isin(self.allowed_days)
        elif self.exclude_weekends:
            day_valid = day_of_week < 5
        else:
            day_valid = pd.Series(True, index=df_m.index)
            
        # Combine Conditions
        is_call = warmup_mask & weekly_bull & regime_valid & pullback_call & rsi_call & vol_low & wick_rejection_call & body_ok & dir_close_call & day_valid
        is_put = warmup_mask & weekly_bear & regime_valid & pullback_put & rsi_put & vol_low & wick_rejection_put & body_ok & dir_close_put & day_valid
        
        if direction_filter == 'CALL':
            is_put = pd.Series(False, index=df_m.index)
        elif direction_filter == 'PUT':
            is_call = pd.Series(False, index=df_m.index)
            
        # Anti-streak edge trigger
        is_call = is_call & (~is_call.shift(1).fillna(False))
        is_put = is_put & (~is_put.shift(1).fillna(False))
        
        conflict = is_call & is_put
        is_call = is_call & (~conflict)
        is_put = is_put & (~conflict)
        
        series_signals = pd.Series(index=orig_indices, dtype=object)
        
        call_orig_indices = df_m.loc[is_call, '_orig_idx_']
        put_orig_indices = df_m.loc[is_put, '_orig_idx_']
        
        series_signals.loc[call_orig_indices] = 'CALL'
        series_signals.loc[put_orig_indices] = 'PUT'
        
        if as_list:
            signals_list = []
            active_rows = df_m[is_call | is_put]
            for _, row in active_rows.iterrows():
                sig_dir = 'CALL' if row['_orig_idx_'] in call_orig_indices.values else 'PUT'
                sig_t = int(row['open_time'] // 1000) if row['open_time'] > 2**32 else int(row['open_time'])
                signals_list.append({
                    'time': sig_t,
                    'direction': sig_dir,
                    'price': float(row['close']),
                    'rsi': float(row['rsi_daily']) if not pd.isna(row['rsi_daily']) else 50.0,
                    'ema_daily': float(row['ema_daily']) if not pd.isna(row['ema_daily']) else 0.0,
                    'ema_weekly': float(row['ema_weekly']) if not pd.isna(row.get('ema_weekly')) else 0.0
                })
            return signals_list
            
        return series_signals

    def generate_signals_list(self, df_daily: pd.DataFrame = None, precomputed: dict = None) -> list[dict]:
        return self.generate_signals(df_daily=df_daily, precomputed=precomputed, as_list=True)
