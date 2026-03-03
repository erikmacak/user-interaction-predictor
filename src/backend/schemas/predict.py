from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

class VideoMetadata(BaseModel):
    video_id: str = Field(..., min_length=1)
    video_author: Optional[str] = None
    video_time_duration: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    hashtags: Optional[List[str]] = None
    likes_count: Optional[int] = Field(None, ge=0)
    comments_count: Optional[int] = Field(None, ge=0)
    reposts_count: Optional[int] = Field(None, ge=0)
    shares_count: Optional[int] = Field(None, ge=0)

class PredictActionsRequest(BaseModel):
    session_id: UUID
    video_metadata: VideoMetadata
    
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

class PredictActionsResponse(BaseModel):
    predicted_actions: List[str]