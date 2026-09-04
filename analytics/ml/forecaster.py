from collections import defaultdict, deque
import numpy as np
from sklearn.linear_model import LinearRegression
WINDOW_SIZE=50
MIN_SAMPLES_TO_FORECAST=5
class Forecaster:
    def __init__(self):
        self._buffers=defaultdict(lambda: deque(maxlen=WINDOW_SIZE))
    def add_and_forecast(self,event_type,value):
        buf=self._buffers[event_type]; buf.append(value)
        if len(buf)<MIN_SAMPLES_TO_FORECAST: return None
        y=np.array(buf); X=np.arange(len(y)).reshape(-1,1)
        model=LinearRegression().fit(X,y)
        return float(model.predict(np.array([[len(y)]]))[0])
    def sample_count(self,event_type): return len(self._buffers[event_type])
forecaster=Forecaster()
