"""Cygnal free IOC enrichment microservice entrypoint."""

from fastapi import FastAPI

from ai_analyst.routes import router


def create_app() -> FastAPI:
    application = FastAPI(title="Cygnal Enrichment Analyst", version="2.0.0")
    application.include_router(router)
    return application


app = create_app()
