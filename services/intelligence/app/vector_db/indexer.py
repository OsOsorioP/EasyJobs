import logging
from typing import List

import cohere
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings
from app.vector_db.client import qdrant_client

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSION = 1024

_cohere_client = cohere.Client(api_key=settings.COHERE_API_KEY)


class VectorIndexer:
    @staticmethod
    def ensure_collection_exists() -> None:
        """Idempotent: creates collection only if absent."""
        existing = {c.name for c in qdrant_client.get_collections().collections}
        if settings.QDRANT_COLLECTION_NAME not in existing:
            qdrant_client.create_collection(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("Created Qdrant collection '%s'", settings.QDRANT_COLLECTION_NAME)

    @staticmethod
    def generate_embeddings_batch(
        texts: List[str],
        input_type: str = "search_document",
    ) -> List[List[float]]:
        """
        Generates Cohere embeddings for a list of texts.

        Raises:
            cohere.CohereError: propagated to caller — do NOT silently swallow here;
            the pipeline must decide whether to skip or abort.
        """
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
        """
        Batch-upserts candidate vectors into Qdrant.

        Each item in candidates_data must have:
          - id: str (UUID from candidate service)
          - text_to_vectorize: str
          - metadata: dict (payload stored in Qdrant)
        """
        if not candidates_data:
            return

        VectorIndexer.ensure_collection_exists()

        texts = [item["text_to_vectorize"] for item in candidates_data]
        embeddings = VectorIndexer.generate_embeddings_batch(texts, input_type="search_document")

        points = [
            PointStruct(
                id=item["id"],
                vector=embeddings[i],
                payload=item["metadata"],
            )
            for i, item in enumerate(candidates_data)
        ]

        qdrant_client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            wait=True,
            points=points,
        )
        logger.info("Upserted %d points into Qdrant", len(points))