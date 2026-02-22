from fastapi import APIRouter, status

from schemas.predict import (
    PredictActionsRequest,
    PredictActionsResponse,
    PredictedAction,
)
from domain.video import VideoSource
from services.predictor.registry import PredictorRegistry
from core.settings import settings

router = APIRouter()

@router.post(
    "/predict_actions",
    response_model=PredictActionsResponse,
    status_code=status.HTTP_200_OK,
)
def predict_actions(payload: PredictActionsRequest) -> PredictActionsResponse:
    video_source = VideoSource(
        platform=payload.platform,
        video_id=payload.video_id,
    )
    predictor = PredictorRegistry.get(settings.PREDICTOR_VERSION)
    predicted_actions = predictor.predict(video_source)

    return PredictActionsResponse(
        predicted_actions=[
            PredictedAction(action=action) for action in predicted_actions
        ]
    )