from fastapi import Depends
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database_factory import DatabaseManager, PostgreSQLFactory
from app.services.service_factory import ConcreteServiceFactory
from app.core.config import get_settings
import os

_db_manager = None
_service_factory = None


def get_database_manager() -> DatabaseManager:
    """Получение Singleton экземпляра DatabaseManager с фабрикой БД"""
    global _db_manager
    if _db_manager is None:
        settings = get_settings()
        factory = PostgreSQLFactory(settings.database_url)
        
        _db_manager = DatabaseManager(factory)
    return _db_manager


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии базы данных через Singleton"""
    db_manager = get_database_manager()
    async for session in db_manager.get_session():
        yield session


def get_service_factory() -> ConcreteServiceFactory:
    """Получение Singleton экземпляра фабрики сервисов"""
    global _service_factory
    if _service_factory is None:
        _service_factory = ConcreteServiceFactory()
    return _service_factory