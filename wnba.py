import streamlit as st


def render_wnba():
    st.title("WNBA Analysis")
    st.caption("Women basketball analytics lab")

    st.markdown(
        """
        ### W Vision Studio

        This space will host:
        * Player and team dashboards
        * Salary and cap experiments
        * Shot and spacing visualizations
        * Win probability and playoff scenarios
        """,
        unsafe_allow_html=False,
    )

    st.info(
        "WNBA analytics module coming soon. "
        "I have been a little busy with work, "
        "so i haven't had time to safely develop this."
    )

    st.write("")
    if st.button("⬅ Back to portfolio"):
        st.session_state.active_hobby = None
        st.rerun()
