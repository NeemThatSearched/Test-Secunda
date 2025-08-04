from sqlalchemy.ext.asyncio import AsyncSession
from app.core.patterns import ServiceFactory
from app.services.organization_service import OrganizationService
from app.services.building_service import BuildingService
from app.services.activity_service import ActivityService


class ConcreteServiceFactory(ServiceFactory):
    def create_organization_service(self, db_session: AsyncSession) -> OrganizationService:
        return OrganizationService(db_session)

    def create_building_service(self, db_session: AsyncSession) -> BuildingService:
        return BuildingService(db_session)

    def create_activity_service(self, db_session: AsyncSession) -> ActivityService:
        return ActivityService(db_session)