from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from domain.models.audit_session import AuditSession
from schemas.predict import (
    PredictActionsRequest,
    PredictActionsResponse,
)
from domain.video import VideoSource, VideoPlatform
from services.predictor.registry import PredictorRegistry
from services.agent_service import AgentService
from domain.errors import SessionNotFoundError, SessionNotRunningError

router = APIRouter()

@router.post(
    "/predict_actions",
    response_model=PredictActionsResponse,
    status_code=status.HTTP_200_OK,
)
async def predict_actions(
    payload: PredictActionsRequest,
    db: AsyncSession = Depends(get_db),
) -> PredictActionsResponse:
    result = await db.execute(
        select(AuditSession).where(AuditSession.id == payload.session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise SessionNotFoundError(str(payload.session_id))
    
    if session.state != "running":
        raise SessionNotRunningError(str(payload.session_id))
    
    agent = await AgentService.get_agent(db, session.agent_id)
    
    video_source = VideoSource(
        platform=VideoPlatform(agent.platform),
        video_id=payload.video_metadata.video_id,
    )
    
    predictor = PredictorRegistry.get(agent.predictor_version)
    
    if agent.predictor_version == "v2":
        predicted_actions = await predictor.predict_with_context(
            video_source=video_source,
            video_metadata=payload.video_metadata,
            user_state_json=agent.state_file_data,
            db=db,
            session_id=payload.session_id,
            agent_id=session.agent_id,
        )
    else:
        predicted_actions = predictor.predict(video_source)

    return PredictActionsResponse(
        predicted_actions=predicted_actions
    )