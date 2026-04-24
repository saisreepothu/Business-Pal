import numpy as np
import streamlit as st


def render_metrics_selection() -> None:
    if st.session_state.business_data is None:
        return
    numeric_cols = st.session_state.business_data.select_dtypes(
        include=[np.number]
    ).columns.tolist()
    if not numeric_cols:
        st.warning("No numeric metrics found in the uploaded data.")


def render_business_metrics_results(state: dict, unique_id: int) -> None:
    if not state:
        return
    if state.get("error"):
        st.error(f"Error: {state['error']}")
        return

    st.subheader("Historical Trend Charts")
    if state.get("charts"):
        for i, (metric, fig) in enumerate(state["charts"].items()):
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{metric}_{i}_{unique_id}")
    else:
        st.warning("No charts generated.")

    st.subheader("Key Metrics Summary")
    if state.get("key_metrics"):
        for metric, values in state["key_metrics"].items():
            c1, c2, c3 = st.columns(3)
            c1.metric(f"Start — {metric}", f"{values['start']:,.2f}")
            c2.metric(f"End — {metric}", f"{values['end']:,.2f}", f"{values['delta']:,.2f}")
            c3.metric("Growth", f"{values['growth']:.1f}%")
    else:
        st.warning("No key metrics calculated.")

    st.subheader("AI-Generated Insights & Recommendations")
    if state.get("insights"):
        st.markdown(state["insights"])
    else:
        st.warning("No insights generated.")

    st.subheader("Latest Web Trends")
    if state.get("web"):
        st.markdown(state["web"])
    else:
        st.warning("No web trends found.")
