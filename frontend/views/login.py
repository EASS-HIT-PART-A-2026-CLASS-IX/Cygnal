from __future__ import annotations

import streamlit as st

from frontend.state import authenticate


def render() -> None:
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"], [data-testid="stHeader"] { display: none; }

            .stMainBlockContainer {
                max-width: 1180px;
                padding-top: 8vh;
            }

            .login-brand {
                --login-accent: var(--cy-accent, var(--primary-color, #38bdf8));
                padding: 3rem 2.5rem;
                border-radius: 16px;
                min-height: 430px;
                box-shadow: 0 24px 60px var(--cy-shadow);
            }

            .login-mark {
                width: fit-content;
                min-width: 198px;
                padding: 0.82rem 1rem;
                border: 1px solid color-mix(in srgb, var(--login-accent) 55%, transparent);
                border-radius: 16px;
                display: inline-flex;
                align-items: center;
                gap: 0.9rem;
                color: var(--login-accent);
                background: color-mix(in srgb, var(--login-accent) 8%, transparent);
                margin-bottom: 1.6rem;
            }

            .login-mark-signal {
                position: relative;
                width: 42px;
                height: 42px;
                border-radius: 12px;
                border: 1px solid color-mix(in srgb, var(--login-accent) 60%, transparent);
                flex: 0 0 auto;
                overflow: hidden;
            }

            .login-mark-dot {
                position: absolute;
                left: 10px;
                top: 50%;
                transform: translateY(-50%);
                width: 7px;
                height: 7px;
                border-radius: 999px;
                background: var(--login-accent);
                box-shadow: 0 0 14px color-mix(in srgb, var(--login-accent) 75%, transparent);
            }

            .login-mark-wave {
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                border: 2px solid var(--login-accent);
                border-left-color: transparent;
                border-top-color: transparent;
                border-bottom-color: transparent;
                border-radius: 50%;
            }

            .login-mark-wave-1 {
                left: 9px;
                width: 18px;
                height: 18px;
                opacity: 0.95;
            }

            .login-mark-wave-2 {
                left: 5px;
                width: 28px;
                height: 28px;
                opacity: 0.68;
            }

            .login-mark-wave-3 {
                left: 1px;
                width: 38px;
                height: 38px;
                opacity: 0.42;
            }

            .login-mark-text {
                display: flex;
                flex-direction: column;
                line-height: 1;
            }

            .login-mark-name {
                font-family: "Inter", "Segoe UI", "Arial", sans-serif;
                font-size: 1.08rem;
                font-weight: 850;
                letter-spacing: 0.14em;
                text-transform: uppercase;
            }

            .login-mark-tagline {
                margin-top: 0.38rem;
                font-family: "Inter", "Segoe UI", "Arial", sans-serif;
                font-size: 0.58rem;
                font-weight: 750;
                letter-spacing: 0.24em;
                text-transform: uppercase;
                opacity: 0.82;
            }

            .login-brand h1 {
                font-size: 2.6rem;
                margin-bottom: 0.5rem;
            }

            .login-brand p {
                font-size: 1rem;
                max-width: 32rem;
            }

            .login-signal {
                color: var(--login-accent);
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
                <div class="login-mark" aria-label="Cygnal logo">
                    <div class="login-mark-signal" aria-hidden="true">
                        <div class="login-mark-dot"></div>
                        <div class="login-mark-wave login-mark-wave-1"></div>
                        <div class="login-mark-wave login-mark-wave-2"></div>
                        <div class="login-mark-wave login-mark-wave-3"></div>
                    </div>
                    <div class="login-mark-text">
                        <div class="login-mark-name">CYGNAL</div>
                        <div class="login-mark-tagline">THREAT INTEL</div>
                    </div>
                </div>
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
