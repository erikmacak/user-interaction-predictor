from services.predictor.base import BasePredictor
from services.predictor.v1 import PredictorV1
from services.predictor.v2 import PredictorV2
from domain.errors import UnsupportedPredictorVersionError

class PredictorRegistry:
    _predictors: dict[str, BasePredictor] = {
        "v1": PredictorV1(),
        "v2": PredictorV2(),
    }
    
    @classmethod
    def get(cls, version: str) -> BasePredictor:
        predictor = cls._predictors.get(version)
        
        if predictor is None:
            raise UnsupportedPredictorVersionError(
                version=version,
                supported_versions=list(cls._predictors.keys()),
            )
        
        return predictor
    
    @classmethod
    def get_supported_versions(cls) -> list[str]:
        return list(cls._predictors.keys())