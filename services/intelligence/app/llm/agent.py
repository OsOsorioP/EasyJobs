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

_EMPTY_INSIGHT = {
    "summary": "Timeout/Error: Insight generation failed after multiple retries.",
    "score": 0,
    "strengths": [],
    "weaknesses": [],
    "suggested_role": "N/A",
}


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
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", PromptLoader.get_prompt("candidate_summary", "v1")),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

    def _build_executor(self, auth_token: str | None) -> AgentExecutor:
        tools = make_tools(auth_token)
        agent = create_tool_calling_agent(
            llm=self._llm,
            tools=tools,
            prompt=self._prompt,
        )
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,  # avoid leaking internal chain traces to logs in prod
            max_iterations=5,
        )

    async def generate_insight(self, query: str, auth_token: str | None = None) -> dict:
        executor = self._build_executor(auth_token)
        compressed_input = ContextCompressor.compress(query)

        @external_api_retry
        async def _run() -> dict:
            return await asyncio.wait_for(
                executor.ainvoke({"input": compressed_input}),
                timeout=settings.LLM_TIMEOUT,
            )

        try:
            response = await _run()
            raw_output = response.get("output", "")

            # The prompt instructs the LLM to return only JSON.
            # Attempt clean parse first, fall back to regex extraction.
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

            # LLM returned plain text — wrap it minimally
            return {**_EMPTY_INSIGHT, "summary": raw_output, "score": 0}

        except Exception as exc:
            logger.error("Error generating insight after retries: %s", exc)
            return _EMPTY_INSIGHT