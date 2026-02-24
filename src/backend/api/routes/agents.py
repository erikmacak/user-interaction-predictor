from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from core.database import get_db
from api.deps import get_current_user_if_password_changed
from domain.models.user import User
from schemas.agent import (
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentResponse,
    AgentListResponse,
    AgentState,
)
from schemas.common import SuccessResponse
from services.agent_service import AgentService
from services.predictor.registry import PredictorRegistry

router = APIRouter()

@router.get("/predictor-versions")
async def get_predictor_versions(
    current_user: User = Depends(get_current_user_if_password_changed),
):
    return {"versions": list(PredictorRegistry._predictors.keys())}

@router.post(
    "/agents",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_agent(
    data: AgentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_if_password_changed),
):
    agent = await AgentService.create_agent(db, data)
    return agent

@router.get("/agents", response_model=AgentListResponse)
async def list_agents(
    state: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_if_password_changed),
):
    agents = await AgentService.list_agents(db, state=state)
    total = await AgentService.get_total_count(db, state=state)
    
    return AgentListResponse(
        agents=agents,
        total=total,
    )

@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_if_password_changed),
):
    agent = await AgentService.get_agent(db, agent_id)
    return agent

@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    data: AgentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_if_password_changed),
):
    agent = await AgentService.update_agent(db, agent_id, data)
    return agent

@router.delete("/agents/{agent_id}", response_model=SuccessResponse)
async def delete_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_if_password_changed),
):
    await AgentService.delete_agent(db, agent_id)
    return SuccessResponse(message="Agent deleted successfully")