from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings


class SingletonMeta(type):
    _instances: Dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseService(ABC):
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    @abstractmethod
    async def get_all(self, **kwargs):
        pass

    @abstractmethod
    async def get_by_id(self, id: int):
        pass

    @abstractmethod
    def get_model_class(self):
        pass

    async def create_entity(self, entity_data, **kwargs):
        await self._validate_creation_data(entity_data)
        entity = await self._build_entity(entity_data, **kwargs)
        await self._save_entity(entity)
        return await self._post_creation_hook(entity)

    async def _validate_creation_data(self, entity_data):
        pass

    @abstractmethod
    async def _build_entity(self, entity_data, **kwargs):
        pass

    async def _save_entity(self, entity):
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)

    async def _post_creation_hook(self, entity):
        return entity


class ServiceFactory(ABC):
    @abstractmethod
    def create_organization_service(self, db_session: AsyncSession):
        pass

    @abstractmethod
    def create_building_service(self, db_session: AsyncSession):
        pass

    @abstractmethod
    def create_activity_service(self, db_session: AsyncSession):
        pass


class SearchStrategy(ABC):
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    @abstractmethod
    async def execute_search(self, **kwargs):
        pass


class GeographicSearchStrategy(SearchStrategy):
    async def execute_search(self, latitude: float, longitude: float, 
                           radius: Optional[float] = None, 
                           min_latitude: Optional[float] = None,
                           max_latitude: Optional[float] = None,
                           min_longitude: Optional[float] = None,
                           max_longitude: Optional[float] = None, **kwargs):
        from app.models.models import Organization, Building
        from sqlalchemy.orm import joinedload, selectinload
        from sqlalchemy import select, func, and_
        
        query = select(Organization).options(
            joinedload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities)
        ).join(Organization.building)
        
        if radius is not None:
            distance_formula = func.sqrt(
                func.pow(Building.latitude - latitude, 2) + 
                func.pow(Building.longitude - longitude, 2)
            ) * 111.32
            query = query.where(distance_formula <= radius)
        else:
            conditions = []
            if min_latitude is not None:
                conditions.append(Building.latitude >= min_latitude)
            if max_latitude is not None:
                conditions.append(Building.latitude <= max_latitude)
            if min_longitude is not None:
                conditions.append(Building.longitude >= min_longitude)
            if max_longitude is not None:
                conditions.append(Building.longitude <= max_longitude)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        result = await self.db.execute(query)
        return result.scalars().unique().all()


class NameSearchStrategy(SearchStrategy):
    async def execute_search(self, name: str, **kwargs):
        from app.models.models import Organization
        from sqlalchemy.orm import joinedload, selectinload
        from sqlalchemy import select
        
        query = select(Organization).options(
            joinedload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities)
        ).where(Organization.name.ilike(f"%{name}%"))
        
        result = await self.db.execute(query)
        return result.scalars().unique().all()


class ActivitySearchStrategy(SearchStrategy):
    async def execute_search(self, activity_name: str, **kwargs):
        from app.models.models import Organization, Activity
        from sqlalchemy.orm import joinedload, selectinload
        from sqlalchemy import select
        
        activity_query = select(Activity).where(Activity.name.ilike(f"%{activity_name}%"))
        activity_result = await self.db.execute(activity_query)
        main_activity = activity_result.scalars().first()
        
        if not main_activity:
            return []

        activity_ids = await self._get_activity_hierarchy_ids(main_activity.id)
        
        query = select(Organization).options(
            joinedload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities)
        ).join(Organization.activities).where(Activity.id.in_(activity_ids))
        
        result = await self.db.execute(query)
        return result.scalars().unique().all()

    async def _get_activity_hierarchy_ids(self, activity_id: int) -> List[int]:
        from app.models.models import Activity
        from sqlalchemy import select
        
        activity_ids = [activity_id]
        
        children_query = select(Activity).where(Activity.parent_id == activity_id)
        children_result = await self.db.execute(children_query)
        children = children_result.scalars().all()
        
        for child in children:
            child_ids = await self._get_activity_hierarchy_ids(child.id)
            activity_ids.extend(child_ids)
        
        return activity_ids


class SearchContext:
    def __init__(self, strategy: SearchStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: SearchStrategy):
        self._strategy = strategy
    
    async def search(self, **kwargs):
        return await self._strategy.execute_search(**kwargs)