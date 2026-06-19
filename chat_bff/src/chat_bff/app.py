"""FastAPI app factory. The route layer reads ``app.state.services``,
which is populated here from whatever ChatServices the caller provides.
Tests build their own services from fakes; production builds from real
cemaf + meridian wiring (see chat_bff.bootstrap, deferred)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chat_bff.routes import chat as chat_route
from chat_bff.routes import health as health_route
from chat_bff.services import ChatServices


def create_app(*, services: ChatServices, cors_origins: tuple[str, ...] = ()) -> FastAPI:
    """Build a FastAPI app with the given services attached."""
    app = FastAPI(title="chat_bff", version="0.1.0")
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
    return app
