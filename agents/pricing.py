from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from agents.base import BaseAgent

_PROMPT = ChatPromptTemplate.from_template(
    """You are PricingStrategistAgent. Given the BUSINESS PROFILE and market context, suggest:
• MSRP to hit target margins
• Promotional / markdown strategies

User request: {query}

=== BUSINESS PROFILE ===
{context}

=== MARKET CONTEXT ===
{web_context}

Provide concrete, actionable pricing recommendations with risk mitigation strategies.
Format your response in clean markdown."""
)


class PricingAgent(BaseAgent):
    def analyze_pricing(self, query: str, context: str) -> str:
        business_context = self.get_business_context(query)
        web_context = self.get_web_context(f"pricing strategies for {query}", business_context)
        chain = _PROMPT | self.llm | StrOutputParser()
        return chain.invoke({"query": query, "context": context, "web_context": web_context})
