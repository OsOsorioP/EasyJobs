import logging
from typing import List

import cohere
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams
from app.core.config import settings
from app.vector_db.client import qdrant_client

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSION = 1024

_cohere_client = cohere.Client(api_key=settings.COHERE_API_KEY)

class VectorIndexer:
    @staticmethod
    def ensure_collection_exists() -> None:
        existing = {c.name for c in qdrant_client.get_collections().collections}
        if settings.QDRANT_COLLECTION_NAME not in existing:
            qdrant_client.create_collection(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(size=EMBEDDING_DIMENSION, distance=Distance.COSINE),
            )
            # Index recruiter_id for efficient filtered search
            qdrant_client.create_payload_index(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                field_name="recruiter_id",
                field_schema="keyword",
            )
            logger.info("Created Qdrant collection '%s'", settings.QDRANT_COLLECTION_NAME)

    @staticmethod
    def generate_embeddings_batch(
        texts: List[str],
        input_type: str = "search_document",
    ) -> List[List[float]]:
        if not texts:
            return []
        response = _cohere_client.embed(
            texts=texts,
            model=settings.COHERE_EMBED_MODEL,
            input_type=input_type,
        )
        embeddings = response.embeddings
        if not embeddings or len(embeddings) != len(texts):
            raise ValueError(
                f"Cohere returned {len(embeddings) if embeddings else 0} embeddings "
                f"for {len(texts)} texts"
            )
        return embeddings

    @staticmethod
    def upsert_candidates_to_vector_db(candidates_data: List[dict]) -> None:
        if not candidates_data:
            return

        VectorIndexer.ensure_collection_exists()

        texts = [item["text_to_vectorize"] for item in candidates_data]
        embeddings = VectorIndexer.generate_embeddings_batch(texts, input_type="search_document")

        points = [
            PointStruct(
                id=item["id"],
                vector=embeddings[i],
                payload=item["metadata"],  # must include recruiter_id
            )
            for i, item in enumerate(candidates_data)
        ]

        qdrant_client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            wait=True,
            points=points,
        )
        logger.info("Upserted %d points into Qdrant", len(points))

    @staticmethod
    def build_recruiter_filter(recruiter_id: str) -> Filter:
        return Filter(
            must=[FieldCondition(key="recruiter_id", match=MatchValue(value=recruiter_id))]
        )

    @staticmethod
    def delete_by_recruiter(recruiter_id: str) -> None:
        qdrant_client.delete(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points_selector=VectorIndexer.build_recruiter_filter(recruiter_id),
        )
        logger.info("Deleted all vectors for recruiter_id=%s", recruiter_id)

    @staticmethod
    def delete_by_ids(ids: List[str]) -> None:
        if not ids:
            return
        qdrant_client.delete(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points_selector=ids,
        )
        logger.info("Deleted %d vectors by id", len(ids))