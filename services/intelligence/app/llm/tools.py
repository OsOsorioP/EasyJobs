import logging
import re
import uuid

import httpx
import jwt
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
    candidate_skills: str
    candidate_experience: str
    job_description: str


def _recruiter_id_from_token(auth_token: str | None) -> str | None:
    if not auth_token:
        return None
    try:
        payload = jwt.decode(auth_token, options={"verify_signature": False})
        return payload.get("sub")
    except Exception:
        return None


def _tokenize(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-záéíóúñ0-9+#./]+", text.lower()) if len(t) > 1}


_EXPERIENCE_YEARS_RE = re.compile(r"(\d+)\s*(?:años|year|yrs|años de experiencia)")
_SENIORITY_WEIGHTS = {
    "junior": 0.3,
    "trainee": 0.2,
    "intern": 0.15,
    "mid": 0.55,
    "semi senior": 0.55,
    "senior": 0.8,
    "lead": 0.9,
    "staff": 0.95,
    "principal": 0.95,
    "cto": 1.0,
    "head": 0.95,
    "manager": 0.85,
}


def _hard_skills_score(candidate_skills: str, job_description: str) -> float:
    job_tokens = _tokenize(job_description)
    skill_tokens = _tokenize(candidate_skills)
    if not job_tokens or not skill_tokens:
        return 0.0
    overlap = job_tokens & skill_tokens
    return round(min(len(overlap) / max(len(job_tokens), 1) * 1.5, 1.0), 2)


def _experience_score(candidate_experience: str) -> float:
    text = candidate_experience.lower()
    years_match = _EXPERIENCE_YEARS_RE.search(text)
    years_score = 0.0
    if years_match:
        years = int(years_match.group(1))
        years_score = min(years / 10, 1.0)

    seniority_score = 0.0
    for keyword, weight in _SENIORITY_WEIGHTS.items():
        if keyword in text:
            seniority_score = max(seniority_score, weight)

    if years_match and seniority_score:
        return round((years_score + seniority_score) / 2, 2)
    return round(years_score or seniority_score, 2)


def _methodology_score(candidate_skills: str, candidate_experience: str) -> float:
    text = f"{candidate_skills} {candidate_experience}".lower()
    keywords = [
        "scrum", "agile", "ágil", "kanban", "ci/cd", "tdd", "devops",
        "microservicios", "microservices", "code review", "pair programming",
    ]
    hits = sum(1 for k in keywords if k in text)
    return round(min(hits / 3, 1.0), 2)


def make_tools(auth_token: str | None = None) -> list:
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    recruiter_id = _recruiter_id_from_token(auth_token)

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
                    f"ID: {parsed_uuid} | "
                    f"Nombre: {c.get('name')} | "
                    f"Habilidades: {c.get('skills') or 'No especificadas'} | "
                    f"Experiencia: {c.get('experience') or 'No registrada'} | "
                    f"Resumen: {c.get('summary') or 'Sin resumen'}"
                )
        except httpx.HTTPStatusError as exc:
            return f"Error downstream (HTTP {exc.response.status_code}): {exc.response.text[:200]}"
        except httpx.RequestError as exc:
            raise exc

    @external_api_retry
    def _search_similar_profiles(query_text: str, limit: int = 5) -> str:
        try:
            embeddings = VectorIndexer.generate_embeddings_batch(
                [query_text], input_type="search_query"
            )

            query_filter = (
                VectorIndexer.build_recruiter_filter(recruiter_id) if recruiter_id else None
            )

            results = qdrant_client.query_points(
                collection_name=settings.QDRANT_COLLECTION_NAME,
                query=embeddings[0],
                query_filter=query_filter,
                limit=limit,
            )

            if not results.points:
                return "No se encontraron candidatos similares."

            lines = [
                f"- ID: {str(p.id)} | {p.payload.get('name', '?')} ({p.payload.get('email', '')}) | "
                f"similitud: {p.score:.3f} | habilidades: {p.payload.get('skills', '')} | "
                f"experiencia: {p.payload.get('experience', '')}"
                for p in results.points
            ]
            return "\n".join(lines)

        except Exception as exc:
            logger.error("Error querying Qdrant in search tool: %s", exc)
            return f"Error al consultar la base vectorial: {exc}"

    def _calculate_score(candidate_skills: str, candidate_experience: str, job_description: str) -> str:
        hard_skills = _hard_skills_score(candidate_skills, job_description)
        experience = _experience_score(candidate_experience)
        methodology = _methodology_score(candidate_skills, candidate_experience)
        overall = round(hard_skills * 0.5 + experience * 0.3 + methodology * 0.2, 2)
        return (
            f"hard_skills_score={hard_skills} | experience_score={experience} | "
            f"methodology_score={methodology} | score={overall}. "
            "Usa EXACTAMENTE estos cuatro valores numéricos en el JSON de salida, no los recalcules ni los inventes."
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
                "Busca candidatos semánticamente similares a una descripción dentro del pool "
                "del recruiter autenticado. Retorna ID, nombre, email, similitud, habilidades y experiencia."
            ),
            func=_search_similar_profiles,
            args_schema=SearchProfilesInput,
        ),
        StructuredTool(
            name="calculate_score",
            description=(
                "Calcula de forma determinística hard_skills_score, experience_score, "
                "methodology_score y score global (0 a 1) comparando las habilidades y "
                "experiencia textuales del candidato contra la descripción del puesto/vacante. "
                "Llámala SIEMPRE antes de redactar el score final de cualquier candidato."
            ),
            func=_calculate_score,
            args_schema=CalculateScoreInput,
        ),
    ]