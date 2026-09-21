import streamlit as st
from services.persistence.exercise_repository import get_or_create_user


def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True

    # =====================================================
    # VISUAL HEADER ONLY
    # =====================================================

    st.markdown(
        '<div class="hero-eyebrow">● AI GYM COACH / REAL-TIME</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-title">
            YOUR BODY.<br>
            <span>INTELLIGENCE.</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-description">
            Real-time movement intelligence that watches your form,
            counts every rep, and understands which muscles you're training.
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # VISUAL STATS ONLY
    # =====================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="micro-stat">
                <div class="micro-value">24/7</div>
                <div class="micro-label">AI COACH</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="micro-stat">
                <div class="micro-value">REAL</div>
                <div class="micro-label">TIME FORM</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="micro-stat">
                <div class="micro-value">3D</div>
                <div class="micro-label">MUSCLE MAP</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # =====================================================
    # VISUAL LOGIN INTRO
    # =====================================================

    st.markdown(
        """
        <div class="login-intro">
            <div class="login-kicker">START TRAINING</div>
            <div class="login-heading">Create your session</div>
            <div class="login-copy">
                Your workout data stays connected to your profile.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # ORIGINAL LOGIN LOGIC
    # =====================================================

    with st.form("login_form", clear_on_submit=False):

        username = st.text_input(
            "Name (unique)",
            placeholder="unique name e.g. princekhunt"
        )

        submit_button = st.form_submit_button(
            "Start Session",
            use_container_width=True
        )

    if submit_button:
        if not username:
            st.error("Name cannot be empty.")
            return False
        
        user = get_or_create_user(username)
    
        st.session_state["user_id"] = user["id"]
        st.session_state["username"] = user["username"]

        st.rerun()

    return False