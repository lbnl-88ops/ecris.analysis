from pathlib import Path
import json

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

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