from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user_if_password_changed
from core.database import get_db
from domain.models.user import User
from schemas.audit_session import (
    AuditSessionListResponse,
    AuditSessionResponse,
    AuditSessionStartRequest,
)
from schemas.common import SuccessResponse
from services.audit_session_service import AuditSessionService

router = APIRouter()

@router.post(
    "/sessions",
    response_model=AuditSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_session(
    data: AuditSessionStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_if_password_changed),
) -> AuditSessionResponse:
    session = await AuditSessionService.start_session(db, data.agent_id)
    
    sessions = await AuditSessionService.list_running_sessions(db)
    session_response = next(s for s in sessions if str(s.id) == str(session.id))
    
    return session_response

@router.get("/sessions/running", response_model=AuditSessionListResponse)
async def list_running_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_if_password_changed),
) -> AuditSessionListResponse:
    sessions = await AuditSessionService.list_running_sessions(db)
    total = await AuditSessionService.get_running_sessions_count(db)
    
    return AuditSessionListResponse(
        sessions=sessions,
        total=total,
    )

@router.post("/sessions/{session_id}/stop", response_model=SuccessResponse)
async def stop_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_if_password_changed),
) -> SuccessResponse:
    await AuditSessionService.stop_session(db, session_id)
    return SuccessResponse(message="Session stopped successfully")