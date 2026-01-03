from pydantic import BaseModel, HttpUrl

class PredictActionRequest(BaseModel):
    video_url: HttpUrl

class PredictActionResponse(BaseModel):
    platform: str
    video_id: str
    predicted_action: str