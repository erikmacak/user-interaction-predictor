from typing import Dict

from services.predictor.base import BasePredictor
from services.predictor.v1 import PredictorV1
from services.predictor.v2 import PredictorV2
from domain.errors import UnsupportedPredictorVersionError

class PredictorRegistry:
    _predictors: Dict[str, BasePredictor] = {
        "v1": PredictorV1(),
        "v2": PredictorV2(),
    }

    @classmethod
    def get(cls, version: str) -> BasePredictor:
        if version not in cls._predictors:
            raise UnsupportedPredictorVersionError(
                version=version,
                supported_versions=list(cls._predictors.keys()),
            )

        return cls._predictors[version]