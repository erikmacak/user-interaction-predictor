from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from uuid import UUID

from domain.models.agent import Agent
from schemas.agent import AgentCreateRequest, AgentUpdateRequest
from domain.errors import AgentAlreadyExistsError, AgentNotFoundError, AgentIsAuditingError

class AgentService:
    
    @staticmethod
    async def create_agent(db: AsyncSession, data: AgentCreateRequest) -> Agent:
        agent = Agent(
            name=data.name,
            platform=data.platform,
            state="offline",
            predictor_version=data.predictor_version,
            state_file_data=data.state_file_data,
        )
        
        try:
            db.add(agent)
            await db.flush()
            await db.refresh(agent)
            return agent
        except IntegrityError:
            await db.rollback()
            raise AgentAlreadyExistsError(data.name)
    
    @staticmethod
    async def get_agent(db: AsyncSession, agent_id: UUID) -> Agent:
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise AgentNotFoundError(str(agent_id))
        
        return agent
    
    @staticmethod
    async def list_agents(
        db: AsyncSession, 
        state: Optional[str] = None
    ) -> List[Agent]:
        query = select(Agent)
        
        if state:
            query = query.where(Agent.state == state)
        
        query = query.order_by(Agent.created_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_agent(
        db: AsyncSession, 
        agent_id: UUID, 
        data: AgentUpdateRequest
    ) -> Agent:
        agent = await AgentService.get_agent(db, agent_id)

        if agent.state == "auditing":
            raise AgentIsAuditingError(agent.name)
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        try:
            await db.flush()
            await db.refresh(agent)
            return agent
        except IntegrityError:
            await db.rollback()
            raise AgentAlreadyExistsError(agent.name)
    
    @staticmethod
    async def delete_agent(db: AsyncSession, agent_id: UUID) -> None:
        agent = await AgentService.get_agent(db, agent_id)

        if agent.state == "auditing":
            raise AgentIsAuditingError(agent.name)

        await db.delete(agent)
        await db.flush()
    
    @staticmethod
    async def get_total_count(db: AsyncSession, state: Optional[str] = None) -> int:
        query = select(func.count(Agent.id))
        
        if state:
            query = query.where(Agent.state == state)
        
        result = await db.execute(query)
        return result.scalar_one()