from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from app.core.patterns import (
    BaseService, SearchContext, GeographicSearchStrategy, 
    NameSearchStrategy, ActivitySearchStrategy
)
from app.models.models import Organization, Building, Activity, Phone
from app.schemas.schemas import OrganizationCreate, SearchArea
import math


class OrganizationService(BaseService):
    
    def get_model_class(self):
        return Organization
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        query = select(Organization).options(
            joinedload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities)
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().unique().all()

    async def get_by_id(self, organization_id: int) -> Optional[Organization]:
        query = select(Organization).options(
            joinedload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities)
        ).where(Organization.id == organization_id)
        
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, organization_data: OrganizationCreate) -> Organization:
        return await self.create_entity(organization_data)
    
    async def _validate_creation_data(self, entity_data: OrganizationCreate):
        building_query = select(Building).where(Building.id == entity_data.building_id)
        building_result = await self.db.execute(building_query)
        building = building_result.scalars().first()
        
        if not building:
            raise ValueError(f"Здание с id {entity_data.building_id} не найдено")
        
        for activity_id in entity_data.activity_ids:
            activity_query = select(Activity).where(Activity.id == activity_id)
            activity_result = await self.db.execute(activity_query)
            activity = activity_result.scalars().first()
            
            if not activity:
                raise ValueError(f"Активность с id {activity_id} не найдена")

    async def _build_entity(self, entity_data: OrganizationCreate, **kwargs) -> Organization:
        organization = Organization(
            name=entity_data.name,
            building_id=entity_data.building_id
        )
        
        for phone_number in entity_data.phone_numbers:
            phone_query = select(Phone).where(Phone.number == phone_number)
            phone_result = await self.db.execute(phone_query)
            phone = phone_result.scalars().first()
            
            if not phone:
                phone = Phone(number=phone_number)
                self.db.add(phone)
                await self.db.flush()
            
            organization.phones.append(phone)
        
        for activity_id in entity_data.activity_ids:
            activity_query = select(Activity).where(Activity.id == activity_id)
            activity_result = await self.db.execute(activity_query)
            activity = activity_result.scalars().first()
            
            if activity:
                organization.activities.append(activity)
        
        return organization

    async def _post_creation_hook(self, entity):
        await self.db.refresh(entity)
        return await self.get_by_id(entity.id)

    async def find_by_building(self, building_id: int) -> List[Organization]:
        query = select(Organization).options(
            joinedload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities)
        ).where(Organization.building_id == building_id)
        
        result = await self.db.execute(query)
        return result.scalars().unique().all()

    async def find_by_activity(self, activity_name: str) -> List[Organization]:
        strategy = ActivitySearchStrategy(self.db)
        search_context = SearchContext(strategy)
        return await search_context.search(activity_name=activity_name)

    async def find_by_name(self, name: str) -> List[Organization]:
        strategy = NameSearchStrategy(self.db)
        search_context = SearchContext(strategy)
        return await search_context.search(name=name)

    async def find_by_geographic_area(
        self, 
        latitude: float, 
        longitude: float, 
        radius: Optional[float] = None,
        min_latitude: Optional[float] = None,
        max_latitude: Optional[float] = None,
        min_longitude: Optional[float] = None,
        max_longitude: Optional[float] = None
    ) -> List[Organization]:
        strategy = GeographicSearchStrategy(self.db)
        search_context = SearchContext(strategy)
        
        return await search_context.search(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude
        )