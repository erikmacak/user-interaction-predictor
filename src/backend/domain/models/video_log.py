from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func

from core.database import Base

class VideoLog(Base):
    __tablename__ = "video_logs"
    
    id: UUID = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    session_id: UUID = Column(PG_UUID(as_uuid=True), ForeignKey("audit_sessions.id"), nullable=False, index=True)
    agent_id: UUID = Column(PG_UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)
    video_url: str = Column(String, nullable=False)
    video_id: str = Column(String, nullable=False)
    video_author: str | None = Column(String, nullable=True)
    video_description: str | None = Column(String, nullable=True)
    video_time_duration: int | None = Column(Integer, nullable=True)
    video_action_watch: bool = Column(Boolean, default=False, nullable=False)
    video_action_like: bool = Column(Boolean, default=False, nullable=False)
    video_action_bookmark: bool = Column(Boolean, default=False, nullable=False)
    user_email: str | None = Column(String, nullable=True)
    topic: str | None = Column(String, nullable=True)
    gender: str | None = Column(String, nullable=True)
    country_code: str | None = Column(String, nullable=True)
    date_of_birth: str | None = Column(String, nullable=True)
    predicted_topic: str = Column(String, nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)