"""Cygnal AI analyst microservice entrypoint."""

from fastapi import FastAPI

from ai_analyst.routes import router


def create_app() -> FastAPI:
    application = FastAPI(title="Cygnal AI Analyst", version="1.0.0")
    application.include_router(router)
    return application


app = create_app()
