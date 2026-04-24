from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from agents.base import BaseAgent

_PROMPT = ChatPromptTemplate.from_template(
    """You are MarketResearchAgent. Given the BUSINESS PROFILE below and market context, identify:
1. 3-5 whitespace opportunities (untapped market areas)
2. Top 5 competitors & their core offerings
3. Suggested price brackets
4. Competitive positioning recommendations

=== BUSINESS PROFILE ===
{context}

=== MARKET CONTEXT ===
{web_context}

Format your response in markdown:
## Competitor Analysis for {query}

### Whitespace Opportunities
1. [Opportunity 1] - [Why it's valuable]
2. [Opportunity 2] - [Why it's valuable]

### Top Competitors
| Competitor | Core Offerings | Price Range | Market Position |
|------------|----------------|-------------|-----------------|

### Strategic Recommendations
- [Positioning strategy 1]
- [Positioning strategy 2]
"""
)


class CompetitorAgent(BaseAgent):
    def analyze_competitors(self, query: str, context: str) -> str:
        focused_context = self.get_business_context(query)
        web_context = self.get_web_context(f"competitors for {query}", focused_context)
        chain = _PROMPT | self.llm | StrOutputParser()
        return chain.invoke({"query": query, "context": context, "web_context": web_context})
