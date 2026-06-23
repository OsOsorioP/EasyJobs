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

def _get_recruiter_id(current_user: dict) -> uuid.UUID:
    return uuid.UUID(current_user["sub"])

@router.post(
    "",
    response_model=CandidateRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "recruiter"))],
)
def create_candidate(
    payload: CandidateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CandidateSQL:
    # recruiter_id always comes from the JWT — never trust the payload
    data = payload.model_dump()
    data["recruiter_id"] = _get_recruiter_id(current_user)

    candidate = CandidateSQL(**data)
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
    current_user: dict = Depends(get_current_user),
) -> list[CandidateSQL]:
    recruiter_id = _get_recruiter_id(current_user)
    stmt = (
        select(CandidateSQL)
        .where(CandidateSQL.recruiter_id == recruiter_id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())

@router.get("/{candidate_id}", response_model=CandidateRead)
def get_candidate(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CandidateSQL:
    recruiter_id = _get_recruiter_id(current_user)
    candidate = db.get(CandidateSQL, candidate_id)
    if candidate is None or candidate.recruiter_id != recruiter_id:
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
    current_user: dict = Depends(get_current_user),
) -> CandidateSQL:
    recruiter_id = _get_recruiter_id(current_user)
    candidate = db.get(CandidateSQL, candidate_id)
    if candidate is None or candidate.recruiter_id != recruiter_id:
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

@router.patch(
    "/{candidate_id}",
    response_model=CandidateRead,
    dependencies=[Depends(require_roles("admin", "recruiter"))],
)
def patch_candidate(
    candidate_id: uuid.UUID,
    payload: CandidatePatch,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> CandidateSQL:
    recruiter_id = _get_recruiter_id(current_user)
    candidate = db.get(CandidateSQL, candidate_id)
    if candidate is None or candidate.recruiter_id != recruiter_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
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
def delete_candidate(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> None:
    recruiter_id = _get_recruiter_id(current_user)
    candidate = db.get(CandidateSQL, candidate_id)
    if candidate is None or candidate.recruiter_id != recruiter_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")
    db.delete(candidate)
    db.commit()