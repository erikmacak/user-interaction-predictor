from pydantic import BaseModel, field_serializer
from datetime import datetime
from uuid import UUID

class AuditSessionStartRequest(BaseModel):
    agent_id: UUID

class AuditSessionResponse(BaseModel):
    id: UUID
    agent_id: UUID
    agent_name: str
    agent_platform: str
    state: str
    started_at: datetime
    ended_at: datetime | None
    
    @field_serializer('id', 'agent_id')
    def serialize_uuid(self, value: UUID, _info) -> str:
        return str(value)
    
    model_config = {"from_attributes": True}

class AuditSessionListResponse(BaseModel):
    sessions: list[AuditSessionResponse]
    total: int