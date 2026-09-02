"""FastAPI app factory. The route layer reads ``app.state.services``,
which is populated here from whatever GatopleServices the caller provides.
Tests build their own services from fakes; production builds from real
cemaf + meridian wiring (see gatople_api.bootstrap, deferred)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gatople_api.routes import chat as chat_route
from gatople_api.routes import generate as generate_route
from gatople_api.routes import health as health_route
from gatople_api.routes import theory as theory_route
from gatople_api.services import GatopleServices


def create_app(*, services: GatopleServices, cors_origins: tuple[str, ...] = ()) -> FastAPI:
    """Build a FastAPI app with the given services attached."""
    app = FastAPI(title="gatople_api", version="0.1.0")
    app.state.services = services

    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(cors_origins),
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["content-type"],
        )

    app.include_router(health_route.router)
    app.include_router(chat_route.router)
    app.include_router(generate_route.router)
    app.include_router(theory_route.router)
    return app
