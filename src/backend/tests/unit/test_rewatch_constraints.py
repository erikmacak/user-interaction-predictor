from services.predictor.v1 import PredictorV1
from domain.action import PredictedActionType

def test_rewatch_without_finish_is_removed():
    predictor = PredictorV1()

    actions = [
        PredictedActionType.REWATCH,
        PredictedActionType.LIKE,
    ]

    ordered = predictor._order_actions(actions)

    assert PredictedActionType.REWATCH not in ordered