import json
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from services.predictor.registry import PredictorRegistry
from domain.platform import PlatformRegistry
from domain.user_profile_schema import UserProfileSchema
from domain.errors import UnsupportedPredictorVersionError

AgentState = Literal["auditing", "offline", "banned"]

class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    platform: str
    predictor_version: str = Field(..., min_length=1, max_length=50)
    state_file_data: str
    
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Agent name cannot be empty or whitespace")
        return stripped
    
    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v: str) -> str:
        return PlatformRegistry.validate_platform(v).value
    
    @field_validator('predictor_version')
    @classmethod
    def validate_predictor_version(cls, v: str) -> str:
        supported_versions = list(PredictorRegistry._predictors.keys())
        if v not in supported_versions:
            raise UnsupportedPredictorVersionError(
                version=v,
                supported_versions=supported_versions
            )
        return v
    
    @field_validator('state_file_data')
    @classmethod
    def validate_state_file_data(cls, v: str) -> str:
        cls._validate_json_format(v)
        cls._validate_user_profile_schema(v)
        return v
    
    @staticmethod
    def _validate_json_format(v: str) -> None:
        try:
            json.loads(v)
        except json.JSONDecodeError as e:
            raise ValueError(f"state_file_data must be valid JSON: {str(e)}")
    
    @staticmethod
    def _validate_user_profile_schema(v: str) -> None:
        is_valid, error_message = UserProfileSchema.validate(v)
        if not is_valid:
            raise ValueError(f"Invalid user profile schema: {error_message}")

class AgentUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    platform: str | None = None
    predictor_version: str | None = Field(None, min_length=1, max_length=50)
    state: AgentState | None = None
    state_file_data: str | None = None
    
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return None
        
        stripped = v.strip()
        if not stripped:
            raise ValueError("Agent name cannot be empty or whitespace")
        return stripped
    
    @field_validator('platform')
    @classmethod
    def validate_platform(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return PlatformRegistry.validate_platform(v).value
    
    @field_validator('predictor_version')
    @classmethod
    def validate_predictor_version(cls, v: str | None) -> str | None:
        if v is None:
            return None
        
        supported_versions = list(PredictorRegistry._predictors.keys())
        if v not in supported_versions:
            raise UnsupportedPredictorVersionError(
                version=v,
                supported_versions=supported_versions
            )
        return v
    
    @field_validator('state')
    @classmethod
    def validate_state(cls, v: AgentState | None) -> AgentState | None:
        if v is None:
            return None
        
        valid_states = ["auditing", "offline", "banned"]
        if v not in valid_states:
            raise ValueError(
                f"Invalid agent state '{v}'. "
                f"Valid states: {', '.join(valid_states)}"
            )
        return v
    
    @field_validator('state_file_data')
    @classmethod
    def validate_state_file_data(cls, v: str | None) -> str | None:
        if v is None:
            return None
        
        cls._validate_json_format(v)
        cls._validate_user_profile_schema(v)
        return v
    
    @staticmethod
    def _validate_json_format(v: str) -> None:
        try:
            json.loads(v)
        except json.JSONDecodeError as e:
            raise ValueError(f"state_file_data must be valid JSON: {str(e)}")
    
    @staticmethod
    def _validate_user_profile_schema(v: str) -> None:
        is_valid, error_message = UserProfileSchema.validate(v)
        if not is_valid:
            raise ValueError(f"Invalid user profile schema: {error_message}")

class AgentResponse(BaseModel):
    id: UUID
    name: str
    platform: str
    state: AgentState
    predictor_version: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={UUID: str},
    )

class AgentListResponse(BaseModel):
    agents: list[AgentResponse] = Field(default_factory=list)
    total: int = Field(..., ge=0)
    
    model_config = ConfigDict(frozen=True)