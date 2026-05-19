from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.routers.dataset import router as dataset_router
from app.exceptions import DatasetNotFound, VersionNotFound, DatasetAlreadyExists, RegistryException
from app.database import AsyncSession, init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("Starting up Registry Service...")
    await init_db()

    yield
    # shutdown
    print("Shutting down Registry Service...")
    await close_db()

def create_app() -> FastAPI:

    settings = get_settings()
    app = FastAPI(
        title=settings.service_name,
        lifespan=lifespan,
    )

    # Register Exception Handlers
    @app.exception_handler(DatasetNotFound)
    async def dataset_not_found_handler(request: Request, exc: DatasetNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(VersionNotFound)
    async def version_not_found_handler(request: Request, exc: VersionNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(DatasetAlreadyExists)
    async def dataset_already_exists_handler(request: Request, exc: DatasetAlreadyExists):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(RegistryException)
    async def registry_exception_handler(request: Request, exc: RegistryException):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    # register routers here

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": settings.service_name,
            "version": settings.service_version
            }
    
    app.include_router(dataset_router)

    return app

app = create_app()