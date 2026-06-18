from fastapi import APIRouter, HTTPException, UploadFile, status
from app.etl.pipeline import ETLPipeline

router = APIRouter(prefix="/etl", tags=["etl"])

@router.post("/csv")
async def ingest_csv(file: UploadFile) -> dict:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe tener extensión .csv")

    content = await file.read()
    try:
        return ETLPipeline.run_csv_ingestion(content)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

@router.post("/cv-batch")
async def ingest_cv_batch(file: UploadFile) -> dict:
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe tener extensión .zip")

    content = await file.read()
    try:
        return await ETLPipeline.run_zip_pdf_ingestion(content)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))