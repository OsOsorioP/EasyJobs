from fastapi import APIRouter, Request, Response
from app.core.config import settings
from app.core.proxy import forward_request

router = APIRouter()

@router.api_route("/identity/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_identity(path: str, request: Request) -> Response:
    return await forward_request(request, settings.IDENTITY_SERVICE_URL, f"/{path}")

@router.api_route("/candidates/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_candidates(path: str, request: Request) -> Response:
    return await forward_request(request, settings.CANDIDATE_SERVICE_URL, f"/api/v1/candidates/{path}")

@router.api_route("/candidates", methods=["GET", "POST"])
async def proxy_candidates_root(request: Request) -> Response:
    return await forward_request(request, settings.CANDIDATE_SERVICE_URL, "/api/v1/candidates")

@router.api_route("/intelligence/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_intelligence(path: str, request: Request) -> Response:
    return await forward_request(request, settings.INTELLIGENCE_SERVICE_URL, f"/api/v1/{path}")