from fastapi import APIRouter, HTTPException
from schemas.predict import PredictActionRequest, PredictActionResponse
from services.video_parser import VideoParserService

router = APIRouter()

@router.post(
    "/predict_action",
    response_model=PredictActionResponse,
)
def predict_action(payload: PredictActionRequest) -> PredictActionResponse:
    try:
        video_source = VideoParserService.parse(str(payload.video_url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    predicted_action = "like"

    return PredictActionResponse(
        platform=video_source.platform,
        video_id=video_source.video_id,
        predicted_action=predicted_action,
    )