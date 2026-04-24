import pandas as pd
import streamlit as st

from config.settings import AVAILABLE_MODELS, DEFAULT_MODEL, MIN_CONTEXT_CHARS
from core.vector_store import get_or_create_pinecone_index
from utils.file_parser import extract_text_from_file


def render_sidebar() -> None:
    st.title("Business Pal")
    st.title("Configuration Your Business Assistant")

    _model_selector()
    st.markdown("---")
    _business_context_section()
    st.markdown("---")
    _business_metrics_section()
    st.markdown("---")
    _agent_capabilities()


# ── Model selector ─────────────────────────────────────────────────────────────

def _model_selector() -> None:
    st.subheader("AI Model")
    model_name = st.selectbox(
        "Select model",
        AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(st.session_state.get("model_name", DEFAULT_MODEL)),
        key="model_selector",
        label_visibility="collapsed",
        help="Select AI model to use for analysis",
    )
    if model_name != st.session_state.prev_model:
        st.session_state.prev_model = model_name
        st.session_state.model_name = model_name
        st.success(f"Model switched to **{model_name}**")
        st.rerun()


# ── Business context ──────────────────────────────────────────────────────────

def _business_context_section() -> None:
    st.subheader("Business Context")

    context_file = st.file_uploader(
        "Upload business document",
        type=["txt", "pdf"],
        help="Upload a TXT or PDF describing your business",
    )

    with st.expander("Sample context templates", expanded=False):
        st.caption("Your context should include: industry, products/services, target customers, competitive advantages, and goals.")
        industry = st.selectbox(
            "Quick sample",
            ["Eco-Fashion", "SaaS", "Coffee", "Restaurant"],
            key="sample_ctx_industry",
        )
        samples = {
            "Eco-Fashion": """GreenThread Apparel
Industry: Sustainable Fashion
Products: Organic cotton apparel
Target: Eco-conscious millennials
Goals: 30% YOY growth, EU expansion
Advantage: Carbon-neutral shipping""",
            "SaaS": """FlowStack Technologies
Industry: B2B Software
Product: AI productivity platform
Target: Tech teams (50-500 employees)
Pricing: $15/user/month
Goal: 10K MAU by EOY""",
            "Coffee": """Mountain Peak Coffee
Industry: Specialty Coffee
Products: Single-origin beans
Target: Urban professionals
Advantage: Direct trade farmers
Goal: 40% subscription growth""",
            "Restaurant": """Urban Bistro
Industry: Casual Dining
Cuisine: Farm-to-table
Target: Foodies (25-45)
Advantage: Locally sourced ingredients
Goal: Expand catering by 25%""",
        }
        st.code(samples[industry], language="text")

    if context_file:
        try:
            extracted = extract_text_from_file(context_file)
            if len(extracted) > MIN_CONTEXT_CHARS:
                st.session_state.context_text = extracted
                st.session_state.context_file = context_file
                st.success("Document loaded — click **Set Context** to index it.")
            else:
                st.warning(f"Document too short (min {MIN_CONTEXT_CHARS} characters).")
        except Exception as e:
            st.error(f"Error processing file: {e}")

    manual = st.text_area(
        "Or describe your business:",
        value=st.session_state.context_text,
        height=140,
        placeholder="We sell eco-friendly products...",
        help=f"Minimum {MIN_CONTEXT_CHARS} characters",
    )
    if manual != st.session_state.context_text:
        st.session_state.context_text = manual
        st.session_state.context_file = None

    if st.session_state.context_set:
        st.success("Business context is active and indexed.")
    else:
        st.info("Business context not set yet.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Set Context", use_container_width=True, key="set_context"):
            _index_context()
    with col2:
        if st.button("Clear", use_container_width=True, key="clear_context"):
            _clear_context()


def _index_context() -> None:
    text = st.session_state.context_text
    if len(text) < MIN_CONTEXT_CHARS:
        st.error(f"Please provide at least {MIN_CONTEXT_CHARS} characters.")
        return
    try:
        with st.spinner("Indexing business context..."):
            vector_store, namespace = get_or_create_pinecone_index(text)
            st.session_state.pinecone_index = vector_store
            st.session_state.context_namespace = namespace
            st.session_state.business_context = text
            st.session_state.context_hash = namespace
            st.session_state.context_set = True
        st.success("Context indexed successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Indexing error: {e}")


