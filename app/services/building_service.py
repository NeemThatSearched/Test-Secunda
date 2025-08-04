from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List, Optional
from app.core.patterns import BaseService
from app.models.models import Building
from app.schemas.schemas import BuildingCreate


class BuildingService(BaseService):
    
    def get_model_class(self):
        return Building
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Building]:
        query = select(Building).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, building_id: int) -> Optional[Building]:
        query = select(Building).where(Building.id == building_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, building_data: BuildingCreate) -> Building:
        return await self.create_entity(building_data)
    
    async def _validate_creation_data(self, entity_data: BuildingCreate):
        if not (-90 <= entity_data.latitude <= 90):
            raise ValueError("Широта должна быть между -90 и 90")
        
        if not (-180 <= entity_data.longitude <= 180):
            raise ValueError("Долгота должна быть между -180 и 180")

    async def _build_entity(self, entity_data: BuildingCreate, **kwargs) -> Building:
        return Building(
            address=entity_data.address,
            latitude=entity_data.latitude,
            longitude=entity_data.longitude
        )

    async def find_by_address(self, address: str) -> List[Building]:
        query = select(Building).where(Building.address.ilike(f"%{address}%"))
        result = await self.db.execute(query)
        return result.scalars().all()