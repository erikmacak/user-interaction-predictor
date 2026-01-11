from typing import List

from domain.action import PredictedActionType
from services.predictor.base import BasePredictor

class PredictorV1(BasePredictor):
    def _predict_from_data(self, data) -> List[PredictedActionType]:
        return [
            PredictedActionType.LIKE,
        ]