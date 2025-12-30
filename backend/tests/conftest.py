"""
pytest configuration and fixtures for CACI Mission Intake Copilot.
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import app and database components
import sys
sys.path.insert(0, '.')

from main import app
from db.database import Base
from db import get_session


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh test database for each test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden database dependency."""
    
    async def override_get_session():
        yield test_db
    
    app.dependency_overrides[get_session] = override_get_session
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_csv_content() -> bytes:
    """Sample CSV content for testing."""
    return b"""threat_id,threat_name,category,severity
THR-001,APT Alpha,Cyber,Critical
THR-002,Supply Chain,Logistics,High
THR-003,Insider Threat,Personnel,Medium"""


@pytest.fixture
def sample_txt_content() -> bytes:
    """Sample TXT content for testing."""
    return b"""ANALYST NOTES - Operation Phoenix
Date: January 28, 2024
Classification: UNCLASSIFIED

Executive Summary:
The target network shows signs of increased activity. 
Recommend continued monitoring and analysis."""


@pytest.fixture
def sample_text_submission() -> dict:
    """Sample text submission for testing."""
    return {
        "content": "This is a test mission for QA purposes. Key stakeholders include the project manager.",
        "source_label": "Test Mission Notes"
    }
