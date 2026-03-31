from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user_if_password_changed
from core.database import get_db
from domain.models.user import User
from domain.platform import PlatformRegistry
from schemas.agent import (
    AgentCreateRequest,
    AgentListResponse,
    AgentResponse,
    AgentUpdateRequest,
)
from schemas.common import SuccessResponse
from services.agent_service import AgentService
from services.predictor.registry import PredictorRegistry

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.get("/platforms")
async def get_platforms(
    current_user: User = Depends(get_current_user_if_password_changed),
) -> dict[str, list[str]]:
    return {"platforms": PlatformRegistry.get_supported_platforms()}

@router.get("/predictor-versions")
async def get_predictor_versions(
    current_user: User = Depends(get_current_user_if_password_changed),
) -> dict[str, list[str]]:
    return {"versions": list(PredictorRegistry.get_supported_versions())}

@router.post(
    "/agents",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_agent(
    data: AgentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_if_password_changed),
) -> AgentResponse:
    agent = await AgentService.create_agent(db, data)
    return agent

@router.get("/agents", response_model=AgentListResponse)
async def list_agents(
    state: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_if_password_changed),
) -> AgentListResponse:
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
) -> AgentResponse:
    agent = await AgentService.get_agent(db, agent_id)
    return agent

@router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    data: AgentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_if_password_changed),
) -> AgentResponse:
    agent = await AgentService.update_agent(db, agent_id, data)
    return agent

@router.delete("/agents/{agent_id}", response_model=SuccessResponse)
@limiter.limit("5/minute")
async def delete_agent(
    request: Request,
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_if_password_changed),
) -> SuccessResponse:
    await AgentService.delete_agent(db, agent_id)
    return SuccessResponse(message="Agent deleted successfully")