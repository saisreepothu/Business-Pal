from core.llm_factory import get_llm
from core.web_search import search_web
from core.vector_store import retrieve_relevant_context


class BaseAgent:
    def __init__(self, model_name: str = "gpt-4o"):
        self.llm = get_llm(model_name)

    def get_business_context(self, query: str) -> str:
        return retrieve_relevant_context(query)

    def get_web_context(self, query: str, business_context: str) -> str:
        search_query = f"{query} in context of {business_context[:100]}"
        return search_web(search_query)
