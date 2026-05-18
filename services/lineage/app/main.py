from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):

    # startup
    yield
    # shutdown

def create_app() -> FastAPI:

    settings = get_settings()
    app = FastAPI(
        title=settings.lineage_service_name,
        lifespan=lifespan,
    )

    # register routers here

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": settings.lineage_service_name,
            "version": settings.lineage_service_version
            }

    return app

app = create_app()