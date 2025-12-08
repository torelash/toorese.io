import streamlit as st


def render_nba():
    st.title("NBA Analysis")
    st.caption("Basketball statistics sandbox")

    st.markdown(
        """
        ### Court Vision Lab

        This space will host:
        * Player impact dashboards
        * Shot charts and spacing maps
        * Lineup and on off exploration
        * Predictive models for performance over the season
        """,
        unsafe_allow_html=False,
    )

    st.info(
        "NBA analytics module coming soon. "
        "I have been a little busy with work, "
        "so i haven't had time to safely develop this."
    )

    st.write("")
    if st.button("⬅ Back to portfolio"):
        st.session_state.active_hobby = None
        st.rerun()
