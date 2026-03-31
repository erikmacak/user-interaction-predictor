import random
from dataclasses import dataclass

from domain.action import PredictedActionType, PredictedAction
from services.predictor.initial_analysis import InitialAnalysisResult
from services.predictor.segment_analyzer import SegmentAnalysisResult

@dataclass
class DecisionContext:
    segment_number: int
    total_segments: int
    video_duration: int
    current_video_time: float
    initial_analysis: InitialAnalysisResult
    segment_analysis: SegmentAnalysisResult | None
    previous_actions: list[PredictedAction]
    description: str | None
    hashtags: list[str] | None
    user_state: dict

class DecisionEngine:
    
    FIRST_SEGMENT_WEIGHTS = {
        'emotion_match': 0.25,
        'language_match': 0.20,
        'topic_match': 0.25,
        'visual_dynamics': 0.10,
        'production_value': 0.08,
        'punchline': 0.05,
        'music': 0.02,
        'retention': 0.05,
    }
    
    OTHER_SEGMENT_WEIGHTS = {
        'emotion_match': 0.15,
        'language_match': 0.10,
        'topic_match': 0.20,
        'visual_dynamics': 0.15,
        'production_value': 0.10,
        'punchline': 0.15,
        'music': 0.05,
        'retention': 0.10,
    }
    
    ENGAGEMENT_BONUS = 0.10
    FAVORITE_AUTHOR_BONUS = 0.15
    ENGAGEMENT_THRESHOLD = 50000
    
    @staticmethod
    def decide(context: DecisionContext) -> list[PredictedAction]:
        if context.segment_analysis is None:
            return DecisionEngine._decide_from_metadata_only(context)
        
        is_first_segment = context.segment_number == 1
        score = DecisionEngine._calculate_match_score(context, is_first_segment)
        
        print(f"       Decision Score: {score:.2f}/1.0")
        
        if is_first_segment:
            actions = DecisionEngine._decide_first_segment(score, context)
        else:
            actions = DecisionEngine._decide_other_segment(score, context)
        
        return DecisionEngine._validate_actions(actions, context)
    
    @staticmethod
    def _calculate_match_score(context: DecisionContext, is_first_segment: bool) -> float:
        weights = DecisionEngine.FIRST_SEGMENT_WEIGHTS if is_first_segment else DecisionEngine.OTHER_SEGMENT_WEIGHTS
        
        ai_analysis = context.segment_analysis.ai_analysis
        user_match = ai_analysis.user_match
        tech_quality = ai_analysis.technical_quality
        
        score = 0.0
        score += DecisionEngine._calculate_emotion_score(user_match.get('emotions'), weights['emotion_match'])
        score += DecisionEngine._calculate_boolean_score(user_match.get('language_code'), weights['language_match'])
        score += DecisionEngine._calculate_boolean_score(user_match.get('topic'), weights['topic_match'])
        score += DecisionEngine._calculate_boolean_score(tech_quality.get('visual_dynamics'), weights['visual_dynamics'])
        score += DecisionEngine._calculate_boolean_score(tech_quality.get('high_production_value'), weights['production_value'])
        score += DecisionEngine._calculate_boolean_score(tech_quality.get('clear_punchline'), weights['punchline'])
        score += DecisionEngine._calculate_boolean_score(tech_quality.get('known_music_detected'), weights['music'])
        score += DecisionEngine._calculate_boolean_score(tech_quality.get('retention_curve_rising'), weights['retention'])
        score += DecisionEngine._calculate_bonus_score(context.initial_analysis)
        
        return min(score, 1.0)
    
    @staticmethod
    def _calculate_emotion_score(emotions: list | None, weight: float) -> float:
        if not emotions or not isinstance(emotions, list):
            return 0.0
        
        emotion_count = len([e for e in emotions if e is not None and e != ""])
        emotion_score = emotion_count / 2.0
        return emotion_score * weight
    
    @staticmethod
    def _calculate_boolean_score(value: any, weight: float) -> float:
        return weight if value else 0.0
    
    @staticmethod
    def _calculate_bonus_score(initial_analysis: InitialAnalysisResult) -> float:
        score = 0.0
        
        if initial_analysis.engagement.weighted_score > DecisionEngine.ENGAGEMENT_THRESHOLD:
            score += DecisionEngine.ENGAGEMENT_BONUS
        
        if initial_analysis.is_favorite_author:
            score += DecisionEngine.FAVORITE_AUTHOR_BONUS
        
        return score
    
    @staticmethod
    def _decide_first_segment(score: float, context: DecisionContext) -> list[PredictedAction]:
        if score >= 0.75:
            return DecisionEngine._create_high_interest_actions(score)
        elif score >= 0.55:
            return DecisionEngine._create_continue_watching_actions(context, 0.5, 10)
        elif score >= 0.35:
            return DecisionEngine._create_medium_interest_actions(context)
        else:
            return [PredictedAction(PredictedActionType.SKIP)]
    
    @staticmethod
    def _create_high_interest_actions(score: float) -> list[PredictedAction]:
        actions = [PredictedAction(PredictedActionType.LIKE)]
        
        if score >= 0.85 and random.random() < 0.3:
            actions.append(PredictedAction(PredictedActionType.SAVE))
        
        if score >= 0.90 and random.random() < 0.15:
            actions.append(PredictedAction(PredictedActionType.REWATCH))
        
        return actions
    
    @staticmethod
    def _create_continue_watching_actions(
        context: DecisionContext,
        duration_multiplier: float,
        max_seconds: int
    ) -> list[PredictedAction]:
        remaining_duration = context.video_duration - context.current_video_time
        watch_seconds = min(int(remaining_duration * duration_multiplier), max_seconds)
        
        return [PredictedAction(PredictedActionType.CONTINUE_WATCHING, watch_seconds)]
    
    @staticmethod
    def _create_medium_interest_actions(context: DecisionContext) -> list[PredictedAction]:
        actions = []
        
        if random.random() < 0.4:
            actions.append(PredictedAction(PredictedActionType.LIKE))
        
        remaining_duration = context.video_duration - context.current_video_time
        watch_seconds = min(int(remaining_duration * 0.3), 5)
        actions.append(PredictedAction(PredictedActionType.CONTINUE_WATCHING, watch_seconds))
        
        return actions
    
    @staticmethod
    def _decide_other_segment(score: float, context: DecisionContext) -> list[PredictedAction]:
        segment_fatigue = (context.segment_number - 1) * 0.05
        adjusted_score = max(0, score - segment_fatigue)
        
        is_last_segment = context.segment_number == context.total_segments
        
        if is_last_segment:
            return DecisionEngine._create_last_segment_actions(adjusted_score, context)
        
        if adjusted_score >= 0.70:
            return DecisionEngine._create_like_action_if_needed(context)
        elif adjusted_score >= 0.45:
            return DecisionEngine._create_continue_watching_actions(context, 0.4, 8)
        else:
            return [PredictedAction(PredictedActionType.SKIP)]
    
    @staticmethod
    def _create_last_segment_actions(adjusted_score: float, context: DecisionContext) -> list[PredictedAction]:
        actions = []
        
        if adjusted_score >= 0.50:
            if not DecisionEngine._has_action_type(context.previous_actions, PredictedActionType.LIKE):
                actions.append(PredictedAction(PredictedActionType.LIKE))
            
            actions.append(PredictedAction(PredictedActionType.FINISH_WATCHING))
            
            if adjusted_score >= 0.85 and random.random() < 0.1:
                actions.append(PredictedAction(PredictedActionType.REWATCH))
            
            actions.append(PredictedAction(PredictedActionType.SKIP))
        else:
            actions.append(PredictedAction(PredictedActionType.FINISH_WATCHING))
            actions.append(PredictedAction(PredictedActionType.SKIP))
        
        return actions
    
    @staticmethod
    def _create_like_action_if_needed(context: DecisionContext) -> list[PredictedAction]:
        if not DecisionEngine._has_action_type(context.previous_actions, PredictedActionType.LIKE):
            return [PredictedAction(PredictedActionType.LIKE)]
        return []
    
    @staticmethod
    def _decide_from_metadata_only(context: DecisionContext) -> list[PredictedAction]:
        print(f"       Metadata-Only Decision")
        
        score = DecisionEngine._calculate_metadata_score(context)
        
        print(f"      Score: {score:.2f}/1.0")
        
        if score >= 0.60:
            return DecisionEngine._create_high_engagement_metadata_actions(context)
        elif score >= 0.35:
            return DecisionEngine._create_medium_engagement_metadata_actions(context)
        else:
            return [PredictedAction(PredictedActionType.SKIP)]
    
    @staticmethod
    def _calculate_metadata_score(context: DecisionContext) -> float:
        score = 0.0
        
        engagement_score = context.initial_analysis.engagement.weighted_score
        if engagement_score > 100000:
            score += 0.40
        elif engagement_score > 50000:
            score += 0.25
        elif engagement_score > 10000:
            score += 0.15
        
        if context.initial_analysis.is_favorite_author:
            score += 0.35
        
        score += DecisionEngine._calculate_hashtag_match_score(context)
        
        return score
    
    @staticmethod
    def _calculate_hashtag_match_score(context: DecisionContext) -> float:
        if not context.hashtags or not context.user_state:
            return 0.0
        
        user_topics = context.user_state.get('interest_topics', [])
        if not user_topics or not isinstance(user_topics, list):
            return 0.0
        
        hashtag_matches = sum(
            1 for tag in context.hashtags 
            if tag.lower() in [t.lower() for t in user_topics]
        )
        
        if hashtag_matches > 0:
            return 0.25 * min(hashtag_matches / 3.0, 1.0)
        
        return 0.0
    
    @staticmethod
    def _create_high_engagement_metadata_actions(context: DecisionContext) -> list[PredictedAction]:
        actions = [PredictedAction(PredictedActionType.LIKE)]
        
        if context.video_duration:
            watch_seconds = min(context.video_duration, 15)
            actions.append(PredictedAction(PredictedActionType.CONTINUE_WATCHING, watch_seconds))
        
        actions.append(PredictedAction(PredictedActionType.SKIP))
        return actions
    
    @staticmethod
    def _create_medium_engagement_metadata_actions(context: DecisionContext) -> list[PredictedAction]:
        actions = []
        
        if context.video_duration:
            watch_seconds = min(context.video_duration, 8)
            actions.append(PredictedAction(PredictedActionType.CONTINUE_WATCHING, watch_seconds))
        
        actions.append(PredictedAction(PredictedActionType.SKIP))
        return actions
    
    @staticmethod
    def _has_action_type(actions: list[PredictedAction], action_type: PredictedActionType) -> bool:
        return any(a.action_type == action_type for a in actions)
    
    @staticmethod
    def _validate_actions(actions: list[PredictedAction], context: DecisionContext) -> list[PredictedAction]:
        validated = []
        seen_types = set()
        
        for action in actions:
            if action.action_type in seen_types:
                continue
            
            if action.action_type == PredictedActionType.CONTINUE_WATCHING:
                action = DecisionEngine._validate_continue_watching_action(action, context)
                if action is None:
                    continue
            
            validated.append(action)
            seen_types.add(action.action_type)
        
        return validated
    
    @staticmethod
    def _validate_continue_watching_action(
        action: PredictedAction,
        context: DecisionContext
    ) -> PredictedAction | None:
        remaining = context.video_duration - context.current_video_time
        
        if not action.seconds:
            return action
        
        adjusted_seconds = min(action.seconds, int(remaining))
        
        if adjusted_seconds < 1:
            return None
        
        return action.with_seconds(adjusted_seconds)
    
    @staticmethod
    def convert_actions_to_response(actions: list[PredictedAction]) -> list[str]:
        result = []
        seen = set()
        
        for action in actions:
            action_str = action.to_string()
            
            if action_str not in seen:
                result.append(action_str)
                seen.add(action_str)
        
        return result