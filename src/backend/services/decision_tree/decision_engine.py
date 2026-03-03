from typing import List, Optional
from dataclasses import dataclass
import random

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
    segment_analysis: Optional[SegmentAnalysisResult]
    previous_actions: List[PredictedAction]
    description: Optional[str]
    hashtags: Optional[List[str]]
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
    
    @staticmethod
    def decide(context: DecisionContext) -> List[PredictedAction]:
        
        actions = []
        
        if context.segment_analysis is None:
            return DecisionEngine._decide_from_metadata_only(context)
        
        is_first_segment = context.segment_number == 1
        
        score = DecisionEngine._calculate_match_score(context, is_first_segment)
        
        print(f"      📊 Decision Score: {score:.2f}/1.0")
        
        if is_first_segment:
            actions = DecisionEngine._decide_first_segment(score, context)
        else:
            actions = DecisionEngine._decide_other_segment(score, context)
        
        actions = DecisionEngine._validate_actions(actions, context)
        
        return actions
    
    @staticmethod
    def _calculate_match_score(context: DecisionContext, is_first_segment: bool) -> float:
        
        weights = DecisionEngine.FIRST_SEGMENT_WEIGHTS if is_first_segment else DecisionEngine.OTHER_SEGMENT_WEIGHTS
        
        ai_analysis = context.segment_analysis.ai_analysis
        user_match = ai_analysis.user_match
        tech_quality = ai_analysis.technical_quality
        
        score = 0.0
        
        emotions = user_match.get('emotions')
        if emotions and isinstance(emotions, list):
            emotion_count = len([e for e in emotions if e is not None and e != ""])
            emotion_score = emotion_count / 2.0  # 0, 0.5, or 1.0
            score += emotion_score * weights['emotion_match']
        
        language_match = user_match.get('language_code') is not None
        score += (1.0 if language_match else 0.0) * weights['language_match']
        
        topic_match = user_match.get('topic') is not None
        score += (1.0 if topic_match else 0.0) * weights['topic_match']
        
        score += (1.0 if tech_quality.get('visual_dynamics') else 0.0) * weights['visual_dynamics']
        score += (1.0 if tech_quality.get('high_production_value') else 0.0) * weights['production_value']
        score += (1.0 if tech_quality.get('clear_punchline') else 0.0) * weights['punchline']
        score += (1.0 if tech_quality.get('known_music_detected') else 0.0) * weights['music']
        score += (1.0 if tech_quality.get('retention_curve_rising') else 0.0) * weights['retention']
        
        if context.initial_analysis.engagement.weighted_score > 50000:
            score += 0.10
        
        if context.initial_analysis.is_favorite_author:
            score += 0.15 
        
        return min(score, 1.0)
    
    @staticmethod
    def _decide_first_segment(score: float, context: DecisionContext) -> List[PredictedAction]:
        
        actions = []
        
        if score >= 0.75:
            actions.append(PredictedAction(PredictedActionType.LIKE))
            
            if score >= 0.85 and random.random() < 0.3:
                actions.append(PredictedAction(PredictedActionType.SAVE))
            
            if score >= 0.90 and random.random() < 0.15:
                actions.append(PredictedAction(PredictedActionType.REWATCH))
            
            return actions
        
        elif score >= 0.55:
            remaining_duration = context.video_duration - context.current_video_time
            watch_seconds = min(int(remaining_duration * 0.5), 10)
            
            actions.append(PredictedAction(PredictedActionType.CONTINUE_WATCHING, watch_seconds))
            return actions
        
        elif score >= 0.35:
            if random.random() < 0.4:
                actions.append(PredictedAction(PredictedActionType.LIKE))
            
            remaining_duration = context.video_duration - context.current_video_time
            watch_seconds = min(int(remaining_duration * 0.3), 5)
            
            actions.append(PredictedAction(PredictedActionType.CONTINUE_WATCHING, watch_seconds))
            return actions
        
        else:
            actions.append(PredictedAction(PredictedActionType.SKIP))
            return actions
    
    @staticmethod
    def _decide_other_segment(score: float, context: DecisionContext) -> List[PredictedAction]:
        
        actions = []
        
        segment_fatigue = (context.segment_number - 1) * 0.05
        adjusted_score = max(0, score - segment_fatigue)
        
        is_last_segment = context.segment_number == context.total_segments
        
        if is_last_segment:
            if adjusted_score >= 0.50:
                if not DecisionEngine._has_action_type(context.previous_actions, PredictedActionType.LIKE):
                    actions.append(PredictedAction(PredictedActionType.LIKE))
                
                actions.append(PredictedAction(PredictedActionType.FINISH_WATCHING))
                
                if adjusted_score >= 0.85 and random.random() < 0.1:
                    actions.append(PredictedAction(PredictedActionType.REWATCH))
                
                actions.append(PredictedAction(PredictedActionType.SKIP))
                return actions
            else:
                actions.append(PredictedAction(PredictedActionType.FINISH_WATCHING))
                actions.append(PredictedAction(PredictedActionType.SKIP))
                return actions
        
        if adjusted_score >= 0.70:
            if not DecisionEngine._has_action_type(context.previous_actions, PredictedActionType.LIKE):
                actions.append(PredictedAction(PredictedActionType.LIKE))
            
            return actions
        
        elif adjusted_score >= 0.45:
            remaining_duration = context.video_duration - context.current_video_time
            watch_seconds = min(int(remaining_duration * 0.4), 8)
            
            actions.append(PredictedAction(PredictedActionType.CONTINUE_WATCHING, watch_seconds))
            return actions
        
        else:
            actions.append(PredictedAction(PredictedActionType.SKIP))
            return actions
    
    @staticmethod
    def _decide_from_metadata_only(context: DecisionContext) -> List[PredictedAction]:
        
        actions = []
        score = 0.0
        
        print(f"      📊 Metadata-Only Decision")
        
        engagement_score = context.initial_analysis.engagement.weighted_score
        if engagement_score > 100000:
            score += 0.40
        elif engagement_score > 50000:
            score += 0.25
        elif engagement_score > 10000:
            score += 0.15
        
        if context.initial_analysis.is_favorite_author:
            score += 0.35
        
        if context.hashtags and context.user_state:
            user_topics = context.user_state.get('interest_topics', [])
            if user_topics and isinstance(user_topics, list):
                hashtag_matches = sum(1 for tag in context.hashtags if tag.lower() in [t.lower() for t in user_topics])
                if hashtag_matches > 0:
                    score += 0.25 * min(hashtag_matches / 3.0, 1.0)
        
        print(f"      Score: {score:.2f}/1.0")
        
        if score >= 0.60:
            actions.append(PredictedAction(PredictedActionType.LIKE))
            
            if context.video_duration:
                watch_seconds = min(context.video_duration, 15)
                actions.append(PredictedAction(PredictedActionType.CONTINUE_WATCHING, watch_seconds))
            
            actions.append(PredictedAction(PredictedActionType.SKIP))
        
        elif score >= 0.35:
            if context.video_duration:
                watch_seconds = min(context.video_duration, 8)
                actions.append(PredictedAction(PredictedActionType.CONTINUE_WATCHING, watch_seconds))
            
            actions.append(PredictedAction(PredictedActionType.SKIP))
        
        else:
            actions.append(PredictedAction(PredictedActionType.SKIP))
        
        return actions
    
    @staticmethod
    def _has_action_type(actions: List[PredictedAction], action_type: PredictedActionType) -> bool:
        return any(a.action_type == action_type for a in actions)
    
    @staticmethod
    def _validate_actions(actions: List[PredictedAction], context: DecisionContext) -> List[PredictedAction]:
        
        validated = []
        seen_types = set()
        
        for action in actions:
            if action.action_type in seen_types:
                continue
            
            if action.action_type == PredictedActionType.CONTINUE_WATCHING:
                remaining = context.video_duration - context.current_video_time
                
                if action.seconds:
                    action.seconds = min(action.seconds, int(remaining))
                    
                    if action.seconds < 1:
                        continue 
            
            validated.append(action)
            seen_types.add(action.action_type)
        
        return validated
    
    @staticmethod
    def convert_actions_to_response(actions: List[PredictedAction]) -> List[str]:
        result = []
        seen = set()
        
        for action in actions:
            action_str = action.to_string()
            
            if action_str not in seen:
                result.append(action_str)
                seen.add(action_str)
        
        return result