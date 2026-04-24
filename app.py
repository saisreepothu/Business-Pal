import streamlit as st

from agents.dispatcher import handle_supplier_request
from ui.chat import render_chat
from ui.metrics import render_metrics_selection
from ui.sidebar import render_sidebar
from ui.styles import inject_css
from ui.supplier_form import render_supplier_form
from utils.session import init_session_state


def main() -> None:
    st.set_page_config(
        page_title="Business-Pal",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/saisree27/Business-Pal",
            "Report a bug": "https://github.com/saisree27/Business-Pal/issues",
            "About": "Business-Pal — AI-powered Business Intelligence Suite",
        },
    )

    inject_css()
    init_session_state()

    with st.sidebar:
        render_sidebar()

    st.title("Business-Pal")
    st.caption("AI-powered Business Intelligence Suite · Supplier · Pricing · Trends · Competitors · Metrics")

    if st.session_state.context_set:
        preview = st.session_state.business_context[:220].replace("\n", " ")
        st.success(f"**Active context** — {preview}...")
    else:
        st.warning(
            "**Getting started** — Set your business context in the sidebar to enable AI assistance."
        )

    if st.session_state.business_data is not None:
        render_metrics_selection()

    if st.session_state.show_supplier_form:
        if render_supplier_form():
            if not st.session_state.business_context:
                st.error("Please set your business context before searching for suppliers.")
            else:
                handle_supplier_request()
                st.session_state.show_supplier_form = False
                st.rerun()

    st.markdown("---")
    render_chat()


if __name__ == "__main__":
    main()
