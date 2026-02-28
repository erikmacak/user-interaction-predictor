from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from core.database import get_db
from api.deps import get_current_user_if_password_changed
from domain.models.user import User
from schemas.audit_session import (
    AuditSessionStartRequest,
    AuditSessionResponse,
    AuditSessionListResponse,
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
):
    session = await AuditSessionService.start_session(db, data)
    
    sessions = await AuditSessionService.list_running_sessions(db)
    session_response = next(s for s in sessions if str(s.id) == str(session.id))
    
    return session_response

@router.get("/sessions/running", response_model=AuditSessionListResponse)
async def list_running_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_if_password_changed),
):
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
):
    await AuditSessionService.stop_session(db, session_id)
    return SuccessResponse(message="Session stopped successfully")