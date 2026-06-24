from typing import Optional

import httpx
import jwt
from fastapi import APIRouter, Header, HTTPException, UploadFile, status

from app.core.config import settings
from app.etl.pipeline import ETLPipeline
from app.vector_db.indexer import VectorIndexer

router = APIRouter(prefix="/etl", tags=["etl"])

# BUG FIX: run_csv_ingestion was a @staticmethod with httpx.Client (blocking).
# It is now async. Both endpoints are properly awaited.

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


@router.post("/csv")
async def ingest_csv(
    file: UploadFile,
    authorization: Optional[str] = Header(default=None),
) -> dict:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe tener extensión .csv",
        )

    content = await file.read()
    try:
        return await ETLPipeline.run_csv_ingestion(content, auth_header=authorization)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/cv-batch")
async def ingest_cv_batch(
    file: UploadFile,
    authorization: Optional[str] = Header(default=None),
) -> dict:
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe tener extensión .zip",
        )

    content = await file.read()
    try:
        return await ETLPipeline.run_zip_pdf_ingestion(content, auth_header=authorization)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/purge")
async def purge_recruiter_candidates(
    authorization: Optional[str] = Header(default=None),
) -> dict:
    """Borra TODOS los candidatos del recruiter autenticado (Postgres + Qdrant).
    Pensado para limpiar una carga ETL antes de re-importar."""
    recruiter_id = _recruiter_id_from_header(authorization)

    headers = {"Authorization": authorization} if authorization else {}
    url = f"{settings.CANDIDATE_SERVICE_INTERNAL_URL}/api/v1/candidates/bulk"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.delete(url, headers=headers)
        response.raise_for_status()
        deleted_count = response.json().get("deleted_count", 0)

    VectorIndexer.delete_by_recruiter(recruiter_id)

    return {"status": "completed", "deleted_count": deleted_count}