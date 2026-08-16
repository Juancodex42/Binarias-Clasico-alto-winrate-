"""
Optuna Framework Integration Engine for Binary Options Strategy Hyperparameter Optimization.
Module: engine/optimizer_optuna.py (Proposed Implementation Blueprint)
Feature 12 & Feature 13 - Milestone 3
"""

import math
import logging
import numpy as np
import pandas as pd
import optuna
from optuna.samplers import TPESampler
from optuna.pruners import MedianPruner, HyperbandPruner
from typing import Dict, Any, Type, Optional, Callable

from engine.simulator import BinarySimulator
from engine.ml_engine.purged_cv import PurgedGroupTimeSeriesSplit
from engine.ml_engine.meta_labeler import MetaLabeler
from engine.ml_engine.regime_detector import RegimeDetector
from strategies.base import BaseStrategy

logger = logging.getLogger(__name__)

# Suppress verbose Optuna logging during search runs unless configured
optuna.logging.set_verbosity(optuna.logging.WARNING)


def calculate_wilson_lower_bound(k: int, n: int, confidence: float = 0.95) -> float:
    """
    Calculates the lower bound of the Wilson score confidence interval for a Bernoulli win rate.
    """
    if n <= 0:
        return 0.0
    z = 1.96  # 95% confidence level
    p = k / n
    denom = 1.0 + (z**2) / n
    center = (p + (z**2) / (2 * n)) / denom
    margin = (z * np.sqrt((p * (1.0 - p) / n) + (z**2) / (4 * (n**2)))) / denom
    return float(max(0.0, center - margin))


class OptunaSearchSpace:
    """
    Standardized multi-dimensional search space definitions for Optuna trial parameter sampling.
    """

    @staticmethod
    def sample_common_dimensions(trial: optuna.Trial) -> Dict[str, Any]:
        """
        Samples core execution and session dimensions.
        """
        return {
            "expiry_candles": trial.suggest_int("expiry_candles", 1, 12),
            "session_filter": trial.suggest_categorical(
                "session_filter",
                ["ALL", "ASIAN", "LONDON", "NEW_YORK", "OVERLAP_LDN_NY"]
            ),
            "exclude_weekends": trial.suggest_categorical("exclude_weekends", [True, False]),
            "meta_threshold": trial.suggest_float("meta_threshold", 0.50, 0.90, step=0.05),
            "regime_breakeven": trial.suggest_float("regime_breakeven", 0.45, 0.60, step=0.01),
        }

    @staticmethod
    def sample_strategy_space(strategy_name: str, trial: optuna.Trial) -> Dict[str, Any]:
        """
        Samples strategy-specific technical parameters based on strategy name.
        """
        params = OptunaSearchSpace.sample_common_dimensions(trial)

        if strategy_name == "volatility_squeeze_ml":
            params.update({
                "bb_pctl_thresh": trial.suggest_float("bb_pctl_thresh", 0.10, 0.50, step=0.05),
                "prob_thresh": trial.suggest_float("prob_thresh", 0.50, 0.95, step=0.05),
                "use_mtf": trial.suggest_categorical("use_mtf", [True, False]),
                "rsi_period": trial.suggest_int("rsi_period", 5, 30),
                "natr_period": trial.suggest_int("natr_period", 7, 28),
            })
        elif strategy_name == "bollinger_bounce":
            params.update({
                "bb_period": trial.suggest_int("bb_period", 10, 50),
                "bb_std": trial.suggest_float("bb_std", 1.5, 3.5, step=0.1),
                "wick_ratio": trial.suggest_float("wick_ratio", 0.10, 0.60, step=0.05),
                "vol_mult": trial.suggest_float("vol_mult", 0.5, 2.5, step=0.1),
            })
        elif strategy_name == "rsi_extremes":
            params.update({
                "rsi_period": trial.suggest_int("rsi_period", 2, 30),
                "oversold": trial.suggest_float("oversold", 15.0, 35.0, step=1.0),
                "overbought": trial.suggest_float("overbought", 65.0, 85.0, step=1.0),
                "wick_ratio": trial.suggest_float("wick_ratio", 0.10, 0.60, step=0.05),
                "vol_mult": trial.suggest_float("vol_mult", 0.5, 2.5, step=0.1),
            })
        elif strategy_name == "daily_confluence":
            params.update({
                "ema_weekly_period": trial.suggest_int("ema_weekly_period", 5, 100),
                "ema_daily_period": trial.suggest_int("ema_daily_period", 5, 100),
                "rsi_period": trial.suggest_int("rsi_period", 2, 30),
                "pullback_tolerance": trial.suggest_float("pullback_tolerance", 0.001, 0.05, step=0.002),
                "rsi_min_call": trial.suggest_float("rsi_min_call", 10.0, 50.0, step=2.5),
                "rsi_max_call": trial.suggest_float("rsi_max_call", 30.0, 70.0, step=2.5),
                "rsi_min_put": trial.suggest_float("rsi_min_put", 30.0, 70.0, step=2.5),
                "rsi_max_put": trial.suggest_float("rsi_max_put", 50.0, 90.0, step=2.5),
                "wick_rejection_ratio": trial.suggest_float("wick_rejection_ratio", 0.10, 0.80, step=0.05),
            })
        else:
            # Fallback generic parameter space
            params.update({
                "rsi_period": trial.suggest_int("rsi_period", 7, 21),
                "wick_ratio": trial.suggest_float("wick_ratio", 0.20, 0.50, step=0.05),
            })

        return params


