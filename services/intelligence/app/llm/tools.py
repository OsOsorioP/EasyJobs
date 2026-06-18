import uuid

import httpx
from langchain.tools import tool

from app.core.config import settings
from app.llm.utils import external_api_retry
from app.vector_db.client import qdrant_client
from app.vector_db.indexer import VectorIndexer


@tool
@external_api_retry
def get_candidate_profile(candidate_id: str) -> str:
    """Obtiene el perfil detallado de un candidato consumiendo la API interna del microservicio.

    Args:
        candidate_id (str): Representación hexadecimal del UUID del candidato.

    Returns:
        str: Información resumida en texto para contexto del LLM.
    """
    try:
        parsed_uuid = uuid.UUID(candidate_id)
    except ValueError:
        return f"Error de validación: El ID '{candidate_id}' provisto no cumple con el estándar RFC 4122 (UUID)."

    url = f"{settings.CANDIDATE_SERVICE_INTERNAL_URL}/api/v1/candidates/{parsed_uuid}"

    try:
        with httpx.Client(timeout=settings.LLM_TIMEOUT) as client:
            response = client.get(url)

            if response.status_code == 404:
                return f"Error: No existe ningún candidato registrado con el ID {parsed_uuid}."

            response.raise_for_status()
            c = response.json()

            return (
                f"Nombre completo: {c.get('name')} | "
                f"Habilidades: {c.get('skills', 'No especificadas')} | "
                f"Experiencia: {c.get('experience', 'No registrada')} | "
                f"Resumen: {c.get('summary', 'Sin resumen')}"
            )

    except httpx.HTTPStatusError as exc:
        return f"Error del sistema downstream (Código: {exc.response.status_code}): {exc.response.text}"
    except httpx.RequestError as exc:
        raise exc


@tool
@external_api_retry
def search_similar_profiles(query_text: str, limit: int = 5) -> str:
    """Busca candidatos con perfiles semánticamente similares a una descripción dada.

    Útil para calibrar la evaluación de un candidato comparándolo contra perfiles
    existentes en el sistema, o para encontrar candidatos afines a una vacante.

    Args:
        query_text (str): Descripción del perfil o vacante a buscar (texto libre).
        limit (int): Cantidad máxima de resultados similares a retornar.

    Returns:
        str: Listado de candidatos similares con su score de similitud.
    """
    try:
        embeddings = VectorIndexer.generate_embeddings_batch([query_text])
        query_vector = embeddings[0]

        results = qdrant_client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
        )

        if not results:
            return "No se encontraron candidatos similares en la base vectorial."

        lines = []
        for point in results:
            name = point.payload.get("name", "Desconocido")
            email = point.payload.get("email", "Sin email")
            lines.append(f"- {name} ({email}) | similitud: {point.score:.3f}")

        return "\n".join(lines)

    except Exception as exc:
        return f"Error al consultar la base vectorial: {exc}"


@tool
@external_api_retry
def calculate_score(candidate_profile: str, job_description: str) -> str:
    """Calcula un puntaje de compatibilidad técnica entre un candidato y una vacante.

    Utilízala cuando el usuario proporcione una descripción de puesto y necesites
    evaluar qué tan alineado está el perfil del candidato con esos requisitos.

    Args:
        candidate_profile (str): Texto con el perfil del candidato (skills, experiencia, resumen).
        job_description (str): Descripción de la vacante o puesto a evaluar.

    Returns:
        str: Texto descriptivo con matches, gaps y conclusión, listo para que el LLM
        lo incorpore a su análisis final.
    """
    return (
        "Insumos recibidos para evaluación de compatibilidad:\n"
        f"PERFIL DEL CANDIDATO: {candidate_profile}\n"
        f"DESCRIPCIÓN DE LA VACANTE: {job_description}\n"
        "Evalúa hard skills (50%), profundidad de experiencia (30%) y metodologías (20%), "
        "siguiendo los criterios del prompt de skill_extraction."
    )