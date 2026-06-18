import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.candidate import CandidateSQL
from app.schemas.candidate import CandidateCreate, CandidateRead, CandidateUpdate, CandidatePatch
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/candidates", tags=["candidates"])

@router.post(
    "",
    response_model=CandidateRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "recruiter"))],
)
def create_candidate(payload: CandidateCreate, db: Session = Depends(get_db)) -> CandidateSQL:
    candidate = CandidateSQL(**payload.model_dump())
    db.add(candidate)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    db.refresh(candidate)
    return candidate

@router.get("", response_model=list[CandidateRead])
def list_candidates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> list[CandidateSQL]:
    stmt = select(CandidateSQL).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())

@router.get("/{candidate_id}", response_model=CandidateRead)
def get_candidate(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
) -> CandidateSQL:
    candidate = db.get(CandidateSQL, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    return candidate

@router.put(
    "/{candidate_id}",
    response_model=CandidateRead,
    dependencies=[Depends(require_roles("admin", "recruiter"))],
)
def update_candidate(
    candidate_id: uuid.UUID,
    payload: CandidateUpdate,
    db: Session = Depends(get_db),
) -> CandidateSQL:
    candidate = db.get(CandidateSQL, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    for field, value in payload.model_dump().items():
        setattr(candidate, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    db.refresh(candidate)
    return candidate

@router.delete(
    "/{candidate_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("admin"))],
)
def delete_candidate(candidate_id: uuid.UUID, db: Session = Depends(get_db)) -> None:
    candidate = db.get(CandidateSQL, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    db.delete(candidate)
    db.commit()

@router.patch(
    "/{candidate_id}",
    response_model=CandidateRead,
    dependencies=[Depends(require_roles("admin", "recruiter"))],
)
def patch_candidate(
    candidate_id: uuid.UUID,
    payload: CandidatePatch,
    db: Session = Depends(get_db),
) -> CandidateSQL:
    candidate = db.get(CandidateSQL, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(candidate, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    db.refresh(candidate)
    return candidate