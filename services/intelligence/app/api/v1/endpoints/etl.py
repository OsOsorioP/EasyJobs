from typing import Optional

from fastapi import APIRouter, Header, HTTPException, UploadFile, status

from app.etl.pipeline import ETLPipeline

router = APIRouter(prefix="/etl", tags=["etl"])

# BUG FIX: run_csv_ingestion was a @staticmethod with httpx.Client (blocking).
# It is now async. Both endpoints are properly awaited.

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