from __future__ import annotations

import streamlit as st

from frontend.state import authenticate


def render() -> None:
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"], [data-testid="stHeader"] { display: none; }
            .stMainBlockContainer { max-width: 1180px; padding-top: 8vh; }
            .login-brand {
                padding: 3rem 2.5rem;
                border-radius: 16px;
                min-height: 430px;
                box-shadow: 0 24px 60px var(--cy-shadow);
            }
            .login-mark {
                width: 58px;
                height: 58px;
                border: 1px solid var(--cy-accent);
                border-radius: 14px;
                display: grid;
                place-items: center;
                color: var(--cy-accent);
                font-size: 1.5rem;
                font-weight: 800;
                margin-bottom: 1.5rem;
            }
            .login-brand h1 { font-size: 2.6rem; margin-bottom: 0.5rem; }
            .login-brand p { font-size: 1rem; max-width: 32rem; }
            .login-signal {
                color: var(--cy-accent);
                text-transform: uppercase;
                letter-spacing: 0.16em;
                font-size: 0.72rem;
                font-weight: 700;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.15, 0.85], gap="large", vertical_alignment="center")
    with left:
        st.markdown(
            """
            <div class="login-brand">
                <div class="login-mark">C</div>
                <div class="login-signal">Secure intelligence workspace</div>
                <h1>See the signal.<br>Act with confidence.</h1>
                <p>
                    Cygnal centralizes indicators, analysis, reporting, and operational
                    response in one focused threat intelligence platform.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown("### Sign in to Cygnal")
        st.caption("Authenticate to access the intelligence workspace.")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="analyst")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign in", type="primary", width="stretch")
        if submitted:
            if not username or not password:
                st.warning("Enter both username and password.")
                return
            try:
                authenticate(username, password)
                st.rerun()
            except Exception:
                st.error("Authentication failed. Check your credentials and try again.")

        st.markdown("---")
        st.caption("Demo access: `analyst / analyst123` or `admin / admin123`")
