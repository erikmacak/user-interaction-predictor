import json
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from domain.models.video_log import VideoLog
from domain.models.audit_session import AuditSession
from schemas.predict import VideoMetadata
from domain.video import VideoSource, VideoPlatform

class VideoLogService:
    
    @staticmethod
    def _build_video_url(platform: VideoPlatform, video_id: str) -> str:
        if platform == VideoPlatform.YOUTUBE:
            return f"https://www.youtube.com/shorts/{video_id}"
        elif platform == VideoPlatform.TIKTOK:
            return f"https://www.tiktok.com/video/{video_id}"
        elif platform == VideoPlatform.INSTAGRAM:
            return f"https://www.instagram.com/reel/{video_id}/"
        return f"{platform.value}/{video_id}"
    
    @staticmethod
    def _build_description_with_hashtags(
        description: Optional[str],
        hashtags: Optional[List[str]]
    ) -> Optional[str]:
        if not description and not hashtags:
            return None
        
        result = description or ""
        
        if hashtags:
            hashtag_str = " ".join(f"#{tag}" for tag in hashtags)
            if result:
                result = f"{result} {hashtag_str}"
            else:
                result = hashtag_str
        
        return result
    
    @staticmethod
    def _parse_user_state(user_state_json: str) -> dict:
        try:
            state = json.loads(user_state_json)
            profile = state.get("user_profile", {})
            triggers = profile.get("retention_triggers", {})
            
            return {
                "user_email": profile.get("user_email"),
                "gender": profile.get("gender"),
                "country_code": profile.get("country_code"),
                "date_of_birth": profile.get("date_of_birth"),
                "interest_topics": triggers.get("interest_topics", []),
            }
        except (json.JSONDecodeError, KeyError):
            return {
                "user_email": None,
                "gender": None,
                "country_code": None,
                "date_of_birth": None,
                "interest_topics": [],
            }
    
    @staticmethod
    def _extract_predicted_topic(
        predicted_actions: List[str],
        segment_analyses: List,
        user_topics: List[str]
    ) -> str:
        
        for analysis in segment_analyses:
            if hasattr(analysis, 'ai_analysis'):
                topic = analysis.ai_analysis.user_match.get('topic')
                
                if topic and user_topics:
                    if topic in user_topics:
                        return topic
        
        return "random"
    
    @staticmethod
    def _extract_actions(predicted_actions: List[str]) -> dict:
        actions_lower = [a.lower() for a in predicted_actions]
        
        return {
            "watch": "finish_watching" in actions_lower,
            "like": "like" in actions_lower,
            "bookmark": "save" in actions_lower,
        }
    
    @staticmethod
    async def log_video(
        db: AsyncSession,
        session_id: UUID,
        agent_id: UUID,
        video_source: VideoSource,
        video_metadata: VideoMetadata,
        predicted_actions: List[str],
        user_state_json: str,
        segment_analyses: List = None
    ) -> VideoLog:

        user_profile = VideoLogService._parse_user_state(user_state_json)
        
        video_url = VideoLogService._build_video_url(
            video_source.platform,
            video_source.video_id
        )
        
        description = VideoLogService._build_description_with_hashtags(
            video_metadata.description,
            video_metadata.hashtags
        )

        actions = VideoLogService._extract_actions(predicted_actions)
        
        predicted_topic = VideoLogService._extract_predicted_topic(
            predicted_actions,
            segment_analyses or [],
            user_profile["interest_topics"]
        )
        
        topics_str = ", ".join(user_profile["interest_topics"]) if user_profile["interest_topics"] else None
        
        log_entry = VideoLog(
            session_id=session_id,
            agent_id=agent_id,
            video_url=video_url,
            video_id=video_source.video_id,
            video_author=video_metadata.video_author,
            video_description=description,
            video_time_duration=video_metadata.video_time_duration,
            video_action_watch=actions["watch"],
            video_action_like=actions["like"],
            video_action_bookmark=actions["bookmark"],
            user_email=user_profile["user_email"],
            topic=topics_str,
            gender=user_profile["gender"],
            country_code=user_profile["country_code"],
            date_of_birth=user_profile["date_of_birth"],
            predicted_topic=predicted_topic,
        )
        
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        
        return log_entry
    
    @staticmethod
    async def get_logs_by_session(
        db: AsyncSession,
        session_id: UUID
    ) -> List[VideoLog]:
        result = await db.execute(
            select(VideoLog)
            .where(VideoLog.session_id == session_id)
            .order_by(VideoLog.created_at)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_logs_by_agent(
        db: AsyncSession,
        agent_id: UUID
    ) -> List[VideoLog]:
        result = await db.execute(
            select(VideoLog)
            .where(VideoLog.agent_id == agent_id)
            .order_by(VideoLog.created_at)
        )
        return result.scalars().all()
    
    @staticmethod
    def export_to_csv(logs: List[VideoLog]) -> str:
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            'video_url',
            'video_id',
            'video_author',
            'video_description',
            'video_time_duration',
            'video_action_watch',
            'video_action_like',
            'video_action_bookmark',
            'user_email',
            'topic',
            'gender',
            'country_code',
            'date_of_birth',
            'predicted_topic',
        ])
        
        for log in logs:
            writer.writerow([
                log.video_url,
                log.video_id,
                log.video_author or '',
                log.video_description or '',
                log.video_time_duration or '',
                log.video_action_watch,
                log.video_action_like,
                log.video_action_bookmark,
                log.user_email or '',
                log.topic or '',
                log.gender or '',
                log.country_code or '',
                log.date_of_birth or '',
                log.predicted_topic,
            ])
        
        return output.getvalue()