from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Literal
from datetime import datetime
from uuid import UUID
import json

from services.predictor.registry import PredictorRegistry
from domain.platform import PlatformRegistry
from domain.user_profile_schema import UserProfileSchema

Platform = Literal["YouTube", "TikTok", "Instagram"]
AgentState = Literal["auditing", "offline", "banned"]

class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    platform: str
    predictor_version: str = Field(..., min_length=1, max_length=50)
    state_file_data: str
    
    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v: str) -> str:
        return PlatformRegistry.validate_platform(v)
    
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
    def validate_state_file_data(cls, v: str) -> str:
        try:
            json.loads(v)
        except json.JSONDecodeError:
            raise ValueError('state_file_data must be valid JSON')
        
        is_valid, error_message = UserProfileSchema.validate(v)
        if not is_valid:
            raise ValueError(error_message)
        
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()

class AgentUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    platform: str | None = None
    predictor_version: str | None = Field(None, min_length=1, max_length=50)
    state: AgentState | None = None
    state_file_data: str | None = None
    
    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v: str | None) -> str | None:
        if v is not None:
            return PlatformRegistry.validate_platform(v)
        return v
    
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
    def validate_state_file_data(cls, v: str | None) -> str | None:
        if v is not None:
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('state_file_data must be valid JSON')
            
            is_valid, error_message = UserProfileSchema.validate(v)
            if not is_valid:
                raise ValueError(error_message)
        
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        return v.strip() if v else None

class AgentResponse(BaseModel):
    id: UUID
    name: str
    platform: str
    state: AgentState
    predictor_version: str
    created_at: datetime
    updated_at: datetime
    
    @field_serializer('id')
    def serialize_id(self, value: UUID, _info) -> str:
        return str(value)
    
    model_config = {"from_attributes": True}

class AgentListResponse(BaseModel):
    agents: list[AgentResponse]
    total: int