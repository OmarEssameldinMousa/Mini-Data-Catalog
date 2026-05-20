from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import get_settings
from app.routers.schemas import router as schemas_router
from app.routers.validation import router as validation_router
from app.core.database import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("Starting up Validator Service...")
    await init_db()

    yield
    # shutdown
    print("Shutting down Validator Service...")
    await close_db()

def create_app() -> FastAPI:

    settings = get_settings()
    app = FastAPI(
        title=settings.service_name,
        lifespan=lifespan,
    )

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