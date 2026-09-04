from django.test import TestCase
from analytics.ml.anomaly_detector import AnomalyDetector
from analytics.ml.forecaster import Forecaster

class AnomalyDetectorTests(TestCase):
    def test_flags_extreme_outlier(self):
        detector = AnomalyDetector()
        for _ in range(30):
            detector.score("test_metric", 10.0)
        is_anomaly, score = detector.score("test_metric", 10000.0)
        self.assertTrue(is_anomaly)

    def test_no_anomaly_before_enough_history(self):
        detector = AnomalyDetector()
        is_anomaly, score = detector.score("brand_new_metric", 5.0)
        self.assertFalse(is_anomaly)
        self.assertEqual(score, 0.0)

class ForecasterTests(TestCase):
    def test_returns_none_before_min_samples(self):
        forecaster = Forecaster()
        for _ in range(3):
            result = forecaster.add_and_forecast("metric", 5.0)
        self.assertIsNone(result)

    def test_forecasts_trend(self):
        forecaster = Forecaster()
        result = None
        for i in range(10):
            result = forecaster.add_and_forecast("metric", float(i))
        self.assertIsNotNone(result)
        self.assertGreater(result, 8.0)
