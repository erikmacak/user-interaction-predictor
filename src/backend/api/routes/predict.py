from fastapi import APIRouter, HTTPException

from schemas.predict import (
    PredictActionsRequest,
    PredictActionsResponse,
    PredictedAction,
)
from services.video_parser import VideoParserService
from services.predictor.registry import PredictorRegistry

router = APIRouter()

@router.post(
    "/predict_actions",
    response_model=PredictActionsResponse,
)
def predict_actions(payload: PredictActionsRequest) -> PredictActionsResponse:
    try:
        video_source = VideoParserService.parse(str(payload.video_url))
        predictor = PredictorRegistry.get("v1")
        predicted_actions = predictor.predict(video_source)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return PredictActionsResponse(
        predicted_actions=[
            PredictedAction(action=action) for action in predicted_actions
        ]
    )
