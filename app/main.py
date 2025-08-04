from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.api.dependencies import get_database_manager
from app.api import organizations, buildings, activities
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager = get_database_manager()
    
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    await db_manager.engine.dispose()


def create_application() -> FastAPI:
    """Создание экземпляра FastAPI приложения"""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="REST API для справочника организаций, зданий и деятельности",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(organizations.router, prefix="/api/v1")
    app.include_router(buildings.router, prefix="/api/v1")
    app.include_router(activities.router, prefix="/api/v1")

    @app.get("/")
    async def root():
        return {
            "message": "Organizations Directory API",
            "version": settings.version,
            "docs": "/docs",
            "redoc": "/redoc"
        }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_application()