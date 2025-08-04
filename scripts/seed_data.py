import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database_factory import DatabaseManager, PostgreSQLFactory
from app.models.models import Building, Activity, Phone, Organization
from app.services.service_factory import ConcreteServiceFactory


async def create_test_data():
    """Создание тестовых данных"""
    # Используем PostgreSQL который встроен в контейнер
    from app.core.config import get_settings
    settings = get_settings()
    factory = PostgreSQLFactory(settings.database_url)
    db_manager = DatabaseManager(factory)
    
    async with db_manager.session_factory() as session:
        # Создание зданий
        buildings_data = [
            {"address": "г. Москва, ул. Блюхера, 32/1", "latitude": 55.7558, "longitude": 37.6176},
            {"address": "г. Москва, ул. Ленина, 1, офис 3", "latitude": 55.7558, "longitude": 37.6200},
            {"address": "г. Санкт-Петербург, Невский пр., 50", "latitude": 59.9311, "longitude": 30.3609},
            {"address": "г. Екатеринбург, ул. Малышева, 15", "latitude": 56.8431, "longitude": 60.6454},
            {"address": "г. Новосибирск, ул. Красный пр., 25", "latitude": 55.0084, "longitude": 82.9357}
        ]
        
        buildings = []
        for building_data in buildings_data:
            building = Building(**building_data)
            session.add(building)
            buildings.append(building)
        
        await session.flush()
        
        # Создание видов деятельности
        activities_data = [
            {"name": "Еда", "parent_id": None, "level": 1},
            {"name": "Автомобили", "parent_id": None, "level": 1},
            {"name": "Услуги", "parent_id": None, "level": 1},
        ]
        
        activities = []
        for activity_data in activities_data:
            activity = Activity(**activity_data)
            session.add(activity)
            activities.append(activity)
        
        await session.flush()
        
        # Создание подкатегорий
        sub_activities_data = [
            {"name": "Мясная продукция", "parent_id": activities[0].id, "level": 2},
            {"name": "Молочная продукция", "parent_id": activities[0].id, "level": 2},
            {"name": "Хлебобулочные изделия", "parent_id": activities[0].id, "level": 2},
            {"name": "Грузовые", "parent_id": activities[1].id, "level": 2},
            {"name": "Легковые", "parent_id": activities[1].id, "level": 2},
            {"name": "Консультации", "parent_id": activities[2].id, "level": 2},
            {"name": "Ремонт", "parent_id": activities[2].id, "level": 2},
            {"name": "Строительство", "parent_id": activities[2].id, "level": 2},
        ]
        
        sub_activities = []
        for activity_data in sub_activities_data:
            activity = Activity(**activity_data)
            session.add(activity)
            sub_activities.append(activity)
        
        await session.flush()
        
        # Создание подподкатегорий
        sub_sub_activities_data = [
            {"name": "Запчасти", "parent_id": sub_activities[4].id, "level": 3},
            {"name": "Аксессуары", "parent_id": sub_activities[4].id, "level": 3},
        ]
        
        for activity_data in sub_sub_activities_data:
            activity = Activity(**activity_data)
            session.add(activity)
            sub_activities.append(activity)
        
        await session.flush()
        
        # Создание телефонов
        phones_data = [
            {"number": "2-222-222"},
            {"number": "3-333-333"},
            {"number": "8-923-666-13-13"},
            {"number": "8-495-123-45-67"},
            {"number": "8-812-987-65-43"},
            {"number": "8-343-555-12-34"},
            {"number": "8-383-777-88-99"}
        ]
        
        phones = []
        for phone_data in phones_data:
            phone = Phone(**phone_data)
            session.add(phone)
            phones.append(phone)
        
        await session.flush()
        
        # Создание организаций
        organizations_data = [
            {
                "name": "ООО \"Рога и Копыта\"",
                "building": buildings[0],
                "phones": [phones[0], phones[1]],
                "activities": [activities[0], sub_activities[0], sub_activities[1]]
            },
            {
                "name": "ЗАО \"Мясокомбинат\"",
                "building": buildings[1],
                "phones": [phones[2]],
                "activities": [sub_activities[0]]
            },
            {
                "name": "ИП Молочников",
                "building": buildings[0],
                "phones": [phones[3]],
                "activities": [sub_activities[1]]
            },
            {
                "name": "Автосалон \"Премиум\"",
                "building": buildings[2],
                "phones": [phones[4], phones[5]],
                "activities": [activities[1], sub_activities[4]]
            },
            {
                "name": "Грузовые перевозки \"Быстро\"",
                "building": buildings[3],
                "phones": [phones[6]],
                "activities": [sub_activities[3]]
            },
            {
                "name": "Автозапчасти \"Деталь\"",
                "building": buildings[4],
                "phones": [phones[1], phones[2]],
                "activities": [sub_activities[7]]
            },
            {
                "name": "Консалтинг \"Эксперт\"",
                "building": buildings[2],
                "phones": [phones[3]],
                "activities": [activities[2], sub_activities[5]]
            },
            {
                "name": "Хлебозавод \"Свежесть\"",
                "building": buildings[1],
                "phones": [phones[0]],
                "activities": [sub_activities[2]]
            }
        ]
        
        for org_data in organizations_data:
            organization = Organization(
                name=org_data["name"],
                building=org_data["building"]
            )
            
            for phone in org_data["phones"]:
                organization.phones.append(phone)
            
            for activity in org_data["activities"]:
                organization.activities.append(activity)
            
            session.add(organization)
        
        await session.commit()
        print("Тестовые данные успешно созданы!")


async def main():
    await create_test_data()


if __name__ == "__main__":
    asyncio.run(main())