class OptunaOptimizer:
    """
    Optuna Bayesian Hyperparameter Optimization Framework for Quantitative Binary Options Strategies.
    Integrates TPE Sampler, Purged Cross-Validation, Trial Pruning, and multi-metric validation.
    """

    def __init__(
        self,
        payout: float = 0.85,
        target_win_rate: float = 0.65,
        min_trades: int = 30,
        n_splits: int = 5,
        embargo_pct: float = 0.01
    ):
        self.payout = payout
        self.target_win_rate = target_win_rate
        self.min_trades = min_trades
        self.n_splits = n_splits
        self.embargo_pct = embargo_pct
        self.simulator = BinarySimulator()

    def _apply_session_filter(self, df: pd.DataFrame, signals: pd.Series, session: str) -> pd.Series:
        """Applies UTC session hours filter to base signals."""
        if session == "ALL" or signals is None or signals.dropna().empty:
            return signals

        if 'open_time' in df.columns:
            is_ms = df['open_time'].max() > 2**32
            ts_sec = df['open_time'] // 1000 if is_ms else df['open_time']
            dt = pd.to_datetime(ts_sec, unit='s', utc=True)
            hours = dt.dt.hour
        else:
            hours = df.index.hour

        filtered = signals.copy()
        if session == "ASIAN":
            mask = (hours >= 0) & (hours < 8)
        elif session == "LONDON":
            mask = (hours >= 8) & (hours < 16)
        elif session == "NEW_YORK":
            mask = (hours >= 13) & (hours < 21)
        elif session == "OVERLAP_LDN_NY":
            mask = (hours >= 13) & (hours < 16)
        else:
            mask = pd.Series(True, index=signals.index)

        filtered[~mask] = None
        return filtered

    def _evaluate_trial_purged_cv(
        self,
        trial: optuna.Trial,
        df: pd.DataFrame,
        strategy_cls: Type[BaseStrategy],
        params: Dict[str, Any]
    ) -> float:
        """
        Evaluates a parameter configuration across Purged Group TimeSeries Cross-Validation folds.
        Reports fold performance to Optuna pruner for early trial termination.
        """
        expiry = params.get("expiry_candles", 1)
        meta_thresh = params.get("meta_threshold", 0.65)
        regime_be = params.get("regime_breakeven", 0.50)
        session = params.get("session_filter", "ALL")

        strat_instance = strategy_cls()
        precomputed = strat_instance.prepare_data(df)
        base_signals = strat_instance.generate_signals(df, params, precomputed=precomputed)

        if base_signals is None or base_signals.dropna().empty:
            return -999.0

        # Session filtering
        signals = self._apply_session_filter(df, base_signals, session)
        if signals.dropna().empty:
            return -999.0

        purged_cv = PurgedGroupTimeSeriesSplit(
            n_splits=self.n_splits,
            expiry_candles=expiry,
            embargo_pct=self.embargo_pct
        )

        fold_oos_winrates = []
        fold_oos_evs = []
        fold_oos_trades = []

        for fold_idx, (train_idx, test_idx) in enumerate(purged_cv.split(df)):
            df_train = df.iloc[train_idx]
            df_test = df.iloc[test_idx].reset_index(drop=True)
            sig_train = signals.iloc[train_idx]
            sig_test = signals.iloc[test_idx].reset_index(drop=True)

            # Check minimum signals in train fold
            if len(sig_train.dropna()) < 10:
                continue

            # MetaLabeler Fit on IS
            meta = MetaLabeler(threshold=meta_thresh)
            entry_prices = df_train['open'].shift(-1)
            exit_prices = df_train['close'].shift(-(1 + expiry))
            labels = pd.Series(index=sig_train.index, dtype=float)
            calls = sig_train == 'CALL'
            puts = sig_train == 'PUT'
            labels[calls & (exit_prices > entry_prices)] = 1.0
            labels[calls & (exit_prices <= entry_prices)] = 0.0
            labels[puts & (exit_prices < entry_prices)] = 1.0
            labels[puts & (exit_prices >= entry_prices)] = 0.0
            labels = labels.dropna()

            if len(labels) >= 10:
                meta.fit(df_train, sig_train, labels)
                filt_test = meta.filter(df_test, sig_test) if meta.is_fitted else sig_test
            else:
                filt_test = sig_test

            # Simulate OOS fold
            sim_res = self.simulator.run(df_test, filt_test, expiry_candles=expiry, payout=self.payout)
            summary = sim_res.get("summary", {})
            n_tr = summary.get("total_trades", 0)
            wr = summary.get("win_rate_effective", 0.0)
            ev = summary.get("expected_value_per_trade", -1.0)

            fold_oos_winrates.append(wr)
            fold_oos_evs.append(ev)
            fold_oos_trades.append(n_tr)

            # Intermediate reporting for Optuna MedianPruner
            intermediate_score = np.mean(fold_oos_winrates) if fold_oos_winrates else 0.0
            trial.report(intermediate_score, step=fold_idx)

            # Check if trial should be pruned early
            if trial.should_prune():
                raise optuna.TrialPruned()

        total_oos_trades = sum(fold_oos_trades)
        if total_oos_trades < self.min_trades:
            return -999.0

        mean_wr = float(np.mean(fold_oos_winrates))
        mean_ev = float(np.mean(fold_oos_evs))
        breakeven_wr = 1.0 / (1.0 + self.payout)  # 54.05% for 0.85 payout

        if mean_wr < breakeven_wr or mean_ev <= 0.0:
            return -100.0 + (mean_wr * 100.0)

        # Composite optimization score: OOS EV * log(1 + trades) * WR bonus
        score = mean_ev * np.log1p(total_oos_trades) * (mean_wr / breakeven_wr)
        if mean_wr >= self.target_win_rate:
            score *= 1.5  # Bonus multiplier for passing 65% OOS WR target

        return float(score)

    def optimize(
        self,
        df: pd.DataFrame,
        strategy_cls: Type[BaseStrategy],
        strategy_name: str,
        n_trials: int = 100,
        timeout: Optional[int] = 300,
        storage: Optional[str] = None,
        study_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes Optuna study optimization using TPE Sampler and Median Pruner.
        Returns best hyperparameter set and comprehensive evaluation metadata.
        """
        sampler = TPESampler(seed=42, multivariate=True, group=True)
        pruner = MedianPruner(n_startup_trials=10, n_warmup_steps=1)

        study = optuna.create_study(
            study_name=study_name or f"optuna_{strategy_name}",
            storage=storage,
            direction="maximize",
            sampler=sampler,
            pruner=pruner,
            load_if_exists=True
        )

        def objective(trial: optuna.Trial) -> float:
            params = OptunaSearchSpace.sample_strategy_space(strategy_name, trial)
            return self._evaluate_trial_purged_cv(trial, df, strategy_cls, params)

        study.optimize(objective, n_trials=n_trials, timeout=timeout)

        best_params = study.best_params
        best_value = study.best_value
        trials_df = study.trials_dataframe()

        # Parameter importance estimation
        try:
            importances = optuna.importance.get_param_importances(study)
        except Exception:
            importances = {}

        # OOS Final Verification of Best Parameters
        final_eval = self._verify_best_params(df, strategy_cls, best_params)

        return {
            "best_params": best_params,
            "best_value": best_value,
            "param_importances": importances,
            "total_trials": len(study.trials),
            "completed_trials": len([t for t in study.trials if t.state == optuna.trial.TrialState.COMPLETE]),
            "pruned_trials": len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED]),
            "trials_df": trials_df,
            "oos_verification": final_eval
        }

    def _verify_best_params(
        self,
        df: pd.DataFrame,
        strategy_cls: Type[BaseStrategy],
        best_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Runs a final strict 60/40 Train/Test verification of the best parameter configuration.
        """
        split_idx = int(len(df) * 0.60)
        df_train = df.iloc[:split_idx]
        df_test = df.iloc[split_idx:].reset_index(drop=True)

        expiry = best_params.get("expiry_candles", 1)
        meta_thresh = best_params.get("meta_threshold", 0.65)
        session = best_params.get("session_filter", "ALL")

        strat = strategy_cls()
        pre_test = strat.prepare_data(df_test)
        sigs_test = strat.generate_signals(df_test, best_params, precomputed=pre_test)
        sigs_test = self._apply_session_filter(df_test, sigs_test, session)

        pre_train = strat.prepare_data(df_train)
        sigs_train = strat.generate_signals(df_train, best_params, precomputed=pre_train)

        # MetaLabeler calibration on Train
        meta = MetaLabeler(threshold=meta_thresh)
        entry_prices = df_train['open'].shift(-1)
        exit_prices = df_train['close'].shift(-(1 + expiry))
        labels = pd.Series(index=sigs_train.index, dtype=float)
        calls = sigs_train == 'CALL'
        puts = sigs_train == 'PUT'
        labels[calls & (exit_prices > entry_prices)] = 1.0
        labels[calls & (exit_prices <= entry_prices)] = 0.0
        labels[puts & (exit_prices < entry_prices)] = 1.0
        labels[puts & (exit_prices >= entry_prices)] = 0.0
        labels = labels.dropna()

        if len(labels) >= 10:
            meta.fit(df_train, sigs_train, labels)
            filt_test = meta.filter(df_test, sigs_test) if meta.is_fitted else sigs_test
        else:
            filt_test = sigs_test

        sim_res = self.simulator.run(df_test, filt_test, expiry_candles=expiry, payout=self.payout)
        s = sim_res.get("summary", {})

        n_trades = s.get("total_trades", 0)
        wins = s.get("wins", 0)
        win_rate = s.get("win_rate_effective", 0.0)
        ev = s.get("expected_value_per_trade", 0.0)
        max_dd = s.get("max_drawdown", 0.0)

        wilson_low = calculate_wilson_lower_bound(wins, n_trades)
        passes_target = (win_rate >= self.target_win_rate) and (ev > 0.0) and (n_trades >= self.min_trades)

        return {
            "total_trades": n_trades,
            "wins": wins,
            "win_rate_oos": win_rate,
            "wilson_ci_lower_95": wilson_low,
            "ev_per_trade_oos": ev,
            "max_drawdown_oos": max_dd,
            "passes_target_criteria": passes_target
        }
