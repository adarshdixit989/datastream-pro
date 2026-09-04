from collections import defaultdict, deque
import numpy as np
from sklearn.ensemble import IsolationForest
WINDOW_SIZE=200
MIN_SAMPLES_TO_FIT=20
REFIT_EVERY_N=10
CONTAMINATION=0.05
class AnomalyDetector:
    def __init__(self):
        self._buffers=defaultdict(lambda: deque(maxlen=WINDOW_SIZE))
        self._models={}
        self._since_refit=defaultdict(int)
    def _maybe_refit(self,event_type):
        buf=self._buffers[event_type]
        if len(buf)<MIN_SAMPLES_TO_FIT or (event_type in self._models and self._since_refit[event_type]<REFIT_EVERY_N): return
        model=IsolationForest(n_estimators=100,contamination=CONTAMINATION,random_state=42)
        model.fit(np.array(buf).reshape(-1,1))
        self._models[event_type]=model; self._since_refit[event_type]=0
    def score(self,event_type,value):
        model=self._models.get(event_type)
        if model is None and len(self._buffers[event_type])>=MIN_SAMPLES_TO_FIT: self._maybe_refit(event_type); model=self._models.get(event_type)
        result=(False,0.0) if model is None else (model.predict(np.array([[value]]))[0]==-1,float(model.decision_function(np.array([[value]]))[0]))
        self._buffers[event_type].append(value); self._since_refit[event_type]+=1; self._maybe_refit(event_type)
        return result
detector=AnomalyDetector()
