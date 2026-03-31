from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from core.database import Base

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Agent(Base):
    __tablename__ = "agents"
    
    id: UUID = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    name: str = Column(String(255), nullable=False, unique=True, index=True)
    platform: str = Column(String(50), nullable=False)
    state: str = Column(String(50), nullable=False, default="offline")
    predictor_version: str = Column(String(50), nullable=False)
    state_file_data: str = Column(Text, nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
    updated_at: datetime = Column(DateTime(timezone=True), nullable=False, default=_utc_now, onupdate=_utc_now)