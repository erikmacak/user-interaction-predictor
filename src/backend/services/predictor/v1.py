import random
from typing import List

from domain.action import PredictedActionType
from services.predictor.base import BasePredictor

class PredictorV1(BasePredictor):
    """
    First experimental predictor implementation.

    Generates a realistic sequence of user interactions
    based on probabilistic group selection and ordering rules.
    """

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
            PredictedActionType.FOLLOW: 0.15,
            PredictedActionType.SAVE: 0.20,
        },
        "consumption": {
            PredictedActionType.FINISH_WATCHING: 0.55,
            PredictedActionType.REWATCH: 0.20,
        },
    }
    
    def _predict_from_data(self, data) -> List[PredictedActionType]:
        actions: List[PredictedActionType] = []

        for group, probability in self.GROUP_PROBABILITIES.items():
            if random.random() > probability:
                continue
            actions.extend(self._select_actions_from_group(group))

        actions.extend(self.MANDATORY_ACTIONS)

        actions = self._enforce_action_dependencies(actions)
        actions = self._order_actions(actions)

        return actions

    def _select_actions_from_group(
        self,
        group: str,
    ) -> List[PredictedActionType]:
        selected: List[PredictedActionType] = []

        for action, probability in self.ACTION_PROBABILITIES[group].items():
            if random.random() <= probability:
                selected.append(action)

        return selected

    def _enforce_action_dependencies(
        self,
        actions: List[PredictedActionType],
    ) -> List[PredictedActionType]:
        if (
            PredictedActionType.REWATCH in actions
            and PredictedActionType.FINISH_WATCHING not in actions
        ):
            actions.remove(PredictedActionType.REWATCH)

        return actions

    def _order_actions(
        self,
        actions: List[PredictedActionType],
    ) -> List[PredictedActionType]:

        has_finish = PredictedActionType.FINISH_WATCHING in actions
        has_rewatch = PredictedActionType.REWATCH in actions

        if has_rewatch and not has_finish:
            actions = [a for a in actions if a != PredictedActionType.REWATCH]
            has_rewatch = False

        engagement_actions = [
            action
            for action in actions
            if action
            not in {
                PredictedActionType.FINISH_WATCHING,
                PredictedActionType.REWATCH,
                PredictedActionType.SKIP,
            }
        ]

        random.shuffle(engagement_actions)

        ordered: List[PredictedActionType] = []

        before_finish: List[PredictedActionType] = []
        between_finish_and_rewatch: List[PredictedActionType] = []
        after_rewatch: List[PredictedActionType] = []

        for action in engagement_actions:
            bucket = random.choice(
                ["before", "between", "after"] if has_rewatch else ["before", "after"]
            )

            if bucket == "before":
                before_finish.append(action)
            elif bucket == "between":
                between_finish_and_rewatch.append(action)
            else:
                after_rewatch.append(action)

        ordered.extend(before_finish)

        if has_finish:
            ordered.append(PredictedActionType.FINISH_WATCHING)

        ordered.extend(between_finish_and_rewatch)

        if has_rewatch:
            ordered.append(PredictedActionType.REWATCH)

        ordered.extend(after_rewatch)

        if PredictedActionType.SKIP in actions:
            ordered = [a for a in ordered if a != PredictedActionType.SKIP] + [PredictedActionType.SKIP]

        return ordered