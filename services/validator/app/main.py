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
        title=settings.validator_service_name,
        lifespan=lifespan,
    )

    # register routers here

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "service": settings.validator_service_name,
            "version": settings.validator_service_version
            }

    return app

app = create_app()