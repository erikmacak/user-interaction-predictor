from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from core.database import Base

class VideoLog(Base):

    __tablename__ = "video_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    session_id = Column(UUID(as_uuid=True), ForeignKey("audit_sessions.id"), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)
    
    video_url = Column(String, nullable=False)
    video_id = Column(String, nullable=False)
    video_author = Column(String, nullable=True)
    video_description = Column(String, nullable=True)
    video_time_duration = Column(Integer, nullable=True)
    
    video_action_watch = Column(Boolean, default=False)
    video_action_like = Column(Boolean, default=False)
    video_action_bookmark = Column(Boolean, default=False)
    
    user_email = Column(String, nullable=True)
    topic = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    country_code = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    
    predicted_topic = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)