def _clear_context() -> None:
    for key in ("business_context", "context_text", "context_file", "pinecone_index",
                "context_namespace", "context_set", "context_hash"):
        st.session_state[key] = None if "index" in key or "namespace" in key or "hash" in key else ""
    st.session_state.context_set = False
    st.info("Context cleared.")


# ── Business metrics ──────────────────────────────────────────────────────────

def _business_metrics_section() -> None:
    st.subheader("Business Metrics")

    data_file = st.file_uploader(
        "Upload metrics CSV",
        type=["csv"],
        help="Must include a 'Date' column and at least two numeric metrics",
    )

    industry = st.selectbox(
        "Download sample template",
        ["E-Commerce", "SaaS", "Restaurant", "Retail"],
        key="sample_industry",
    )
    sample_data = _build_sample_data(industry)
    st.download_button(
        "Download Sample CSV",
        data=sample_data.to_csv(index=False).encode("utf-8"),
        file_name=f"{industry}_sample.csv",
        mime="text/csv",
        use_container_width=True,
    )

    with st.expander("CSV format guide", expanded=False):
        st.markdown("""
**Required**: `Date` column (YYYY-MM-DD) + at least 2 numeric metrics.

```csv
Date,Revenue,Traffic
2024-01-01,45000,120000
2024-02-01,52000,145000
```
        """)

    if data_file:
        try:
            st.session_state.business_data = pd.read_csv(data_file)
            st.success("Data uploaded successfully!")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    if st.button("Clear Data", use_container_width=True):
        st.session_state.business_data = None
        st.info("Data cleared.")


def _build_sample_data(industry: str) -> pd.DataFrame:
    samples = {
        "E-Commerce": pd.DataFrame({
            "Date": ["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01"],
            "Revenue": [45000, 52000, 61000, 58500],
            "Website Traffic": [120000, 145000, 162000, 158000],
            "Conversion Rate": [2.1, 2.3, 2.5, 2.4],
            "Return Rate": [4.2, 3.8, 3.5, 4.0],
        }),
        "SaaS": pd.DataFrame({
            "Date": ["2024-01-08", "2024-01-15", "2024-01-22", "2024-01-29"],
            "Active Users": [1250, 1380, 1470, 1620],
            "Paid Conversions": [35, 42, 38, 45],
            "Churn Rate": [1.2, 1.1, 1.0, 0.9],
            "ARR": [185000, 192500, 201000, 218000],
        }),
        "Restaurant": pd.DataFrame({
            "Date": ["2024-05-01", "2024-05-02", "2024-05-03", "2024-05-04"],
            "Foot Traffic": [320, 290, 410, 480],
            "Avg Ticket Size": [24.50, 26.10, 22.80, 27.40],
            "Food Cost Pct": [28, 30, 26, 27],
            "Online Orders": [85, 92, 103, 121],
        }),
        "Retail": pd.DataFrame({
            "Date": ["2024-06-01", "2024-06-08", "2024-06-15", "2024-06-22"],
            "Sales": [12500, 14200, 13850, 16100],
            "Foot Traffic": [420, 380, 410, 510],
            "Avg Basket Size": [45.20, 48.10, 42.50, 46.80],
            "Conversion Rate": [22.5, 24.1, 21.8, 23.7],
        }),
    }
    return samples.get(industry, samples["E-Commerce"])


# ── Agent capability reference ─────────────────────────────────────────────────

def _agent_capabilities() -> None:
    st.subheader("Agent Capabilities")
    st.markdown("""
| Agent | What it does |
|-------|-------------|
| **Supplier** | Global vendor research & qualification |
| **Pricing** | MSRP, margins & promotional strategy |
| **Trend** | Market forecasting & emerging trends |
| **Competitor** | Benchmarking & whitespace opportunities |
| **Newsletter** | Marketing email & campaign copy |
| **Metrics** | KPI analysis & performance charts |
| **General** | Any other business question |
    """)
