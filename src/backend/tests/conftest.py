import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from core.database import Base, get_db
from core.security import get_password_hash
from domain.models.user import User
from main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()

@pytest.fixture(scope="function")
def client(db_session):
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
async def admin_user(db_session: AsyncSession):
    user = User(
        username="admin",
        password_hash=get_password_hash("TestPassword123!"),
        must_change_password=False
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user

@pytest.fixture
def authenticated_client(client, admin_user):
    response = client.post(
        "/api/auth/login",
        json={"password": "TestPassword123!"}
    )
    
    assert response.status_code == 200
    return client

@pytest.fixture
def valid_user_profile():
    return {
        "user_profile": {
            "user_email": "test@example.com",
            "gender": "male",
            "country_code": "us",
            "date_of_birth": "15.03.1998",
            "favorite_authors": ["author1", "author2"],
            "retention_triggers": {
                "preferred_emotions": ["curiosity", "amusement", "surprise"],
                "preferred_languages": ["en"],
                "interest_topics": ["technology", "coding", "ai"]
            }
        }
    }