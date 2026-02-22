from typing import List
from pydantic import BaseModel, ConfigDict, Field

from domain.video import VideoPlatform
from domain.action import PredictedActionType

class PredictActionsRequest(BaseModel):
    platform: VideoPlatform = Field(..., description="Social media platform")
    video_id: str = Field(..., min_length=1, description="Platform-specific video identifier")

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

class PredictedAction(BaseModel):
    action: PredictedActionType

class PredictActionsResponse(BaseModel):
    predicted_actions: List[PredictedAction]