import pandas as pd
import streamlit as st

from agents.competitor import CompetitorAgent
from agents.general import GeneralAgent
from agents.newsletter import NewsletterAgent
from agents.pricing import PricingAgent
from agents.supplier import SupplierAgent
from agents.trend import TrendAgent
from core.workflows import get_metrics_workflow


def handle_agent_response(prompt: str, agent_type: str) -> None:
    model = st.session_state.model_name
    context = st.session_state.business_context

    if not context:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Business context not set — please configure in sidebar.",
        })
        return

    if agent_type == "pricing":
        response = PricingAgent(model).analyze_pricing(prompt, context)
        st.session_state.messages.append({"role": "assistant", "content": response})

    elif agent_type == "trend":
        response = TrendAgent(model).analyze_trends(prompt, context)
        st.session_state.messages.append({"role": "assistant", "content": response})

    elif agent_type == "competitor":
        response = CompetitorAgent(model).analyze_competitors(prompt, context)
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"## Competitor & Whitespace Analysis\n{response}",
        })

    elif agent_type == "newsletter":
        response = NewsletterAgent(model).generate_copy(prompt, context)
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"## Marketing Copy\n{response}",
        })

    elif agent_type == "business_metrics":
        _run_metrics_agent(prompt)

    else:
        response = GeneralAgent(model).answer_question(prompt, context)
        st.session_state.messages.append({"role": "assistant", "content": response})


def _run_metrics_agent(prompt: str) -> None:
    business_data = st.session_state.business_data
    if business_data is None or business_data.empty:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "No business data available. Please upload a CSV in the sidebar.",
            "agent_type": "business_metrics",
        })
        return
    if "Date" not in business_data.columns:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Data must contain a 'Date' column.",
            "agent_type": "business_metrics",
        })
        return

    try:
        business_data = business_data.copy()
        business_data["Date"] = pd.to_datetime(business_data["Date"], errors="coerce")
        business_data = business_data.dropna(subset=["Date"]).sort_values("Date")
        historic_json = business_data.to_json(orient="records", date_format="iso")

        result = get_metrics_workflow().invoke({
            "topic": prompt,
            "historic": historic_json,
            "web": "",
            "insights": "",
            "charts": {},
            "key_metrics": {},
            "error": None,
        })
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"## Business Metrics Analysis for '{prompt}'",
            "agent_type": "business_metrics",
            "data": result,
        })
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Error processing data: {e}",
            "agent_type": "business_metrics",
        })


def handle_supplier_request() -> None:
    context = st.session_state.business_context
    if not context:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Business context not set — please configure in sidebar.",
        })
        return

    with st.spinner("Searching global suppliers..."):
        agent = SupplierAgent(st.session_state.model_name)
        suppliers = agent.search_suppliers(
            st.session_state.query,
            st.session_state.specifications,
            st.session_state.locations,
            st.session_state.exclude,
            st.session_state.notes,
            context,
        )

    if suppliers:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"## Supplier Research: {st.session_state.query}",
            "suppliers": suppliers,
        })
    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "No suppliers found. Try broadening your search criteria.",
        })
