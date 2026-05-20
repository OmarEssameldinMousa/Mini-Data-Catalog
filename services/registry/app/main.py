from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from app.config import get_settings
from app.routers.dataset import router as dataset_router
from app.exceptions import DatasetNotFound, VersionNotFound, DatasetAlreadyExists, RegistryException, SchemaValidationFailed, ServiceUnavailableError
from app.database import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("Starting up Registry Service...")
    await init_db()
    
    settings = get_settings()
    _timeout = httpx.Timeout(connect=3.0, read=10.0, write=5.0, pool=2.0)
    app.state.http_client = httpx.AsyncClient(timeout=_timeout)
    app.state.validator_url = settings.validator_url

    yield
    # shutdown
    print("Shutting down Registry Service...")
    await app.state.http_client.aclose()
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

    @app.exception_handler(SchemaValidationFailed)
    async def schema_validation_failed_handler(request: Request, exc: SchemaValidationFailed):
        return JSONResponse(status_code=422, content={"detail": "Schema validation failed", "errors": exc.errors})

    @app.exception_handler(ServiceUnavailableError)
    async def service_unavailable_handler(request: Request, exc: ServiceUnavailableError):
        return JSONResponse(status_code=503, content={"detail": str(exc)})

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