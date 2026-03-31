from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.models.audit_session import AuditSession
from domain.models.agent import Agent
from schemas.audit_session import AuditSessionResponse
from services.agent_service import AgentService
from domain.errors import (
    AgentAlreadyAuditingError,
    AgentNotAuditingError,
    SessionNotFoundError,
    SessionAlreadyCompletedError,
)

class AuditSessionService:    
    AUDITING_STATE = "auditing"
    OFFLINE_STATE = "offline"
    BANNED_STATE = "banned"
    RUNNING_STATE = "running"
    COMPLETED_STATE = "completed"
    
    @staticmethod
    async def start_session(
        db: AsyncSession,
        agent_id: UUID
    ) -> AuditSession:
        agent = await AgentService.get_agent(db, agent_id)
        
        AuditSessionService._validate_can_start_session(agent)
        
        agent.state = AuditSessionService.AUDITING_STATE
        
        session = AuditSession(
            agent_id=agent.id,
            state=AuditSessionService.RUNNING_STATE,
        )
        
        db.add(session)
        await db.flush()
        await db.refresh(session)
        await db.refresh(agent)
        
        return session
    
    @staticmethod
    async def stop_session(db: AsyncSession, session_id: UUID) -> AuditSession:
        session = await AuditSessionService._get_session(db, session_id)
        
        AuditSessionService._validate_session_running(session)
        
        agent = await AgentService.get_agent(db, session.agent_id)
        
        AuditSessionService._complete_session(session, agent)
        
        await db.flush()
        await db.refresh(session)
        await db.refresh(agent)
        
        return session
    
    @staticmethod
    async def list_running_sessions(db: AsyncSession) -> list[AuditSessionResponse]:
        result = await db.execute(
            select(AuditSession, Agent)
            .join(Agent, AuditSession.agent_id == Agent.id)
            .where(AuditSession.state == AuditSessionService.RUNNING_STATE)
            .order_by(AuditSession.started_at.desc())
        )
        
        return [
            AuditSessionService._build_session_response(session, agent)
            for session, agent in result.all()
        ]
    
    @staticmethod
    async def get_running_sessions_count(db: AsyncSession) -> int:
        result = await db.execute(
            select(AuditSession)
            .where(AuditSession.state == AuditSessionService.RUNNING_STATE)
        )
        return len(result.scalars().all())
    
    @staticmethod
    async def _get_session(db: AsyncSession, session_id: UUID) -> AuditSession:
        result = await db.execute(
            select(AuditSession).where(AuditSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise SessionNotFoundError(str(session_id))
        
        return session
    
    @staticmethod
    def _validate_can_start_session(agent: Agent) -> None:
        if agent.state == AuditSessionService.AUDITING_STATE:
            raise AgentAlreadyAuditingError(agent.name)
        
        if agent.state == AuditSessionService.BANNED_STATE:
            raise AgentNotAuditingError(agent.name)
    
    @staticmethod
    def _validate_session_running(session: AuditSession) -> None:
        if session.state == AuditSessionService.COMPLETED_STATE:
            raise SessionAlreadyCompletedError(str(session.id))
    
    @staticmethod
    def _complete_session(session: AuditSession, agent: Agent) -> None:
        session.state = AuditSessionService.COMPLETED_STATE
        session.ended_at = datetime.now(timezone.utc)
        agent.state = AuditSessionService.OFFLINE_STATE
    
    @staticmethod
    def _build_session_response(
        session: AuditSession,
        agent: Agent
    ) -> AuditSessionResponse:
        return AuditSessionResponse(
            id=session.id,
            agent_id=session.agent_id,
            agent_name=agent.name,
            agent_platform=agent.platform,
            state=session.state,
            started_at=session.started_at,
            ended_at=session.ended_at,
        )