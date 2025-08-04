from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api.dependencies import get_db, get_service_factory
from app.core.security import verify_api_key
from app.schemas.schemas import Building, BuildingCreate
from app.services.service_factory import ConcreteServiceFactory

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("/", response_model=List[Building])
async def get_buildings(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    """Получить список всех зданий"""
    service = factory.create_building_service(db)
    buildings = await service.get_all(skip=skip, limit=limit)
    return buildings


@router.get("/{building_id}", response_model=Building)
async def get_building(
    building_id: int,
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    """Получить информацию о здании по ID"""
    service = factory.create_building_service(db)
    building = await service.get_by_id(building_id)
    
    if not building:
        raise HTTPException(status_code=404, detail="Здание не найдено")
    
    return building


@router.get("/search/address", response_model=List[Building])
async def search_buildings_by_address(
    address: str = Query(..., description="Поисковый запрос по адресу"),
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    """Поиск зданий по адресу"""
    service = factory.create_building_service(db)
    buildings = await service.find_by_address(address)
    return buildings


@router.post("/", response_model=Building)
async def create_building(
    building: BuildingCreate,
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    service = factory.create_building_service(db)
    try:
        return await service.create(building)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))