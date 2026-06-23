import logging
from typing import List, Optional

import jwt
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.vector_db.client import qdrant_client
from app.vector_db.indexer import VectorIndexer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


def _recruiter_id_from_header(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        sub = payload.get("sub")
        if not sub:
            raise ValueError
        return sub
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=5, ge=1, le=50)


class SearchResult(BaseModel):
    id: str
    score: float
    name: str
    email: str
    skills: str
    experience: str
    summary: str


@router.post("", response_model=List[SearchResult])
async def search_profiles(
    payload: SearchRequest,
    authorization: Optional[str] = Header(default=None),
) -> List[SearchResult]:
    if not payload.query.strip():
        return []

    recruiter_id = _recruiter_id_from_header(authorization)

    try:
        VectorIndexer.ensure_collection_exists()

        embeddings = VectorIndexer.generate_embeddings_batch(
            [payload.query], input_type="search_query"
        )

        results = qdrant_client.query_points(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query=embeddings[0],
            query_filter=VectorIndexer.build_recruiter_filter(recruiter_id),
            limit=payload.limit,
        )

        return [
            SearchResult(
                id=str(point.id),
                score=float(point.score),
                name=point.payload.get("name") or "Desconocido",
                email=point.payload.get("email") or "",
                skills=point.payload.get("skills") or "",
                experience=point.payload.get("experience") or "",
                summary=point.payload.get("summary") or "",
            )
            for point in results.points
        ]

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error searching Qdrant")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar en Qdrant: {exc}",
        )