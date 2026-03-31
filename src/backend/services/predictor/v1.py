import random

from domain.action import PredictedActionType
from services.predictor.base import BasePredictor

class PredictorV1(BasePredictor):
    GROUP_PROBABILITIES = {
        "engagement": 0.65,
        "consumption": 0.35,
    }
    
    MANDATORY_ACTIONS = {
        PredictedActionType.SKIP,
    }
    
    ACTION_PROBABILITIES = {
        "engagement": {
            PredictedActionType.LIKE: 0.45,
            PredictedActionType.SAVE: 0.20,
        },
        "consumption": {
            PredictedActionType.FINISH_WATCHING: 0.55,
            PredictedActionType.REWATCH: 0.20,
        },
    }
    
    CONSUMPTION_ACTIONS = {
        PredictedActionType.FINISH_WATCHING,
        PredictedActionType.REWATCH,
        PredictedActionType.SKIP,
    }
    
    def _predict_from_data(self, data: dict) -> list[PredictedActionType]:
        actions = self._select_random_actions()
        actions = self._enforce_action_dependencies(actions)
        actions = self._order_actions(actions)
        
        return actions
    
    def _select_random_actions(self) -> list[PredictedActionType]:
        actions = []
        
        for group, probability in self.GROUP_PROBABILITIES.items():
            if random.random() <= probability:
                actions.extend(self._select_actions_from_group(group))
        
        actions.extend(self.MANDATORY_ACTIONS)
        
        return actions
    
    def _select_actions_from_group(self, group: str) -> list[PredictedActionType]:
        selected = []
        
        for action, probability in self.ACTION_PROBABILITIES[group].items():
            if random.random() <= probability:
                selected.append(action)
        
        return selected
    
    def _enforce_action_dependencies(
        self,
        actions: list[PredictedActionType],
    ) -> list[PredictedActionType]:
        if (
            PredictedActionType.REWATCH in actions
            and PredictedActionType.FINISH_WATCHING not in actions
        ):
            actions.remove(PredictedActionType.REWATCH)
        
        return actions
    
    def _order_actions(
        self,
        actions: list[PredictedActionType],
    ) -> list[PredictedActionType]:
        has_finish = PredictedActionType.FINISH_WATCHING in actions
        has_rewatch = PredictedActionType.REWATCH in actions
        
        if has_rewatch and not has_finish:
            actions = [a for a in actions if a != PredictedActionType.REWATCH]
            has_rewatch = False
        
        engagement_actions = self._extract_engagement_actions(actions)
        random.shuffle(engagement_actions)
        
        buckets = self._distribute_actions_into_buckets(
            engagement_actions,
            has_rewatch
        )
        
        return self._build_ordered_sequence(
            buckets,
            has_finish,
            has_rewatch,
            PredictedActionType.SKIP in actions
        )
    
    def _extract_engagement_actions(
        self,
        actions: list[PredictedActionType]
    ) -> list[PredictedActionType]:
        return [
            action for action in actions
            if action not in self.CONSUMPTION_ACTIONS
        ]
    
    def _distribute_actions_into_buckets(
        self,
        engagement_actions: list[PredictedActionType],
        has_rewatch: bool
    ) -> dict[str, list[PredictedActionType]]:
        buckets = {
            "before": [],
            "between": [],
            "after": []
        }
        
        bucket_choices = ["before", "between", "after"] if has_rewatch else ["before", "after"]
        
        for action in engagement_actions:
            bucket = random.choice(bucket_choices)
            buckets[bucket].append(action)
        
        return buckets
    
    def _build_ordered_sequence(
        self,
        buckets: dict[str, list[PredictedActionType]],
        has_finish: bool,
        has_rewatch: bool,
        has_skip: bool
    ) -> list[PredictedActionType]:
        ordered = []
        
        ordered.extend(buckets["before"])
        
        if has_finish:
            ordered.append(PredictedActionType.FINISH_WATCHING)
        
        ordered.extend(buckets["between"])
        
        if has_rewatch:
            ordered.append(PredictedActionType.REWATCH)
        
        ordered.extend(buckets["after"])
        
        if has_skip:
            ordered = [a for a in ordered if a != PredictedActionType.SKIP]
            ordered.append(PredictedActionType.SKIP)
        
        return ordered