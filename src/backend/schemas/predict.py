from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class VideoMetadata(BaseModel):
    video_id: str = Field(..., min_length=1)
    video_author: str | None = None
    video_time_duration: int | None = Field(None, ge=0)
    description: str | None = None
    hashtags: list[str] | None = None
    likes_count: int | None = Field(None, ge=0)
    comments_count: int | None = Field(None, ge=0)
    reposts_count: int | None = Field(None, ge=0)
    shares_count: int | None = Field(None, ge=0)
    
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

class PredictActionsRequest(BaseModel):
    session_id: UUID
    video_metadata: VideoMetadata
    
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

class PredictActionsResponse(BaseModel):
    predicted_actions: list[str] = Field(default_factory=list)
    
    model_config = ConfigDict(frozen=True)