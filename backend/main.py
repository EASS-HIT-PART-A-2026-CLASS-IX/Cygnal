from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.error_handlers import register_error_handlers
from backend.api.routes import auth, health, indicators
from backend.db.session import create_db_and_tables
from backend.middleware.trace import register_trace_and_rate_limit_middleware
from backend.models import Indicator  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


def create_app() -> FastAPI:
    application = FastAPI(title="Cygnal API", lifespan=lifespan)
    register_error_handlers(application)
    register_trace_and_rate_limit_middleware(application)
    application.include_router(auth.router)
    application.include_router(health.router)
    application.include_router(indicators.router)
    return application


app = create_app()
