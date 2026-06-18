from fastapi import APIRouter
from pydantic import BaseModel
from app.llm.agent import Agent

router = APIRouter(prefix="/insights", tags=["insights"])

_agent = Agent()

class InsightRequest(BaseModel):
    query: str

@router.post("")
async def generate_insight(payload: InsightRequest) -> dict:
    return await _agent.generate_insight(payload.query)