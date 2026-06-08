"""FastAPI application factory for the ERP platform."""

from __future__ import annotations

from fastapi import FastAPI

from crm.controllers.routes import router as crm_router
from sales.controllers.routes import router as sales_router
from shared.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    app.include_router(crm_router)
    app.include_router(sales_router)
    return app


app = create_app()
