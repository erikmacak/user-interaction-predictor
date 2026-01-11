from typing import List
from pydantic import BaseModel, HttpUrl

from domain.action import PredictedActionType

class PredictActionsRequest(BaseModel):
    video_url: HttpUrl

class PredictedAction(BaseModel):
    action: PredictedActionType

class PredictActionsResponse(BaseModel):
    predicted_actions: List[PredictedAction]