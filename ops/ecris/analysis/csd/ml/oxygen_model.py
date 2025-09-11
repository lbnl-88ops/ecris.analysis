from pathlib import Path
from logging import getLogger
import json
from typing import Optional, List, Tuple

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from scipy.signal import find_peaks

from ops.ecris.analysis.model import CSD
from ops.ecris.analysis.csd import ElementPeaks, Peak
from .helpers import sorted_permutations

_log = getLogger(__name__)

def train_oxygen_model(model_parameters_path: Path, 
                       X_path: Path, 
                       y_path: Path) -> Pipeline:
    with open(model_parameters_path) as f:
        model_params = json.load(f)
    mlp_params = {k.replace('mlp__', ''): v for k, v in model_params.items()
              if k.startswith('mlp__')}
    X = np.load(X_path)
    y = np.load(y_path)
    pipeline = Pipeline([('scaler', StandardScaler()), 
                         ('mlp', MLPClassifier(random_state=42,
                          max_iter=500,
                          early_stopping=True,
                          **mlp_params))])
    pipeline.fit(X, y)
    return pipeline

def find_oxygen_peaks(csd: CSD, model: Pipeline, 
                      n_peaks: List[int] | int = 10,
                      *, 
                      prominance=0.1, 
                      minimum_height = 1,
                      **kwargs) -> Tuple[ElementPeaks, float]:
    if csd.m_over_q is None:
        raise RuntimeError('CSD m_over_q must be set')
    if isinstance(n_peaks, int):
        n_peaks = [n_peaks]
    expected_m_over_q = [16/float(q) for q in range(1, 9)]
    all_peaks, properties = find_peaks(csd.beam_current, 
                                       prominence=prominance, 
                                       height=(minimum_height, None), 
                                       **kwargs)
    sorted_peaks = np.flip(np.argsort(properties['prominences']))
    probability = 0
    for n in n_peaks:
        highest_peaks = sorted(all_peaks[sorted_peaks][:n])
        sorted_peaks = sorted_permutations([int(v) for v in highest_peaks])
        probabilities = model.predict_proba(sorted_peaks)[:, 1] 
        highest_prob = np.flip(np.argsort(probabilities))[0]

        probability = float(probabilities[highest_prob])
        peak_idxs = sorted_peaks[highest_prob]
        peaks = []
        if probability > 0.5:
            for idx in peak_idxs:
                m_over_q = expected_m_over_q[np.argmin([abs(moq - csd.m_over_q[idx]) 
                                                        for moq in expected_m_over_q])]
                peaks.append(Peak(m_over_q, float(csd.beam_current[idx]), index=idx))
            return ElementPeaks(peaks), probability
    raise RuntimeError(f'Oxygen peaks not found, max probability {probability}')

