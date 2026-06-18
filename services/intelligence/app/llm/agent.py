from langchain_groq import ChatGroq
from langchain_cohere import ChatCohere
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from app.llm.tools import get_candidate_profile, search_similar_profiles, calculate_score
from app.llm.prompt_loader import PromptLoader
from app.llm.compression import ContextCompressor
from app.core.config import settings
from app.llm.utils import external_api_retry
import json, re, asyncio

class Agent:
    def __init__(self):
        primary_llm = ChatCohere(
            model=settings.MODEL_NAME,
            cohere_api_key=settings.COHERE_API_KEY,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )

        fallback_llm = ChatGroq(
            model=settings.FALLBACK_MODEL_NAME,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )

        self.llm = primary_llm.with_fallbacks([fallback_llm])

        self.tools = [
            get_candidate_profile,
            search_similar_profiles,
            calculate_score
        ]

        prompt = ChatPromptTemplate.from_messages([
            ("system", PromptLoader.get_prompt("candidate_summary", "v1")),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
        )

    @external_api_retry
    async def _generate_internal(self, input_data: dict):
        return await asyncio.wait_for(
            self.agent_executor.ainvoke(input_data),
            timeout=settings.LLM_TIMEOUT
        )

    async def generate_insight(self, query: str):
        try:
            compressed_input = ContextCompressor.compress(query)

            response = await self._generate_internal({
                "input": compressed_input
            })

            raw_output = response["output"]

            match = re.search(r'\{.*\}', raw_output, re.DOTALL)

            if match:
                json_str = match.group(0)
                try:
                    data = json.loads(json_str)
                    return data
                except json.JSONDecodeError:
                    print("Error al parsear JSON del LLM")

            return {
                "summary": raw_output,
                "score": 0,
                "strengths": [],
                "weaknesses": [],
                "suggested_role": "N/A"
                }
        except Exception as e:
            print(f"Error generating insight after retries: {e}")
            return {
                'summary': 'Timeout/Error: Insight generation failed after multiple retries.',
                'score': 0,
                'strengths': [],
                'weaknesses': [],
                'suggested_role': 'N/A'
            }