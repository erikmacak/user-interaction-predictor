from services.predictor.v1 import PredictorV1
from domain.action import PredictedActionType

def test_skip_is_always_last():
    predictor = PredictorV1()

    actions = [
        PredictedActionType.LIKE,
        PredictedActionType.SKIP,
        PredictedActionType.FINISH_WATCHING,
    ]

    ordered = predictor._order_actions(actions)

    assert ordered[-1] == PredictedActionType.SKIP