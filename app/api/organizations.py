from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.api.dependencies import get_db, get_service_factory
from app.core.security import verify_api_key
from app.schemas.schemas import (
    Organization, OrganizationCreate, OrganizationList, 
    SearchArea, PaginationParams, ApiResponse
)
from app.services.service_factory import ConcreteServiceFactory

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/", response_model=List[OrganizationList])
async def get_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    service = factory.create_organization_service(db)
    organizations = await service.get_all(skip=skip, limit=limit)
    return organizations


@router.get("/{organization_id}", response_model=Organization)
async def get_organization(
    organization_id: int,
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    service = factory.create_organization_service(db)
    organization = await service.get_by_id(organization_id)
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return organization


@router.get("/building/{building_id}", response_model=List[OrganizationList])
async def get_organizations_by_building(
    building_id: int,
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    """Получить список организаций в конкретном здании"""
    service = factory.create_organization_service(db)
    organizations = await service.find_by_building(building_id)
    return organizations


@router.get("/activity/{activity_name}", response_model=List[OrganizationList])
async def get_organizations_by_activity(
    activity_name: str,
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    """Получить список организаций по виду деятельности (включая иерархию)"""
    service = factory.create_organization_service(db)
    organizations = await service.find_by_activity(activity_name)
    return organizations


@router.get("/search/name", response_model=List[OrganizationList])
async def search_organizations_by_name(
    name: str = Query(..., description="Поисковый запрос по названию"),
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    """Поиск организаций по названию"""
    service = factory.create_organization_service(db)
    organizations = await service.find_by_name(name)
    return organizations


@router.post("/search/geographic", response_model=List[OrganizationList])
async def search_organizations_by_geographic_area(
    latitude: float = Query(..., ge=-90, le=90, description="Широта центра поиска"),
    longitude: float = Query(..., ge=-180, le=180, description="Долгота центра поиска"),
    radius: Optional[float] = Query(None, gt=0, description="Радиус поиска в километрах"),
    min_latitude: Optional[float] = Query(None, ge=-90, le=90, description="Минимальная широта"),
    max_latitude: Optional[float] = Query(None, ge=-90, le=90, description="Максимальная широта"),
    min_longitude: Optional[float] = Query(None, ge=-180, le=180, description="Минимальная долгота"),
    max_longitude: Optional[float] = Query(None, ge=-180, le=180, description="Максимальная долгота"),
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    """Поиск организаций в заданном радиусе или прямоугольной области"""
    service = factory.create_organization_service(db)
    organizations = await service.find_by_geographic_area(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        min_latitude=min_latitude,
        max_latitude=max_latitude,
        min_longitude=min_longitude,
        max_longitude=max_longitude
    )
    return organizations


@router.post("/", response_model=Organization)
async def create_organization(
    organization: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    service = factory.create_organization_service(db)
    try:
        return await service.create(organization)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))