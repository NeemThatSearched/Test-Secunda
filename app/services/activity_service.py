from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from typing import List, Optional
from app.core.patterns import BaseService
from app.models.models import Activity
from app.schemas.schemas import ActivityCreate
from app.core.config import get_settings


class ActivityService(BaseService):
    
    def get_model_class(self):
        return Activity
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Activity]:
        query = select(Activity).options(
            selectinload(Activity.children)
        ).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().unique().all()

    async def get_by_id(self, activity_id: int) -> Optional[Activity]:
        query = select(Activity).options(
            selectinload(Activity.children),
            selectinload(Activity.parent),
            selectinload(Activity.organizations)
        ).where(Activity.id == activity_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, activity_data: ActivityCreate) -> Activity:
        return await self.create_entity(activity_data)
    
    async def _validate_creation_data(self, entity_data: ActivityCreate):
        if entity_data.parent_id:
            parent_query = select(Activity).where(Activity.id == entity_data.parent_id)
            parent_result = await self.db.execute(parent_query)
            parent = parent_result.scalars().first()
            
            if not parent:
                raise ValueError("Родительская активность не найдена")
            
            level = parent.level + 1
            settings = get_settings()
            if level > settings.max_activity_depth:
                raise ValueError(f"Превышена максимальная глубина активности ({settings.max_activity_depth})")

    async def _build_entity(self, entity_data: ActivityCreate, **kwargs) -> Activity:
        level = 1
        
        if entity_data.parent_id:
            parent_query = select(Activity).where(Activity.id == entity_data.parent_id)
            parent_result = await self.db.execute(parent_query)
            parent = parent_result.scalars().first()
            level = parent.level + 1
        
        return Activity(
            name=entity_data.name,
            parent_id=entity_data.parent_id,
            level=level
        )

    async def get_root_activities(self) -> List[Activity]:
        query = select(Activity).options(
            selectinload(Activity.children)
        ).where(Activity.parent_id.is_(None))
        result = await self.db.execute(query)
        return result.scalars().unique().all()

    async def get_activity_tree(self, activity_id: int) -> Optional[Activity]:
        activity = await self.get_by_id(activity_id)
        if not activity:
            return None
        
        await self._load_children_recursively(activity)
        return activity

    async def _load_children_recursively(self, activity: Activity):
        for child in activity.children:
            child_query = select(Activity).options(
                selectinload(Activity.children)
            ).where(Activity.id == child.id)
            child_result = await self.db.execute(child_query)
            loaded_child = child_result.scalars().first()
            
            if loaded_child and loaded_child.children:
                await self._load_children_recursively(loaded_child)

    async def find_by_name(self, name: str) -> List[Activity]:
        query = select(Activity).options(
            selectinload(Activity.children),
            selectinload(Activity.parent)
        ).where(Activity.name.ilike(f"%{name}%"))
        result = await self.db.execute(query)
        return result.scalars().unique().all()