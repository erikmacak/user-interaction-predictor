from domain.action import PredictedAction, PredictedActionType

class TestDecisionEngine:
    def test_convert_actions_to_response_single_action(self):
        from services.decision_tree.decision_engine import DecisionEngine
        
        actions = [PredictedAction(PredictedActionType.LIKE)]
        
        result = DecisionEngine.convert_actions_to_response(actions)
        
        assert result == ["like"]
    
    def test_convert_actions_to_response_multiple_actions(self):
        from services.decision_tree.decision_engine import DecisionEngine
        
        actions = [
            PredictedAction(PredictedActionType.LIKE),
            PredictedAction(PredictedActionType.FINISH_WATCHING),
            PredictedAction(PredictedActionType.SKIP),
        ]
        
        result = DecisionEngine.convert_actions_to_response(actions)
        
        assert result == ["like", "finish_watching", "skip"]
    
    def test_convert_actions_with_continue_watching(self):
        from services.decision_tree.decision_engine import DecisionEngine
        
        action = PredictedAction(PredictedActionType.CONTINUE_WATCHING, seconds=10)
        actions = [action]
        
        result = DecisionEngine.convert_actions_to_response(actions)
        
        assert result == ["continue_watching_for: 10 seconds"]
    
    def test_convert_empty_actions(self):
        from services.decision_tree.decision_engine import DecisionEngine
        
        actions = []
        
        result = DecisionEngine.convert_actions_to_response(actions)
        
        assert result == []