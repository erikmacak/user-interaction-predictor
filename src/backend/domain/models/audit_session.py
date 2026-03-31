from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from core.database import Base

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AuditSession(Base):
    __tablename__ = "audit_sessions"
    
    id: UUID = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    agent_id: UUID | None = Column(PG_UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=True)
    state: str = Column(String(50), nullable=False, default="running")
    started_at: datetime = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
    ended_at: datetime | None = Column(DateTime(timezone=True), nullable=True)
    
    agent = relationship("Agent", backref="audit_sessions")