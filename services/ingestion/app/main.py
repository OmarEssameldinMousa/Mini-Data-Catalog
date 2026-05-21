import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.api.v1.jobs import jobs_router
from app.exceptions import IngestionException, JobNotFound

from app.middleware.correlation import get_correlation_id, CorrelationIDMiddleware
from app.core.logging_config import setup_logging
import logging

logger = logging.getLogger(__name__)

async def _inject_correlation_id(request: httpx.Request) -> None:
    request.headers["X-Correlation-ID"] = get_correlation_id()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    settings = get_settings()
    setup_logging(
        service_name=settings.service_name,
        debug=settings.debug,
    )
    logger.info("Starting up Ingestion Service...")
    await init_db()

    # Store session factory on app.state for background tasks
    from app.core.database import AsyncSessionFactory as factory
    app.state.session_factory = factory

    # Create per-service async HTTP clients with explicit timeouts
    _timeout = httpx.Timeout(connect=3.0, read=10.0, write=5.0, pool=2.0)
    app.state.validator_http_client = httpx.AsyncClient(timeout=_timeout)
    app.state.registry_http_client = httpx.AsyncClient(timeout=_timeout)

    yield

    # shutdown
    logger.info("Shutting down Ingestion Service...")
    await app.state.validator_http_client.aclose()
    await app.state.registry_http_client.aclose()
    await close_db()


def create_app() -> FastAPI:

    settings = get_settings()
    app = FastAPI(
        title=settings.service_name,
        lifespan=lifespan,
        root_path="/api/ingestion",
    )
    
    app.add_middleware(CorrelationIDMiddleware)
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