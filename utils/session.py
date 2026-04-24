import streamlit as st
from config.settings import DEFAULT_MODEL


def init_session_state() -> None:
    defaults = {
        "business_context": "",
        "business_data": None,
        "messages": [],
        "model_name": DEFAULT_MODEL,
        "prev_model": DEFAULT_MODEL,
        "specifications": "",
        "locations": [],
        "exclude": [],
        "notes": "",
        "context_file": None,
        "context_text": "",
        "show_supplier_form": False,
        "pinecone_index": None,
        "context_namespace": None,
        "context_chunks": [],
        "web_cache": {},
        "context_set_time": None,
        "context_set": False,
        "context_hash": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
