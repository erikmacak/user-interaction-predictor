import random
from services.predictor.v1 import PredictorV1
from domain.action import PredictedActionType

class TestPredictorV1:
    def test_engagement_actions_can_be_anywhere(self):
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
    
    def test_rewatch_without_finish_is_removed(self):
        predictor = PredictorV1()
        
        actions = [
            PredictedActionType.REWATCH,
            PredictedActionType.LIKE,
        ]
        
        ordered = predictor._order_actions(actions)
        
        assert PredictedActionType.REWATCH not in ordered
    
    def test_skip_is_always_last(self):
        predictor = PredictorV1()
        
        actions = [
            PredictedActionType.LIKE,
            PredictedActionType.SKIP,
            PredictedActionType.FINISH_WATCHING,
        ]
        
        ordered = predictor._order_actions(actions)
        
        assert ordered[-1] == PredictedActionType.SKIP
    
    def test_continue_watching_before_skip(self):
        predictor = PredictorV1()
        
        actions = [
            PredictedActionType.CONTINUE_WATCHING,
            PredictedActionType.SKIP,
        ]
        
        ordered = predictor._order_actions(actions)
        
        continue_index = ordered.index(PredictedActionType.CONTINUE_WATCHING)
        skip_index = ordered.index(PredictedActionType.SKIP)
        
        assert continue_index < skip_index
    
    def test_empty_actions_list(self):
        predictor = PredictorV1()
        
        actions = []
        ordered = predictor._order_actions(actions)
        
        assert ordered == []
    
    def test_only_skip_action(self):
        predictor = PredictorV1()
        
        actions = [PredictedActionType.SKIP]
        ordered = predictor._order_actions(actions)
        
        assert ordered == [PredictedActionType.SKIP]
    
    def test_all_action_types(self):
        predictor = PredictorV1()
        
        actions = [
            PredictedActionType.LIKE,
            PredictedActionType.SAVE,
            PredictedActionType.FINISH_WATCHING,
            PredictedActionType.REWATCH,
            PredictedActionType.SKIP,
            PredictedActionType.CONTINUE_WATCHING,
        ]
        
        ordered = predictor._order_actions(actions)
        
        assert PredictedActionType.SKIP == ordered[-1]
        assert PredictedActionType.FINISH_WATCHING in ordered
        assert PredictedActionType.REWATCH in ordered
        
        finish_index = ordered.index(PredictedActionType.FINISH_WATCHING)
        rewatch_index = ordered.index(PredictedActionType.REWATCH)
        assert finish_index < rewatch_index