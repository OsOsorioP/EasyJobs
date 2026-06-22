import logging
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, field_validator

from app.llm.agent import Agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insights", tags=["insights"])

# BUG FIX: module-level singleton _agent = Agent() causes startup failure if
# Cohere/Groq keys are missing or prompts are absent. Instantiated per-request
# is slightly heavier but Agent is stateless — acceptable tradeoff.
# If performance matters at scale, use FastAPI dependency injection with lifespan.

_agent = Agent()


class InsightRequest(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query must not be empty")
        return v.strip()


@router.post("")
async def generate_insight(
    payload: InsightRequest,
    authorization: Optional[str] = Header(default=None),
) -> dict:
    token = authorization.removeprefix("Bearer ").strip() if authorization else None
    try:
        return await _agent.generate_insight(payload.query, auth_token=token)
    except Exception as exc:
        logger.exception("Unhandled error in generate_insight")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando insight: {exc}",
        )