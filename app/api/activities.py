from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.api.dependencies import get_db, get_service_factory
from app.core.security import verify_api_key
from app.schemas.schemas import Activity, ActivityCreate, ActivityWithChildren
from app.services.service_factory import ConcreteServiceFactory

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/", response_model=List[Activity])
async def get_activities(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    """Получить список всех видов деятельности"""
    service = factory.create_activity_service(db)
    activities = await service.get_all(skip=skip, limit=limit)
    return activities


@router.get("/root", response_model=List[ActivityWithChildren])
async def get_root_activities(
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    """Получить корневые виды деятельности (первый уровень)"""
    service = factory.create_activity_service(db)
    activities = await service.get_root_activities()
    return activities


@router.get("/{activity_id}", response_model=Activity)
async def get_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    """Получить информацию о виде деятельности по ID"""
    service = factory.create_activity_service(db)
    activity = await service.get_by_id(activity_id)
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    return activity


@router.get("/{activity_id}/tree", response_model=ActivityWithChildren)
async def get_activity_tree(
    activity_id: int,
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    """Получить дерево деятельности начиная с указанного узла"""
    service = factory.create_activity_service(db)
    activity = await service.get_activity_tree(activity_id)
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    return activity


@router.get("/search/name", response_model=List[Activity])
async def search_activities_by_name(
    name: str = Query(..., description="Поисковый запрос по названию"),
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    """Поиск видов деятельности по названию"""
    service = factory.create_activity_service(db)
    activities = await service.find_by_name(name)
    return activities


@router.post("/", response_model=Activity)
async def create_activity(
    activity: ActivityCreate,
    db: AsyncSession = Depends(get_db),
    factory: ConcreteServiceFactory = Depends(get_service_factory),
    api_key: str = Depends(verify_api_key)
):
    """Создать новый вид деятельности"""
    try:
        service = factory.create_activity_service(db)
        return await service.create(activity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))