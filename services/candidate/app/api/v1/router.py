from fastapi import APIRouter

from app.api.v1.endpoints import candidate

api_router = APIRouter()
api_router.include_router(candidate.router)