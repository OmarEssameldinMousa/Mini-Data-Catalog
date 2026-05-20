import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.settings import get_settings
from app.core.database import init_db, close_db
from app.api.routers.edges import router as edges_router
from app.exceptions import (
    LineageException,
    EdgeNotFound,
    EdgeAlreadyExists,
    DatasetNotFoundInRegistry,
    CycleDetected,
    ServiceUnavailableError,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("Starting up Lineage Service...")
    await init_db()
    app.state.http_client = httpx.AsyncClient()

    yield

    # shutdown
    print("Shutting down Lineage Service...")
    await app.state.http_client.aclose()
    await close_db()


def create_app() -> FastAPI:

    settings = get_settings()
    app = FastAPI(
        title=settings.service_name,
        lifespan=lifespan,
    )

    # ── Domain Exception Handlers ──

    @app.exception_handler(EdgeNotFound)
    async def edge_not_found_handler(request: Request, exc: EdgeNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(EdgeAlreadyExists)
    async def edge_already_exists_handler(request: Request, exc: EdgeAlreadyExists):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(DatasetNotFoundInRegistry)
    async def dataset_not_found_handler(request: Request, exc: DatasetNotFoundInRegistry):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(CycleDetected)
    async def cycle_detected_handler(request: Request, exc: CycleDetected):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(ServiceUnavailableError)
    async def service_unavailable_handler(request: Request, exc: ServiceUnavailableError):
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(LineageException)
    async def lineage_exception_handler(request: Request, exc: LineageException):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    # ── Routes ──

    app.include_router(edges_router)

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": settings.service_name,
            "version": settings.service_version,
        }

    return app

app = create_app()