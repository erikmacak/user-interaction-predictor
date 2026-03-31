from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO

from core.database import get_db
from services.video_log_service import VideoLogService
from api.deps import get_current_user
from domain.models.user import User

router = APIRouter()

@router.get("/agents/{agent_id}/sessions")
async def get_agent_sessions(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions_data = await VideoLogService.get_agent_sessions_summary(db, agent_id)
    return sessions_data

@router.get("/agents/{agent_id}/sessions/{session_id}/export")
async def export_session_data(
    agent_id: UUID,
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    csv_content = await VideoLogService.export_session_to_csv(db, session_id, agent_id)
    filename = await VideoLogService.generate_session_filename(db, session_id)
    
    return StreamingResponse(
        BytesIO(csv_content.encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/agents/{agent_id}/export")
async def export_all_agent_data(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    csv_content = await VideoLogService.export_agent_to_csv(db, agent_id)
    
    return StreamingResponse(
        BytesIO(csv_content.encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=agent_{agent_id}_all_data.csv"}
    )