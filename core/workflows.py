from typing import Any, Dict, List, Literal, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from core.llm_factory import get_llm
from core.web_search import search_web


# ── State schemas ─────────────────────────────────────────────────────────────

class SupervisorState(TypedDict):
    query: str
    context: str
    model_name: str
    agent_type: Literal[
        "supplier", "pricing", "trend", "business_metrics",
        "general", "competitor", "newsletter", "unknown"
    ]
    specifications: Optional[str]
    locations: Optional[List[str]]
    exclude: Optional[List[str]]
    notes: Optional[str]
    results: Any
    feedback: str
    needs_data: bool


class BusinessMetricsState(TypedDict):
    topic: str
    historic: str
    web: str
    insights: str
    charts: Dict[str, Any]
    key_metrics: Dict[str, Any]
    error: Optional[str]


# ── Supervisor workflow ────────────────────────────────────────────────────────

@st.cache_resource
def get_supervisor_workflow():
    """Compiled once per server process — safe to cache (state passed at invoke time)."""

    def classify_intent(state: SupervisorState):
        prompt = f"""
        Classify this business query into exactly one category:
        {state['query']}

        Categories:
        - supplier: Sourcing vendors, manufacturers, supply chain partners
        - pricing: Product pricing, cost analysis, pricing strategies
        - trend: Market trends, industry forecasts, emerging developments
        - competitor: Competitor analysis, whitespace opportunities, competitive benchmarking
        - business_metrics: Business performance, KPIs, data analysis, historical metrics
        - newsletter: Marketing emails, newsletters, promotional content
        - general: General business advice, strategy, or other non-specific queries

        Respond ONLY with the category name.
        """
        llm = get_llm(state.get("model_name", "gpt-4o"))
        response = llm.invoke([
            SystemMessage(content="You are a business intelligence routing specialist"),
            HumanMessage(content=prompt),
        ])
        return {**state, "agent_type": response.content.lower().strip()}

    def route_node(state: SupervisorState):
        business_data = st.session_state.get("business_data")
        business_data_empty = business_data is None or (
            hasattr(business_data, "empty") and business_data.empty
        )
        agent_type = state["agent_type"]

        if agent_type == "supplier":
            if not state.get("specifications") or not state.get("locations"):
                st.session_state.show_supplier_form = True
                return {**state, "feedback": "Need more details", "needs_data": True}
            return {**state, "results": "SUPPLIER_AGENT"}
        elif agent_type == "pricing":
            return {**state, "results": "PRICING_AGENT"}
        elif agent_type == "competitor":
            return {**state, "results": "COMPETITOR_AGENT"}
        elif agent_type == "trend":
            return {**state, "results": "TREND_AGENT"}
        elif agent_type == "newsletter":
            return {**state, "results": "NEWSLETTER_AGENT"}
        elif agent_type == "business_metrics":
            if business_data_empty:
                return {**state, "feedback": "Need business metrics data", "needs_data": True}
            return {**state, "results": "BUSINESS_METRICS_AGENT"}
        else:
            return {**state, "agent_type": "general", "results": "GENERAL_AGENT"}

    workflow = StateGraph(SupervisorState)
    workflow.add_node("classify", classify_intent)
    workflow.add_node("route", route_node)
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "route")
    workflow.add_edge("route", END)
    return workflow.compile()


# ── Business metrics workflow ─────────────────────────────────────────────────

@st.cache_resource
def get_metrics_workflow():
    """Compiled once per server process."""

    trend_prompt = PromptTemplate.from_template("""
    You are a predictive AI agent analyzing business trends.
    Given the historical data and the latest trends from the web, provide:
    1. A summary of historical performance.
    2. Key trend shifts.
    3. Forecasted developments.
    4. Strategic insights & suggested actions.

    Historical Data:
    {historic}

    Recent Web Trends:
    {web}

    Respond in a markdown bullet-point format.
    """)

    def fetch_web_trends(state: BusinessMetricsState):
        return {**state, "web": search_web(state["topic"])}

    def analyze_trends(state: BusinessMetricsState):
        llm = get_llm(st.session_state.get("model_name", "gpt-4o"))
        # LCEL — replaces deprecated LLMChain
        chain = trend_prompt | llm | StrOutputParser()
        insights = chain.invoke({"historic": state["historic"], "web": state["web"]})
        return {**state, "insights": insights}

    def generate_charts_and_metrics(state: BusinessMetricsState):
        try:
            df = pd.read_json(state["historic"])
            if df.empty:
                return {**state, "error": "No data in uploaded file"}
            if "Date" not in df.columns:
                return {**state, "error": "Data must contain a 'Date' column"}

            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_cols:
                return {**state, "error": "No numeric metrics found"}

            llm = get_llm(st.session_state.get("model_name", "gpt-4o"))
            selection_prompt = (
                f"You are a business intelligence analyst. Numeric columns: {', '.join(numeric_cols)}\n"
                f"User query: \"{state['topic']}\"\n"
                "Select 2-5 most relevant metrics for trend visualization.\n"
                "Return ONLY a comma-separated list. Example: Revenue,Active Users"
            )
            response = llm.invoke([
                SystemMessage(content="You are a data visualization expert"),
                HumanMessage(content=selection_prompt),
            ])
            selected = [m.strip() for m in response.content.split(",") if m.strip() in numeric_cols]
            if not selected:
                selected = numeric_cols[: min(3, len(numeric_cols))]

            charts: Dict[str, Any] = {}
            key_metrics: Dict[str, Any] = {}

            for metric in selected:
                fig = px.line(df, x="Date", y=metric, title=f"{metric} Trend", markers=True)
                fig.update_layout(
                    height=400,
                    xaxis_title="Date",
                    yaxis_title=metric,
                    hovermode="x unified",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=20, r=20, t=60, b=20),
                    font=dict(family="Inter, sans-serif"),
                )
                charts[metric] = fig

                col = pd.to_numeric(df[metric], errors="coerce").dropna()
                if col.empty:
                    continue
                start_val, end_val = col.iloc[0], col.iloc[-1]
                delta = end_val - start_val
                growth = (delta / start_val) * 100 if start_val != 0 else 0
                key_metrics[metric] = {
                    "start": start_val, "end": end_val,
                    "delta": delta, "growth": growth,
                }

            return {**state, "charts": charts, "key_metrics": key_metrics}
        except Exception as e:
            return {**state, "error": f"Data processing error: {e}"}

    workflow = StateGraph(BusinessMetricsState)
    workflow.add_node("fetch_web_trends", fetch_web_trends)
    workflow.add_node("analyze_trends", analyze_trends)
    workflow.add_node("generate_charts", generate_charts_and_metrics)
    workflow.set_entry_point("fetch_web_trends")
    workflow.add_edge("fetch_web_trends", "analyze_trends")
    workflow.add_edge("analyze_trends", "generate_charts")
    workflow.add_edge("generate_charts", END)
    return workflow.compile()
