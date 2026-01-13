import random

from services.predictor.v1 import PredictorV1
from domain.action import PredictedActionType

def test_engagement_actions_can_be_anywhere():
    random.seed(42)

    predictor = PredictorV1()

    actions = [
        PredictedActionType.LIKE,
        PredictedActionType.SAVE,
        PredictedActionType.FINISH_WATCHING,
        PredictedActionType.REWATCH,
    ]

    ordered = predictor._order_actions(actions)

    finish_index = ordered.index(PredictedActionType.FINISH_WATCHING)
    rewatch_index = ordered.index(PredictedActionType.REWATCH)

    assert finish_index < rewatch_index
    assert set(actions) == set(ordered)