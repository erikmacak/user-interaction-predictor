import csv
import json
from io import StringIO
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.models.video_log import VideoLog
from domain.models.audit_session import AuditSession
from domain.platform import VideoPlatform
from domain.video import VideoSource
from domain.errors import SessionNotFoundError, NoVideoLogsFoundError
from schemas.predict import VideoMetadata

class VideoLogService:    
    CSV_HEADERS = [
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
    ]
    
    @staticmethod
    async def log_video(
        db: AsyncSession,
        session_id: UUID,
        agent_id: UUID,
        video_source: VideoSource,
        video_metadata: VideoMetadata,
        predicted_actions: list[str],
        user_state_json: str,
        segment_analyses: list | None = None
    ) -> VideoLog:
        user_profile = VideoLogService._parse_user_state(user_state_json)
        
        log_entry = VideoLogService._build_log_entry(
            session_id=session_id,
            agent_id=agent_id,
            video_source=video_source,
            video_metadata=video_metadata,
            predicted_actions=predicted_actions,
            user_profile=user_profile,
            segment_analyses=segment_analyses or []
        )
        
        db.add(log_entry)
        await db.commit()
        await db.refresh(log_entry)
        
        return log_entry
    
    @staticmethod
    async def get_agent_sessions_summary(
        db: AsyncSession,
        agent_id: UUID
    ) -> list[dict]:
        sessions = await VideoLogService._get_agent_sessions(db, agent_id)
        
        sessions_data = []
        for session in sessions:
            logs = await VideoLogService.get_logs_by_session(db, session.id)
            
            sessions_data.append({
                "session_id": str(session.id),
                "date": session.started_at.strftime("%Y-%m-%d") if session.started_at else "Unknown",
                "video_count": len(logs),
            })
        
        return sessions_data
    
    @staticmethod
    async def export_session_to_csv(
        db: AsyncSession,
        session_id: UUID,
        agent_id: UUID
    ) -> str:
        await VideoLogService._validate_session_exists(db, session_id, agent_id)
        logs = await VideoLogService.get_logs_by_session(db, session_id)
        
        if not logs:
            raise NoVideoLogsFoundError(context=f"session '{session_id}'")
        
        return VideoLogService.export_to_csv(logs)
    
    @staticmethod
    async def export_agent_to_csv(
        db: AsyncSession,
        agent_id: UUID
    ) -> str:
        logs = await VideoLogService.get_logs_by_agent(db, agent_id)
        
        if not logs:
            raise NoVideoLogsFoundError(context=f"agent '{agent_id}'")
        
        return VideoLogService.export_to_csv(logs)
    
    @staticmethod
    async def generate_session_filename(
        db: AsyncSession,
        session_id: UUID
    ) -> str:
        result = await db.execute(
            select(AuditSession).where(AuditSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return "session_unknown_data.csv"
        
        date_str = session.started_at.strftime("%Y%m%d") if session.started_at else "unknown"
        return f"session_{date_str}_data.csv"
    
    @staticmethod
    async def get_logs_by_session(
        db: AsyncSession,
        session_id: UUID
    ) -> list[VideoLog]:
        result = await db.execute(
            select(VideoLog)
            .where(VideoLog.session_id == session_id)
            .order_by(VideoLog.created_at)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_logs_by_agent(
        db: AsyncSession,
        agent_id: UUID
    ) -> list[VideoLog]:
        result = await db.execute(
            select(VideoLog)
            .where(VideoLog.agent_id == agent_id)
            .order_by(VideoLog.created_at)
        )
        return list(result.scalars().all())
    
    @staticmethod
    def export_to_csv(logs: list[VideoLog]) -> str:
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow(VideoLogService.CSV_HEADERS)
        
        for log in logs:
            writer.writerow(VideoLogService._build_csv_row(log))
        
        return output.getvalue()
    
    @staticmethod
    async def _get_agent_sessions(db: AsyncSession, agent_id: UUID) -> list[AuditSession]:
        result = await db.execute(
            select(AuditSession)
            .where(AuditSession.agent_id == agent_id)
            .order_by(AuditSession.started_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def _validate_session_exists(
        db: AsyncSession,
        session_id: UUID,
        agent_id: UUID
    ) -> None:
        result = await db.execute(
            select(AuditSession).where(
                AuditSession.id == session_id,
                AuditSession.agent_id == agent_id
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise SessionNotFoundError(session_id=str(session_id))
    
    @staticmethod
    def _build_log_entry(
        session_id: UUID,
        agent_id: UUID,
        video_source: VideoSource,
        video_metadata: VideoMetadata,
        predicted_actions: list[str],
        user_profile: dict,
        segment_analyses: list
    ) -> VideoLog:
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
            segment_analyses,
            user_profile["interest_topics"]
        )
        
        topics_str = ", ".join(user_profile["interest_topics"]) if user_profile["interest_topics"] else None
        
        return VideoLog(
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
    
    @staticmethod
    def _build_csv_row(log: VideoLog) -> list:
        return [
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
        ]
    
    @staticmethod
    def _build_video_url(platform: VideoPlatform, video_id: str) -> str:
        url_templates = {
            VideoPlatform.YOUTUBE: f"https://www.youtube.com/shorts/{video_id}",
            VideoPlatform.TIKTOK: f"https://www.tiktok.com/video/{video_id}",
            VideoPlatform.INSTAGRAM: f"https://www.instagram.com/reel/{video_id}/",
        }
        return url_templates.get(platform, f"{platform.value}/{video_id}")
    
    @staticmethod
    def _build_description_with_hashtags(
        description: str | None,
        hashtags: list[str] | None
    ) -> str | None:
        if not description and not hashtags:
            return None
        
        result = description or ""
        
        if hashtags:
            hashtag_str = " ".join(f"#{tag}" for tag in hashtags)
            result = f"{result} {hashtag_str}".strip()
        
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
        segment_analyses: list,
        user_topics: list[str]
    ) -> str:
        for analysis in segment_analyses:
            if hasattr(analysis, 'ai_analysis'):
                topic = analysis.ai_analysis.user_match.get('topic')
                
                if topic and user_topics and topic in user_topics:
                    return topic
        
        return "random"
    
    @staticmethod
    def _extract_actions(predicted_actions: list[str]) -> dict[str, bool]:
        actions_lower = [a.lower() for a in predicted_actions]
        
        return {
            "watch": "finish_watching" in actions_lower,
            "like": "like" in actions_lower,
            "bookmark": "save" in actions_lower,
        }