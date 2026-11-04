"""Creates the FastAPI app: middleware + routers.

Run with: uv run uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, schema
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Build and configure the app (a function so tests could build a fresh one if needed)."""
    settings = get_settings()
    app = FastAPI(
        title="AskData API",
        description="Ask questions about the Chinook database in plain language.",
        version="0.1.0",
    )

    # The React dev server runs on another origin (port 5173), so the browser
    # blocks its requests unless the API explicitly allows that origin.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    app.include_router(health.router)
    app.include_router(schema.router)
    return app


app = create_app()
