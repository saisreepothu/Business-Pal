from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from agents.base import BaseAgent

_PROMPT = ChatPromptTemplate.from_template(
    """As a market analyst, identify key trends for:
Industry: {query}
Business Context: {context}
Market Context from Web: {web_context}

Provide in markdown format:
## Market Trends

### Emerging Trends
1. [Trend 1]
2. [Trend 2]
3. [Trend 3]

### Impact Analysis
| Trend | Opportunity Level | Business Impact |
|-------|-------------------|-----------------|

### Strategic Recommendations
- [Initiative 1]
- [Initiative 2]"""
)


class TrendAgent(BaseAgent):
    def analyze_trends(self, query: str, context: str) -> str:
        focused_context = self.get_business_context(query)
        web_context = self.get_web_context(f"market trends for {query}", focused_context)
        chain = _PROMPT | self.llm | StrOutputParser()
        return chain.invoke({"query": query, "context": context, "web_context": web_context})
