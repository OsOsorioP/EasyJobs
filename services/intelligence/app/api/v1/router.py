from fastapi import APIRouter

from app.api.v1.endpoints import etl, insights, search

api_router = APIRouter()
api_router.include_router(etl.router)
api_router.include_router(insights.router)
api_router.include_router(search.router)