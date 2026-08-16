import pandas as pd
import numpy as np
from .base import BaseStrategy
from engine.indicators import compute_ema, compute_wilders_rsi
from sklearn.ensemble import HistGradientBoostingClassifier

class VolatilitySqueezeMLStrategy(BaseStrategy):
    name = "Volatility Squeeze MTF ML (Walk-Forward Calibrado)"
    description = "Meta-filtro ML con Walk-Forward expandible, features de microestructura y umbral de probabilidad calibrado."

    def get_params_schema(self) -> list[dict]:
        return [
            {"name": "bb_pctl_thresh", "type": "float", "default": 0.35, "min": 0.10, "max": 0.50, "step": 0.05, "description": "Percentil Maximo de Ancho BB"},
            {"name": "prob_thresh", "type": "float", "default": 0.80, "min": 0.50, "max": 0.95, "step": 0.05, "description": "Umbral de Probabilidad ML P(WIN)"},
            {"name": "use_mtf", "type": "bool", "default": True, "description": "Activar Filtro de Tendencia Macro MTF"},
        ]

    def prepare_data(self, df: pd.DataFrame) -> dict:
        if df is None or len(df) < 200:
            return {}
            
        close = df['close']
        open_p = df['open']
        high = df['high']
        low = df['low']
        volume = df['volume'] if 'volume' in df.columns else pd.Series(1.0, index=df.index)
        
        candle_range = (high - low).replace(0, 1e-8)
        
        # Candle geometry
        wick_upper = (high - np.maximum(open_p, close)) / candle_range
        wick_lower = (np.minimum(open_p, close) - low) / candle_range
        body_ratio = (close - open_p).abs() / candle_range
        
        # True Range & ATR
        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr_14 = tr.rolling(14).mean().replace(0, 1e-8)
        
        # Bollinger Bands
        bb_sma20 = close.rolling(20).mean()
        bb_std20 = close.rolling(20).std(ddof=0)
        bb_upper = bb_sma20 + 2.0 * bb_std20
        bb_lower = bb_sma20 - 2.0 * bb_std20
        bb_w = (4.0 * bb_std20) / bb_sma20.replace(0, 1e-8)
        
        w_min = bb_w.rolling(100).min()
        w_max = bb_w.rolling(100).max()
        bb_pctl = (bb_w - w_min) / (w_max - w_min + 1e-8)
        
        # BB Position (where in the band 0=lower, 1=upper)
        bb_pos = (close - bb_lower) / (bb_upper - bb_lower + 1e-8)
        
        # EMAs MTF
        ema_20 = compute_ema(close, 20)
        ema_50 = compute_ema(close, 50)
        ema_200 = compute_ema(close, 200)
        
        # Momentum & Oscillators
        rsi_7 = compute_wilders_rsi(close, 7)
        rsi_14 = compute_wilders_rsi(close, 14)
        
        # Volume
        vol_sma20 = volume.rolling(20).mean().replace(0, 1e-8)
        rel_vol = volume / vol_sma20
        vol_delta = volume / volume.shift(1).replace(0, 1e-8)
        
        # Returns at multiple lags
        ret_1 = close.pct_change(1).fillna(0)
        ret_3 = close.pct_change(3).fillna(0)
        ret_5 = close.pct_change(5).fillna(0)
        ret_10 = close.pct_change(10).fillna(0)
        
        # ATR change (volatility expansion/contraction)
        atr_change = (atr_14 / atr_14.shift(5).replace(0, 1e-8)) - 1.0
        
        # EMA slope (trend strength)
        ema_slope = (ema_20 - ema_20.shift(5)) / atr_14
        
        # Rolling return 10 candles (fast replacement for consec_dir)
        ret_10 = close.pct_change(10).fillna(0)
        
        # 19 features total (all vectorized, no Python loops)
        features = pd.DataFrame({
            'wick_upper': wick_upper,
            'wick_lower': wick_lower,
            'body_ratio': body_ratio,
            'natr_14': atr_14 / close.replace(0, 1e-8),
            'bb_width': bb_w,
            'bb_pctl': bb_pctl.fillna(0.5),
            'bb_pos': bb_pos.fillna(0.5),
            'dist_ema20': (close - ema_20) / atr_14,
            'dist_ema50': (close - ema_50) / atr_14,
            'dist_ema200': (close - ema_200) / atr_14,
            'rsi_7': rsi_7,
            'rsi_14': rsi_14,
            'rel_vol': rel_vol,
            'vol_delta': vol_delta.fillna(1.0),
            'ret_1': ret_1,
            'ret_3': ret_3,
            'ret_5': ret_5,
            'ret_10': ret_10,
            'atr_change': atr_change.fillna(0),
        }, index=df.index).fillna(0.0)
        
        # Clip extremes using backward rolling window statistics to prevent lookahead bias
        for col in features.columns:
            q01 = features[col].rolling(200, min_periods=20).quantile(0.01).fillna(features[col])
            q99 = features[col].rolling(200, min_periods=20).quantile(0.99).fillna(features[col])
            features[col] = features[col].clip(q01, q99)
        
        return {
            'close': close,
            'open': open_p,
            'high': high,
            'low': low,
            'volume': volume,
            'bb_upper': bb_upper,
            'bb_lower': bb_lower,
            'bb_pctl': bb_pctl,
            'ema_20': ema_20,
            'ema_50': ema_50,
            'ema_200': ema_200,
            'rsi_7': rsi_7,
            'atr_14': atr_14,
            'features': features
        }

    def generate_signals(self, df: pd.DataFrame = None, params: dict = None, precomputed: dict = None, **kwargs) -> pd.Series:
        p = params or {}
        bb_pctl_thresh = float(p.get("bb_pctl_thresh", 0.35))
        prob_thresh = float(p.get("prob_thresh", 0.80))
        use_mtf = bool(p.get("use_mtf", True))
        
        if precomputed is None or 'features' not in precomputed:
            if df is None or len(df) < 200:
                return pd.Series(dtype=object)
            precomputed = self.prepare_data(df)
            
        close = precomputed['close']
        open_p = precomputed['open']
        high = precomputed['high']
        low = precomputed['low']
        ema_20 = precomputed['ema_20']
        ema_50 = precomputed['ema_50']
        ema_200 = precomputed['ema_200']
        rsi_7 = precomputed['rsi_7']
        atr_14 = precomputed['atr_14']
        
        candle_range = (high - low).replace(0, 1e-8)
        lower_wick = (np.minimum(open_p, close) - low) / candle_range
        upper_wick = (high - np.maximum(open_p, close)) / candle_range
        dist_ema20 = (close - ema_20).abs() / atr_14
        
        mtf_bull = (ema_20 > ema_50) & (ema_50 > ema_200) if use_mtf else pd.Series(True, index=close.index)
        mtf_bear = (ema_20 < ema_50) & (ema_50 < ema_200) if use_mtf else pd.Series(True, index=close.index)
        
        signals = pd.Series(index=close.index, data=None, dtype=object)
        
        # Relaxed base signals to generate MORE candidates for ML to filter
        call_cond = mtf_bull & (dist_ema20 <= 2.0) & (close > open_p) & (lower_wick >= 0.20) & (rsi_7 >= 30) & (rsi_7 <= 75)
        put_cond = mtf_bear & (dist_ema20 <= 2.0) & (close < open_p) & (upper_wick >= 0.20) & (rsi_7 <= 70) & (rsi_7 >= 25)
        
        signals.loc[call_cond] = 'CALL'
        signals.loc[put_cond] = 'PUT'
        
        # =====================================================================
        # EXPANDING WALK-FORWARD ML META-FILTER
        # Train on ALL past data, predict ONLY the next fold (never the same data)
        # =====================================================================
        active_indices = signals.dropna().index
        if len(active_indices) < 50:
            return signals
        
        features = precomputed['features']
        n_active = len(active_indices)
        
        # Build outcome labels for ALL signals
        locs = df.index.get_indexer(active_indices)
        n_df = len(df)
        valid_mask = (locs + 1) < n_df
        
        entry_prices = np.full(n_active, np.nan)
        exit_prices = np.full(n_active, np.nan)
        locs_valid = locs[valid_mask]
        entry_prices[valid_mask] = df['open'].values[np.minimum(locs_valid + 1, n_df - 1)]
        exit_prices[valid_mask] = df['close'].values[locs_valid + 1]
        
        dirs = signals.loc[active_indices].values
        diffs = exit_prices - entry_prices
        y_all = np.full(n_active, np.nan)
        y_all[valid_mask] = np.where(
            dirs[valid_mask] == 'CALL',
            diffs[valid_mask] > 1e-8,
            diffs[valid_mask] < -1e-8
        ).astype(float)
        
        X_all = features.loc[active_indices].values
        X_all = np.nan_to_num(X_all, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Expanding walk-forward: divide into K chronological folds
        min_train_size = 40  # minimum signals to train on
        fold_size = max(20, n_active // 8)  # ~8 folds
        n_folds = max(2, (n_active - min_train_size) // fold_size + 1)
        
        oos_probs = np.full(n_active, np.nan)
        
        for fold_idx in range(1, n_folds + 1):
            # Training: all signals up to this fold
            train_end = min(min_train_size + (fold_idx - 1) * fold_size, n_active)
            # Test: next fold_size signals
            test_start = train_end
            test_end = min(train_end + fold_size, n_active)
            
            if test_start >= n_active:
                break
            
            # Training mask: valid labels only
            train_indices = np.arange(0, train_end)
            train_valid = valid_mask[train_indices] & ~np.isnan(y_all[train_indices])
            
            if train_valid.sum() < 30:
                continue
            
            X_train = X_all[train_indices[train_valid]]
            y_train = y_all[train_indices[train_valid]].astype(int)
            
            if len(np.unique(y_train)) < 2:
                continue
            
            # Heavily regularized model to prevent overfitting
            clf = HistGradientBoostingClassifier(
                max_iter=200,
                max_depth=3,
                learning_rate=0.03,
                min_samples_leaf=20,
                l2_regularization=5.0,
                max_bins=64,
                random_state=42
            )
            clf.fit(X_train, y_train)
            
            # Predict ONLY on OOS fold (never seen during training)
            test_indices = np.arange(test_start, test_end)
            if len(test_indices) == 0:
                continue
            X_test = X_all[test_indices]
            probs = clf.predict_proba(X_test)[:, 1]
            oos_probs[test_indices] = probs
        
        # =====================================================================
        # FILTER: Only keep signals where OOS probability >= threshold
        # =====================================================================
        filtered = pd.Series(index=close.index, data=None, dtype=object)
        
        for i, idx in enumerate(active_indices):
            if not np.isnan(oos_probs[i]) and oos_probs[i] >= prob_thresh:
                filtered.loc[idx] = signals.loc[idx]
        
        return filtered
