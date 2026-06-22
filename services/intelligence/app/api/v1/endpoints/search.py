import logging
from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.vector_db.client import qdrant_client
from app.vector_db.indexer import VectorIndexer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


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
async def search_profiles(payload: SearchRequest) -> List[SearchResult]:
    if not payload.query.strip():
        return []

    try:
        VectorIndexer.ensure_collection_exists()

        embeddings = VectorIndexer.generate_embeddings_batch(
            [payload.query],
            input_type="search_query",
        )
        query_vector = embeddings[0]

        results = qdrant_client.query_points(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query=query_vector,
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

    except Exception as exc:
        logger.exception("Error searching Qdrant")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar en Qdrant: {exc}",
        )