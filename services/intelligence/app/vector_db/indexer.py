from typing import Any, List
from qdrant_client.models import PointStruct
from app.vector_db.client import qdrant_client
from app.core.config import settings
import cohere

cohere_client = cohere.Client(api_key=settings.COHERE_API_KEY)

class VectorIndexer:
    @staticmethod
    def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
        """Genera representaciones vectoriales en un solo lote para optimizar las llamadas de red."""
        response = cohere_client.embed(
            texts=texts,
            model="embed-multilingual-v3.0",
            input_type="search_document"
        )
        return response.embeddings

    @staticmethod
    def upsert_candidates_to_vector_db(candidates_data: List[dict]) -> None:
        """Sube un bloque de candidatos indexándolos en la base de datos vectorial.
        
        candidates_data debe contener diccionarios con las llaves:
        'id' (UUID string de PostgreSQL), 'text_to_vectorize' y 'metadata'.
        """
        if not candidates_data:
            return

        texts_to_embed = [item["text_to_vectorize"] for item in candidates_data]
        embeddings = VectorIndexer.generate_embeddings_batch(texts_to_embed)

        points = []
        for i, item in enumerate(candidates_data):
            points.append(
                PointStruct(
                    id=item["id"],  # Preservamos el UUID de PostgreSQL como clave primaria en Qdrant
                    vector=embeddings[i],
                    payload=item["metadata"]
                )
            )

        # Inserción masiva en Qdrant
        qdrant_client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            wait=True,
            points=points
        )