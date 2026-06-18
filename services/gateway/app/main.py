from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.api.proxy_routes import router
from app.core.auth_middleware import JWTAuthMiddleware
from app.core.correlation_middleware import CorrelationIdMiddleware
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    limits = httpx.Limits(
        max_keepalive_connections=100,
        max_connections=500,
        keepalive_expiry=30.0,
    )

    app.state.http_client = httpx.AsyncClient(
        limits=limits,
        timeout=httpx.Timeout(10.0),
    )
    yield
    await app.state.http_client.aclose()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(JWTAuthMiddleware)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}