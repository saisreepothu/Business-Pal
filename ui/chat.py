import streamlit as st

from agents.dispatcher import handle_agent_response
from core.workflows import get_supervisor_workflow
from ui.metrics import render_business_metrics_results


def render_chat() -> None:
    _display_history()
    _handle_input()


def _display_history() -> None:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg.get("agent_type") == "business_metrics" and msg.get("data"):
                render_business_metrics_results(msg["data"], i)

            if "suppliers" in msg:
                suppliers = msg["suppliers"]
                st.markdown(f"**Found {len(suppliers)} supplier(s)**")
                for j, s in enumerate(suppliers):
                    with st.expander(f"{j + 1}. {s['name']} — {s['type']}"):
                        cols = st.columns([2, 1])
                        with cols[0]:
                            st.markdown(f"**Website**: [{s['website']}]({s['website']})")
                            st.caption(s["description"])
                        with cols[1]:
                            st.markdown(f"**HQ**: {s['hq']}")
                            st.markdown(f"**Type**: {s['type']}")


def _handle_input() -> None:
    prompt = st.chat_input("Ask about your business...")
    if not prompt:
        return

    if not st.session_state.business_context:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Please set your business context in the sidebar before asking questions.",
        })
        st.rerun()
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.query = prompt

    supervisor_state = {
        "query": prompt,
        "context": st.session_state.business_context,
        "model_name": st.session_state.model_name,
        "agent_type": "unknown",
        "specifications": st.session_state.get("specifications", ""),
        "locations": st.session_state.get("locations", []),
        "exclude": [],
        "notes": st.session_state.get("notes", ""),
        "results": None,
        "feedback": "",
        "needs_data": False,
    }

    result = get_supervisor_workflow().invoke(supervisor_state)
    st.session_state.supervisor_state = result
    agent_type = result["agent_type"]

    if agent_type == "supplier":
        if result.get("needs_data"):
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Please scroll up and fill in the Supplier Requirements form.",
            })
            st.session_state.show_supplier_form = True
        else:
            st.rerun()
    elif agent_type == "business_metrics":
        if result.get("needs_data"):
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Please upload your business metrics CSV in the sidebar.",
            })
        else:
            with st.spinner("Analyzing business metrics..."):
                handle_agent_response(prompt, agent_type)
    else:
        with st.spinner("Analyzing..."):
            handle_agent_response(prompt, agent_type)

    st.rerun()
