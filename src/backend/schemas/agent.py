from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Literal
from datetime import datetime
from uuid import UUID
import json

from services.predictor.registry import PredictorRegistry

Platform = Literal["YouTube", "TikTok", "Instagram"]
AgentState = Literal["offline", "banned"]

class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    platform: Platform
    predictor_version: str = Field(..., min_length=1, max_length=50)
    check_video_existence: bool = True
    state_file_data: str

    @field_validator('predictor_version')
    @classmethod
    def validate_predictor_version(cls, v: str) -> str:
        supported_versions = list(PredictorRegistry._predictors.keys())
        if v not in supported_versions:
            raise ValueError(
                f"Unsupported predictor version '{v}'. "
                f"Supported versions: {', '.join(supported_versions)}"
            )
        return v
    
    @field_validator('state_file_data')
    @classmethod
    def validate_json(cls, v: str) -> str:
        try:
            json.loads(v)
            return v
        except json.JSONDecodeError:
            raise ValueError('state_file_data must be valid JSON')
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()

class AgentUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    platform: Platform | None = None
    predictor_version: str | None = Field(None, min_length=1, max_length=50)
    check_video_existence: bool | None = None
    state: AgentState | None = None
    state_file_data: str | None = None

    @field_validator('predictor_version')
    @classmethod
    def validate_predictor_version(cls, v: str | None) -> str | None:
        if v is not None:
            supported_versions = list(PredictorRegistry._predictors.keys())
            if v not in supported_versions:
                raise ValueError(
                    f"Unsupported predictor version '{v}'. "
                    f"Supported versions: {', '.join(supported_versions)}"
                )
        return v
    
    @field_validator('state_file_data')
    @classmethod
    def validate_json(cls, v: str | None) -> str | None:
        if v is not None:
            try:
                json.loads(v)
                return v
            except json.JSONDecodeError:
                raise ValueError('state_file_data must be valid JSON')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        return v.strip() if v else None

class AgentResponse(BaseModel):
    id: UUID
    name: str
    platform: Platform
    state: AgentState
    predictor_version: str
    check_video_existence: bool
    created_at: datetime
    updated_at: datetime
    
    @field_serializer('id')
    def serialize_id(self, value: UUID) -> str:
        return str(value)
    
    model_config = {"from_attributes": True}

class AgentListResponse(BaseModel):
    agents: list[AgentResponse]
    total: int