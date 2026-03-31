from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from core.database import Base

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    
    id: UUID = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    username: str = Column(String(100), unique=True, nullable=False, index=True)
    password_hash: str = Column(String(255), nullable=False)
    must_change_password: bool = Column(Boolean, default=False, nullable=False)
    password_changed_at: datetime | None = Column(DateTime(timezone=True), nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), default=_utc_now, nullable=False)
    updated_at: datetime = Column(DateTime(timezone=True), default=_utc_now, onupdate=_utc_now, nullable=False)