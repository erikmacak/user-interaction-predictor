from services.predictor.base import BasePredictor

class PredictorV1(BasePredictor):
    def _predict_from_data(self, data) -> str:
        return "like"