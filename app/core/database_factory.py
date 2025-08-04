from abc import ABC, abstractmethod
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.patterns import SingletonMeta


class DatabaseFactory(ABC):
    """Абс фабрика для работы с базами данных"""
    
    @abstractmethod
    def get_database_url(self) -> str:
        pass
    
    @abstractmethod
    def get_engine_kwargs(self) -> dict:
        pass


class PostgreSQLFactory(DatabaseFactory):
    """Фабрика для PostgreSQL"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
    
    def get_database_url(self) -> str:
        return self.database_url
    
    def get_engine_kwargs(self) -> dict:
        return {
            "echo": False,
            "pool_size": 20,
            "max_overflow": 0,
            "pool_pre_ping": True
        }





class DatabaseManager(metaclass=SingletonMeta):
    """Singleton менеджер базы данных с поддержкой разных БД через фабрики"""
    
    def __init__(self, factory: DatabaseFactory = None):
        if not hasattr(self, '_initialized'):
            self._factory = factory
            self._engine = None
            self._session_factory = None
            self._initialized = True

    def set_factory(self, factory: DatabaseFactory):
        """Установить фабрику БД"""
        self._factory = factory
        self._engine = None
        self._session_factory = None

    @property
    def engine(self):
        if self._engine is None:
            if self._factory is None:
                raise ValueError("Database factory not set")
            
            database_url = self._factory.get_database_url()
            engine_kwargs = self._factory.get_engine_kwargs()
            self._engine = create_async_engine(database_url, **engine_kwargs)
        return self._engine

    @property
    def session_factory(self):
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        return self._session_factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session