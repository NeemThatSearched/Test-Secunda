from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from enum import Enum


class PhoneBase(BaseModel):
    number: str = Field(..., max_length=20, description="Номер телефона")


class PhoneCreate(PhoneBase):
    pass


class Phone(PhoneBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class BuildingBase(BaseModel):
    address: str = Field(..., max_length=500, description="Адрес здания")
    latitude: float = Field(..., ge=-90, le=90, description="Широта")
    longitude: float = Field(..., ge=-180, le=180, description="Долгота")


class BuildingCreate(BuildingBase):
    pass


class Building(BuildingBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int


class ActivityBase(BaseModel):
    name: str = Field(..., max_length=200, description="Название деятельности")


class ActivityCreate(ActivityBase):
    parent_id: Optional[int] = Field(None, description="ID родительской деятельности")


class Activity(ActivityBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    parent_id: Optional[int] = None
    level: int


class OrganizationBase(BaseModel):
    name: str = Field(..., max_length=300, description="Название организации")


class OrganizationCreate(OrganizationBase):
    building_id: int = Field(..., description="ID здания")
    phone_numbers: List[str] = Field(default=[], description="Номера телефонов")
    activity_ids: List[int] = Field(default=[], description="ID видов деятельности")


class Organization(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    building_id: int
    building: Building
    phones: List[Phone] = []
    activities: List[Activity] = []


class ActivityWithChildren(Activity):
    children: List[Activity] = []


class OrganizationList(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    building: Building
    phones: List[Phone] = []
    activities: List[Activity] = []


class SearchArea(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius: Optional[float] = Field(None, gt=0, description="Радиус поиска в километрах")
    min_latitude: Optional[float] = Field(None, ge=-90, le=90)
    max_latitude: Optional[float] = Field(None, ge=-90, le=90)
    min_longitude: Optional[float] = Field(None, ge=-180, le=180)
    max_longitude: Optional[float] = Field(None, ge=-180, le=180)


class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0, description="Количество записей для пропуска")
    limit: int = Field(100, ge=1, le=1000, description="Максимальное количество записей")


class ApiResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    data: Optional[List] = None


Activity.model_rebuild()