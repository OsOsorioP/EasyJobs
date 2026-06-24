import asyncio
import json
import logging
import re

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import settings
from app.llm.compression import ContextCompressor
from app.llm.prompt_loader import PromptLoader
from app.llm.tools import make_tools
from app.llm.utils import external_api_retry

logger = logging.getLogger(__name__)

_EMPTY_SINGLE_INSIGHT = {
    "type": "single",
    "candidate_id": None,
    "candidate_name": None,
    "summary": "Timeout/Error: la generación del insight falló después de varios reintentos.",
    "score": 0,
    "hard_skills_score": 0,
    "experience_score": 0,
    "methodology_score": 0,
    "strengths": [],
    "weaknesses": [],
    "suggested_role": "N/A",
}

_EMPTY_COMPARISON_INSIGHT = {
    "type": "comparison",
    "evaluated_against": "N/A",
    "candidates": [],
    "winner_candidate_id": None,
    "winner_name": None,
    "verdict": "Timeout/Error: la generación de la comparativa falló después de varios reintentos.",
}

_COMPARISON_KEYWORDS = (
    "compara", "compare", "comparar", "comparativa",
    "mejores candidatos", "mejores perfiles", "cuál es más apto",
    "cuál es mejor", "ranking", "rankea", "contrasta", "frente a",
    "versus", " vs ", "los top", "el top",
)


def _is_comparison_query(query: str) -> bool:
    normalized = query.lower()
    return any(keyword in normalized for keyword in _COMPARISON_KEYWORDS)


class Agent:
    def __init__(self) -> None:
        self._primary_llm = ChatCohere(
            model=settings.MODEL_NAME,
            cohere_api_key=settings.COHERE_API_KEY,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
        )
        self._fallback_llm = ChatGroq(
            model=settings.FALLBACK_MODEL_NAME,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
        )
        self._llm = self._primary_llm.with_fallbacks([self._fallback_llm])

        self._single_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", PromptLoader.get_prompt("candidate_summary", "v2")),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        self._comparison_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", PromptLoader.get_prompt("candidate_comparison", "v1")),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

    def _build_executor(self, auth_token: str | None, comparison: bool) -> AgentExecutor:
        tools = make_tools(auth_token)
        prompt = self._comparison_prompt if comparison else self._single_prompt
        agent = create_tool_calling_agent(
            llm=self._llm,
            tools=tools,
            prompt=prompt,
        )
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,  # avoid leaking internal chain traces to logs in prod
            max_iterations=12 if comparison else 5,
        )

    @staticmethod
    def _parse_json_output(raw_output: str, empty_fallback: dict) -> dict:
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                logger.warning("Agent returned non-parseable JSON block")

        # LLM returned plain text — wrap it minimally instead of failing the request
        return {**empty_fallback, "summary": raw_output, "verdict": raw_output}

    async def generate_insight(self, query: str, auth_token: str | None = None) -> dict:
        comparison = _is_comparison_query(query)
        executor = self._build_executor(auth_token, comparison=comparison)
        compressed_input = ContextCompressor.compress(query)
        empty_fallback = _EMPTY_COMPARISON_INSIGHT if comparison else _EMPTY_SINGLE_INSIGHT

        @external_api_retry
        async def _run() -> dict:
            return await asyncio.wait_for(
                executor.ainvoke({"input": compressed_input}),
                timeout=settings.LLM_TIMEOUT,
            )

        try:
            response = await _run()
            raw_output = response.get("output", "")
            parsed = self._parse_json_output(raw_output, empty_fallback)
            parsed.setdefault("type", "comparison" if comparison else "single")
            return parsed

        except Exception as exc:
            logger.error("Error generating insight after retries: %s", exc)
            return empty_fallback