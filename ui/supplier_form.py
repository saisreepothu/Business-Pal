import streamlit as st


def render_supplier_form() -> bool:
    with st.expander("Supplier Requirements", expanded=True):
        with st.form("supplier_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.query = st.text_input(
                    "Product / Service *",
                    st.session_state.get("query", ""),
                    placeholder="Wind turbine parts",
                )
                st.session_state.specifications = st.text_area(
                    "Specifications *",
                    st.session_state.get("specifications", ""),
                    placeholder="Technical requirements, certifications, etc.",
                    height=100,
                )
            with col2:
                st.session_state.locations = st.multiselect(
                    "Preferred Locations",
                    ["USA", "Canada", "UK", "Germany", "France", "China", "Japan", "India"],
                    default=st.session_state.get("locations", []),
                )
                st.session_state.notes = st.text_area(
                    "Additional Notes",
                    st.session_state.get("notes", ""),
                    placeholder="Urgency, budget constraints, etc.",
                    height=80,
                )
            submitted = st.form_submit_button("Find Suppliers", use_container_width=True)
            if submitted:
                if st.session_state.query and st.session_state.specifications:
                    return True
                st.error("Please fill in the required fields (marked with *)")
    return False
