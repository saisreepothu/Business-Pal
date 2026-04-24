from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from agents.base import BaseAgent

_PROMPT = ChatPromptTemplate.from_template(
    """You are an AI Business Builder assistant. Your role is to help entrepreneurs and business leaders
make informed decisions. Answer the user's question using the business context and current market insights.

### Business Context
{business_context}

### Market Insights (Web Search)
{web_context}

### User Question
{query}

If the question is unclear or unrelated to business, answer helpfully based on your general knowledge."""
)


class GeneralAgent(BaseAgent):
    def answer_question(self, query: str, business_context: str) -> str:
        ctx = self.get_business_context(query)
        web_context = self.get_web_context(query, ctx)
        chain = _PROMPT | self.llm | StrOutputParser()
        return chain.invoke({"query": query, "business_context": ctx, "web_context": web_context})
