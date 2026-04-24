from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from agents.base import BaseAgent

_PROMPT = ChatPromptTemplate.from_template(
    """You are MarketingCopyAgent. Based on this user request:

"{query}"

And business context:

{context}

And current email marketing trends from web:

{web_context}

Write a clear, catchy but professional marketing email with:

- Subject line
- Email body

Format:

## Subject:
[subject line here]

## Email Body:

[well formatted email body here]
"""
)


class NewsletterAgent(BaseAgent):
    def generate_copy(self, query: str, context: str) -> str:
        business_context = self.get_business_context(query)
        web_context = self.get_web_context(f"email marketing trends for {query}", business_context)
        chain = _PROMPT | self.llm | StrOutputParser()
        return chain.invoke({"query": query, "context": context, "web_context": web_context})
