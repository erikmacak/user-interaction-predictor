from typing import Dict

from services.predictor.base import BasePredictor
from services.predictor.v1 import PredictorV1

class PredictorRegistry:
    _predictors: Dict[str, BasePredictor] = {
        "v1": PredictorV1(),
    }

    @classmethod
    def get(cls, version: str) -> BasePredictor:
        try:
            return cls._predictors[version]
        except KeyError:
            raise ValueError(f"Unsupported predictor version: {version}")