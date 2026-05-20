import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.api.v1.jobs import jobs_router
from app.exceptions import IngestionException, JobNotFound


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("Starting up Ingestion Service...")
    await init_db()

    # Store session factory on app.state for background tasks
    from app.core.database import AsyncSessionFactory as factory
    app.state.session_factory = factory

    # Create shared async HTTP client for inter-service calls
    app.state.http_client = httpx.AsyncClient()

    yield

    # shutdown
    print("Shutting down Ingestion Service...")
    await app.state.http_client.aclose()
    await close_db()


def create_app() -> FastAPI:

    settings = get_settings()
    app = FastAPI(
        title=settings.service_name,
        lifespan=lifespan,
    )

    # ── Domain Exception Handlers ──

    @app.exception_handler(JobNotFound)
    async def job_not_found_handler(request: Request, exc: JobNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(IngestionException)
    async def ingestion_exception_handler(request: Request, exc: IngestionException):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    # ── Routes ──

    app.include_router(jobs_router)

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": settings.service_name,
            "version": settings.service_version
            }

    return app

app = create_app()