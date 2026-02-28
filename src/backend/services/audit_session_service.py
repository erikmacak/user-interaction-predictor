from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from datetime import datetime

from domain.models.audit_session import AuditSession
from domain.models.agent import Agent
from schemas.audit_session import AuditSessionStartRequest, AuditSessionResponse
from services.agent_service import AgentService
from domain.errors import (
    AgentAlreadyAuditingError,
    AgentNotAuditingError,
    SessionNotFoundError,
    SessionAlreadyCompletedError,
)

class AuditSessionService:
    
    @staticmethod
    async def start_session(db: AsyncSession, data: AuditSessionStartRequest) -> AuditSession:
        agent = await AgentService.get_agent(db, data.agent_id)
        
        if agent.state == "auditing":
            raise AgentAlreadyAuditingError(agent.name)
        
        if agent.state == "banned":
            raise AgentNotAuditingError(agent.name)
        
        agent.state = "auditing"
        
        session = AuditSession(
            agent_id=agent.id,
            state="running",
        )
        
        db.add(session)
        await db.flush()
        await db.refresh(session)
        await db.refresh(agent)
        
        return session
    
    @staticmethod
    async def stop_session(db: AsyncSession, session_id: UUID) -> AuditSession:
        result = await db.execute(
            select(AuditSession).where(AuditSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise SessionNotFoundError(str(session_id))
        
        if session.state == "completed":
            raise SessionAlreadyCompletedError(str(session_id))
        
        agent = await AgentService.get_agent(db, session.agent_id)
        
        session.state = "completed"
        session.ended_at = datetime.utcnow()
        
        agent.state = "offline"
        
        await db.flush()
        await db.refresh(session)
        await db.refresh(agent)
        
        return session
    
    @staticmethod
    async def list_running_sessions(db: AsyncSession) -> List[AuditSessionResponse]:
        result = await db.execute(
            select(AuditSession, Agent)
            .join(Agent, AuditSession.agent_id == Agent.id)
            .where(AuditSession.state == "running")
            .order_by(AuditSession.started_at.desc())
        )
        
        sessions_data = []
        for session, agent in result.all():
            sessions_data.append(
                AuditSessionResponse(
                    id=session.id,
                    agent_id=session.agent_id,
                    agent_name=agent.name,
                    agent_platform=agent.platform,
                    state=session.state,
                    started_at=session.started_at,
                    ended_at=session.ended_at,
                )
            )
        
        return sessions_data
    
    @staticmethod
    async def get_running_sessions_count(db: AsyncSession) -> int:
        result = await db.execute(
            select(AuditSession)
            .where(AuditSession.state == "running")
        )
        return len(result.scalars().all())