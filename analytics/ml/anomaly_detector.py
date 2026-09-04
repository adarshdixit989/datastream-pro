from collections import defaultdict, deque

import numpy as np
from sklearn.ensemble import IsolationForest

WINDOW_SIZE = 200
MIN_SAMPLES_TO_FIT = 20
REFIT_EVERY_N = 10
CONTAMINATION = 0.05
MIN_ABS_DEVIATION = 6.0


class AnomalyDetector:
    def __init__(self):
        self._buffers = defaultdict(lambda: deque(maxlen=WINDOW_SIZE))
        self._models = {}
        self._since_refit = defaultdict(int)

    def _maybe_refit(self, event_type):
        buf = self._buffers[event_type]
        if len(buf) < MIN_SAMPLES_TO_FIT:
            return
        if event_type in self._models and self._since_refit[event_type] < REFIT_EVERY_N:
            return
        model = IsolationForest(
            n_estimators=100,
            contamination=CONTAMINATION,
            random_state=42,
        )
        model.fit(np.array(buf).reshape(-1, 1))
        self._models[event_type] = model
        self._since_refit[event_type] = 0

    def score(self, event_type, value):
        model = self._models.get(event_type)
        buf = self._buffers[event_type]

        if model is None and len(buf) >= MIN_SAMPLES_TO_FIT:
            self._maybe_refit(event_type)
            model = self._models.get(event_type)

        if model is None:
            result = (False, 0.0)
        else:
            sample = np.array([[value]])
            prediction = model.predict(sample)[0]
            decision_score = float(model.decision_function(sample)[0])

            # IsolationForest can be indecisive for a zero-variance history.
            # Use a deterministic deviation guard for that degenerate case.
            history = np.asarray(buf, dtype=float)
            spread = float(np.std(history))
            baseline = float(np.median(history))
            degenerate_outlier = spread == 0.0 and abs(value - baseline) >= MIN_ABS_DEVIATION
            result = (prediction == -1 or degenerate_outlier, decision_score)

        buf.append(value)
        self._since_refit[event_type] += 1
        self._maybe_refit(event_type)
        return result


detector = AnomalyDetector()
