from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class AuditSessionStartRequest(BaseModel):
    agent_id: UUID
    
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

class AuditSessionResponse(BaseModel):
    id: UUID
    agent_id: UUID
    agent_name: str
    agent_platform: str
    state: str
    started_at: datetime
    ended_at: datetime | None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={UUID: str},
    )

class AuditSessionListResponse(BaseModel):
    sessions: list[AuditSessionResponse] = Field(default_factory=list)
    total: int = Field(..., ge=0)
    
    model_config = ConfigDict(frozen=True)