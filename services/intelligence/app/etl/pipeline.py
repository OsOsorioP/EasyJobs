import asyncio
import logging
from typing import Optional
import jwt
import httpx
from langchain_cohere import ChatCohere

from app.core.config import settings
from app.etl.parser import ETLParser
from app.schemas.extracted_candidate import ExtractedCandidate
from app.vector_db.indexer import VectorIndexer

logger = logging.getLogger(__name__)

_HTTP_LIMITS = httpx.Limits(max_keepalive_connections=5, max_connections=10)
_HTTP_TIMEOUT = 30.0

def _extract_recruiter_id(auth_header: Optional[str]) -> Optional[str]:
    """Decodes JWT without verification (gateway already validated it) to get sub."""
    if not auth_header:
        return None
    token = auth_header.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("sub")
    except Exception:
        return None

def _build_index_item(candidate_db: dict, recruiter_id: str) -> dict:
    return {
        "id": candidate_db["id"],
        "text_to_vectorize": (
            f"Nombre: {candidate_db['name']}. "
            f"Habilidades: {candidate_db.get('skills') or ''}. "
            f"Resumen: {candidate_db.get('summary') or ''}"
        ),
        "metadata": {
            "recruiter_id": recruiter_id,  # scoping key for Qdrant filtered search
            "name": candidate_db["name"],
            "email": candidate_db["email"],
            "skills": candidate_db.get("skills") or "",
            "experience": candidate_db.get("experience") or "",
            "summary": candidate_db.get("summary") or "",
        },
    }


async def _flush_to_vector_db(batch: list) -> None:
    if batch:
        await asyncio.to_thread(VectorIndexer.upsert_candidates_to_vector_db, batch)

class ETLPipeline:
    @staticmethod
    async def run_csv_ingestion(file_content: bytes, auth_header: Optional[str] = None) -> dict:
        recruiter_id = _extract_recruiter_id(auth_header)
        if not recruiter_id:
            raise ValueError("No se pudo determinar el recruiter_id desde el token.")

        candidates_to_process = ETLParser.parse_csv(file_content)
        candidates_to_index: list = []
        processed_count = 0
        skipped_count = 0
        error_count = 0

        headers = {"Content-Type": "application/json"}
        if auth_header:
            headers["Authorization"] = auth_header

        url = f"{settings.CANDIDATE_SERVICE_INTERNAL_URL}/api/v1/candidates"

        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, limits=_HTTP_LIMITS) as client:
            for candidate_payload in candidates_to_process:
                candidate_payload["recruiter_id"] = recruiter_id
                try:
                    response = await client.post(url, json=candidate_payload, headers=headers)
                    if response.status_code == 409:
                        skipped_count += 1
                        continue
                    response.raise_for_status()
                    candidate_db = response.json()
                    candidates_to_index.append(_build_index_item(candidate_db, recruiter_id))

                    if len(candidates_to_index) >= settings.CSV_BATCH_SIZE:
                        await _flush_to_vector_db(candidates_to_index)
                        processed_count += len(candidates_to_index)
                        candidates_to_index.clear()

                except httpx.HTTPStatusError as exc:
                    error_count += 1
                    logger.warning(
                        "ETL CSV: HTTP %d for '%s' — %s",
                        exc.response.status_code,
                        candidate_payload.get("email", "?"),
                        exc.response.text[:200],
                    )
                except Exception as exc:
                    error_count += 1
                    logger.warning("ETL CSV: skipped — %s", exc)

            if candidates_to_index:
                await _flush_to_vector_db(candidates_to_index)
                processed_count += len(candidates_to_index)

        return {
            "status": "completed",
            "total_records": processed_count,
            "skipped_duplicates": skipped_count,
            "errors": error_count,
        }

    @staticmethod
    async def _extract_candidate_metadata_with_llm(raw_text: str) -> Optional[ExtractedCandidate]:
        try:
            llm = ChatCohere(
                model=settings.MODEL_NAME,
                cohere_api_key=settings.COHERE_API_KEY,
                temperature=0.0,
            )
            structured_llm = llm.with_structured_output(ExtractedCandidate)
            system_prompt = (
                "Eres un asistente de reclutamiento de IA. Analiza el texto de la siguiente "
                "hoja de vida (CV) y extrae la información requerida de manera estricta y profesional."
            )
            return await asyncio.to_thread(
                structured_llm.invoke,
                [("system", system_prompt), ("human", raw_text)],
            )
        except Exception as exc:
            logger.warning("LLM extraction failed: %s", exc)
            return None

    @staticmethod
    async def run_zip_pdf_ingestion(zip_content: bytes, auth_header: Optional[str] = None) -> dict:
        recruiter_id = _extract_recruiter_id(auth_header)
        if not recruiter_id:
            raise ValueError("No se pudo determinar el recruiter_id desde el token.")

        pdf_files = ETLParser.parse_zip_archive(zip_content)
        candidates_to_index: list = []
        processed_count = 0
        skipped_count = 0
        error_count = 0

        headers = {"Content-Type": "application/json"}
        if auth_header:
            headers["Authorization"] = auth_header

        url = f"{settings.CANDIDATE_SERVICE_INTERNAL_URL}/api/v1/candidates"

        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT, limits=_HTTP_LIMITS) as client:
            for pdf_file in pdf_files:
                try:
                    raw_text = ETLParser.extract_text_from_pdf(pdf_file["content"])
                    if not raw_text or len(raw_text) < 50:
                        logger.warning("ETL ZIP: skipped '%s' — insufficient text", pdf_file["filename"])
                        continue

                    extracted: Optional[ExtractedCandidate] = (
                        await ETLPipeline._extract_candidate_metadata_with_llm(raw_text)
                    )
                    if not extracted:
                        error_count += 1
                        continue

                    payload = extracted.model_dump()
                    payload["recruiter_id"] = recruiter_id

                    response = await client.post(url, json=payload, headers=headers)
                    if response.status_code == 409:
                        skipped_count += 1
                        continue
                    response.raise_for_status()
                    candidate_db = response.json()
                    candidates_to_index.append(_build_index_item(candidate_db, recruiter_id))

                    if len(candidates_to_index) >= settings.PDF_BATCH_SIZE:
                        await _flush_to_vector_db(candidates_to_index)
                        processed_count += len(candidates_to_index)
                        candidates_to_index.clear()

                except httpx.HTTPStatusError as exc:
                    error_count += 1
                    logger.warning(
                        "ETL ZIP: HTTP %d for '%s' — %s",
                        exc.response.status_code,
                        pdf_file.get("filename", "?"),
                        exc.response.text[:200],
                    )
                except Exception as exc:
                    error_count += 1
                    logger.warning("ETL ZIP: PDF skipped '%s' — %s", pdf_file.get("filename"), exc)

            if candidates_to_index:
                await _flush_to_vector_db(candidates_to_index)
                processed_count += len(candidates_to_index)

        return {
            "status": "completed",
            "total_pdfs_processed": processed_count,
            "skipped_duplicates": skipped_count,
            "errors": error_count,
        }