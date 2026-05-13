import sys
import os
from pathlib import Path
from unittest.mock import patch

# Добавляем корневую папку backend в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.vm import VirtualMachine
from app.core.security import get_password_hash

# Тестовая БД (SQLite для быстрых тестов)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool
)

TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# Мок для Celery (отключаем отправку писем при тестах)
@pytest.fixture(autouse=True)
def mock_celery():
    with patch('app.tasks.email_tasks.send_activation_email.delay') as mock:
        mock.return_value = None
        yield mock

@pytest.fixture(autouse=True)
async def setup_database():
    """Создание таблиц перед каждым тестом"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client() -> AsyncGenerator:
    """HTTP клиент для тестов"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def test_user(db: AsyncSession):
    """Создание тестового пользователя"""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("test123"),
        is_active=False
    )
    user.generate_activation_key()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@pytest.fixture
async def test_vm(db: AsyncSession):
    """Создание тестовой виртуальной машины"""
    vm = VirtualMachine(
        name="test-proxy-1",
        host="185.244.35.67",
        port=1080,
        protocol="socks5",
        is_active=True,
        current_user_id=None
    )
    db.add(vm)
    await db.commit()
    await db.refresh(vm)
    return vm

@pytest.fixture
async def db() -> AsyncGenerator:
    """Сессия БД"""
    async with TestingSessionLocal() as session:
        yield session