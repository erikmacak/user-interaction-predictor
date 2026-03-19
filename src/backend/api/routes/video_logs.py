from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from io import BytesIO
from datetime import datetime

from core.database import get_db
from services.video_log_service import VideoLogService
from api.deps import get_current_user
from domain.models.user import User
from domain.models.audit_session import AuditSession

router = APIRouter()

@router.get("/agents/{agent_id}/sessions")
async def get_agent_sessions(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    result = await db.execute(
        select(AuditSession)
        .where(AuditSession.agent_id == agent_id)
        .order_by(AuditSession.started_at.desc())
    )
    sessions = result.scalars().all()
    
    sessions_data = []
    for session in sessions:
        logs = await VideoLogService.get_logs_by_session(db, session.id)
        
        sessions_data.append({
            "session_id": str(session.id),
            "date": session.started_at.strftime("%Y-%m-%d") if session.started_at else "Unknown",
            "video_count": len(logs),
        })
    
    return sessions_data

@router.get("/agents/{agent_id}/sessions/{session_id}/export")
async def export_session_data(
    agent_id: UUID,
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    result = await db.execute(
        select(AuditSession).where(
            AuditSession.id == session_id,
            AuditSession.agent_id == agent_id
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    logs = await VideoLogService.get_logs_by_session(db, session_id)
    
    if not logs:
        raise HTTPException(status_code=404, detail="No data found for this session")
    
    csv_content = VideoLogService.export_to_csv(logs)
    
    date_str = session.started_at.strftime("%Y%m%d") if session.started_at else "unknown"
    
    return StreamingResponse(
        BytesIO(csv_content.encode('utf-8')),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=session_{date_str}_data.csv"
        }
    )

@router.get("/agents/{agent_id}/export")
async def export_all_agent_data(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):  
    logs = await VideoLogService.get_logs_by_agent(db, agent_id)
    
    if not logs:
        raise HTTPException(status_code=404, detail="No data found for this agent")
    
    csv_content = VideoLogService.export_to_csv(logs)
    
    return StreamingResponse(
        BytesIO(csv_content.encode('utf-8')),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=agent_{agent_id}_all_data.csv"
        }
    )