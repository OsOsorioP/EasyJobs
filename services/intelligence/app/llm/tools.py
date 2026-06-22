import logging
import uuid

import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel

from app.core.config import settings
from app.llm.utils import external_api_retry
from app.vector_db.client import qdrant_client
from app.vector_db.indexer import VectorIndexer

logger = logging.getLogger(__name__)


class CandidateIdInput(BaseModel):
    candidate_id: str


class SearchProfilesInput(BaseModel):
    query_text: str
    limit: int = 5


class CalculateScoreInput(BaseModel):
    candidate_profile: str
    job_description: str


def make_tools(auth_token: str | None = None) -> list:
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}

    @external_api_retry
    def _get_candidate_profile(candidate_id: str) -> str:
        try:
            parsed_uuid = uuid.UUID(candidate_id)
        except ValueError:
            return f"Error de validación: '{candidate_id}' no es un UUID válido."

        url = f"{settings.CANDIDATE_SERVICE_INTERNAL_URL}/api/v1/candidates/{parsed_uuid}"
        try:
            with httpx.Client(timeout=settings.LLM_TIMEOUT) as client:
                response = client.get(url, headers=headers)
                if response.status_code == 404:
                    return f"No existe candidato con ID {parsed_uuid}."
                response.raise_for_status()
                c = response.json()
                return (
                    f"Nombre: {c.get('name')} | "
                    f"Habilidades: {c.get('skills') or 'No especificadas'} | "
                    f"Experiencia: {c.get('experience') or 'No registrada'} | "
                    f"Resumen: {c.get('summary') or 'Sin resumen'}"
                )
        except httpx.HTTPStatusError as exc:
            return f"Error downstream (HTTP {exc.response.status_code}): {exc.response.text[:200]}"
        except httpx.RequestError as exc:
            raise exc  # re-raise so tenacity retries

    @external_api_retry
    def _search_similar_profiles(query_text: str, limit: int = 5) -> str:
        """
        BUG FIX: original implementation returned only name/email/score.
        The agent prompt instructs to extract the candidate ID from this result
        to call get_candidate_profile. IDs were never included → agent could never
        follow its own workflow. Now includes the UUID from Qdrant point.id.
        """
        try:
            embeddings = VectorIndexer.generate_embeddings_batch(
                [query_text], input_type="search_query"
            )
            results = qdrant_client.query_points(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                query=embeddings[0],
                limit=limit,
            )
            if not results.points:
                return "No se encontraron candidatos similares."

            lines = []
            for p in results.points:
                name = p.payload.get("name", "Desconocido")
                email = p.payload.get("email", "")
                score = p.score
                candidate_id = str(p.id)  # UUID stored as Qdrant point ID
                lines.append(
                    f"- ID: {candidate_id} | {name} ({email}) | similitud: {score:.3f}"
                )
            return "\n".join(lines)

        except Exception as exc:
            logger.error("Error querying Qdrant in search tool: %s", exc)
            return f"Error al consultar la base vectorial: {exc}"

    def _calculate_score(candidate_profile: str, job_description: str) -> str:
        return (
            "Insumos para evaluación de compatibilidad:\n"
            f"PERFIL: {candidate_profile}\n"
            f"VACANTE: {job_description}\n"
            "Evalúa hard skills (50%), experiencia (30%) y metodologías (20%)."
        )

    return [
        StructuredTool(
            name="get_candidate_profile",
            description="Obtiene el perfil detallado de un candidato a partir de su UUID.",
            func=_get_candidate_profile,
            args_schema=CandidateIdInput,
        ),
        StructuredTool(
            name="search_similar_profiles",
            description=(
                "Busca candidatos semánticamente similares a una descripción. "
                "Retorna ID, nombre, email y similitud. Usa el ID para llamar a get_candidate_profile."
            ),
            func=_search_similar_profiles,
            args_schema=SearchProfilesInput,
        ),
        StructuredTool(
            name="calculate_score",
            description="Calcula compatibilidad técnica entre un candidato y una vacante.",
            func=_calculate_score,
            args_schema=CalculateScoreInput,
        ),
    ]