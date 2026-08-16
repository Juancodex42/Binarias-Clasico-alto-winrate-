import numpy as np
import pandas as pd

class PurgedGroupTimeSeriesSplit:
    """
    Purged & Embargoed Group TimeSeries Cross-Validator para Opciones Binarias (Metodología Marcos López de Prado).
    Previene la fuga de datos (Data Leakage) entre la ventana de expiración del trade de entrenamiento y la ventana de prueba.
    """
    def __init__(self, n_splits: int = 5, expiry_candles: int = 1, embargo_pct: float = 0.01):
        self.n_splits = n_splits
        self.expiry_candles = expiry_candles
        self.embargo_pct = embargo_pct

    @staticmethod
    def purge_embargo_split(n_samples: int, train_ratio: float = 0.60, expiry_candles: int = 1, embargo_pct: float = 0.01):
        """
        Retorna (is_end_idx, oos_start_idx) con purga de expiración y embargo temporal.
        - IS finaliza en max(0, raw_split - expiry_candles)
        - OOS inicia en min(n_samples, raw_split + embargo_offset)
        """
        raw_split = int(n_samples * train_ratio)
        embargo_offset = max(1, int(n_samples * embargo_pct))
        
        is_end = max(0, raw_split - expiry_candles)
        oos_start = min(n_samples, raw_split + embargo_offset)
        
        return is_end, oos_start

    def get_n_splits(self, X=None, y=None, groups=None):
        return self.n_splits

    def split(self, X, y=None, groups=None):
        n_samples = len(X)
        indices = np.arange(n_samples)
        embargo_offset = int(n_samples * self.embargo_pct)
        test_size = n_samples // self.n_splits

        for i in range(self.n_splits):
            test_start = i * test_size
            test_end = (i + 1) * test_size if i < self.n_splits - 1 else n_samples
            
            # Máscara inicial: todo en train excepto la ventana de test
            train_mask = np.ones(n_samples, dtype=bool)
            train_mask[test_start:test_end] = False

            # Purga previa al test start: si un trade de train vence dentro del conjunto test
            purge_start = max(0, test_start - self.expiry_candles)
            train_mask[purge_start:test_start] = False

            # Embargo posterior al test end: prevenir autocorrelación serial
            embargo_end = min(n_samples, test_end + max(embargo_offset, self.expiry_candles))
            train_mask[test_end:embargo_end] = False

            train_indices = indices[train_mask]
            test_indices = indices[test_start:test_end]
            
            yield train_indices, test_indices
