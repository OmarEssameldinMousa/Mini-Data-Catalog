from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.routers.schemas import router as schemas_router
from app.routers.validation import router as validation_router
from app.core.database import init_db, close_db
from app.exceptions import (
    ValidatorException,
    SchemaNotFound,
    SchemaVersionNotFound,
    ActiveVersionNotFound,
)
import httpx
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
    logger.info("Starting up Validator Service...")
    await init_db()

    yield
    # shutdown
    logger.info("Shutting down Validator Service...")
    await close_db()

def create_app() -> FastAPI:

    settings = get_settings()
    app = FastAPI(
        title=settings.service_name,
        lifespan=lifespan,
        root_path="/api/validator",
    )
    
    app.add_middleware(CorrelationIDMiddleware)

    # ── Domain Exception Handlers (mirrors Registry pattern) ──

    @app.exception_handler(SchemaNotFound)
    async def schema_not_found_handler(request: Request, exc: SchemaNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(SchemaVersionNotFound)
    async def schema_version_not_found_handler(request: Request, exc: SchemaVersionNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ActiveVersionNotFound)
    async def active_version_not_found_handler(request: Request, exc: ActiveVersionNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ValidatorException)
    async def validator_exception_handler(request: Request, exc: ValidatorException):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    # ── Routes ──

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": settings.service_name,
            "version": settings.service_version
            }
    
    
    app.include_router(schemas_router)
    app.include_router(validation_router)

    return app

app = create_app()