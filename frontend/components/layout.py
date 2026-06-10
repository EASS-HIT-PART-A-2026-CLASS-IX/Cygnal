import streamlit as st


def render_sidebar_brand() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="cygnal-brand">
                <div class="cygnal-brand-name">CYGNAL</div>
                <div class="cygnal-brand-tagline">Threat Intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_user_card() -> None:
    user = st.session_state.current_user or {}
    st.markdown(
        f"""
        <div class="cygnal-user-card">
            <div class="cygnal-eyebrow">Authenticated session</div>
            <strong>{user.get("username", "Unknown user")}</strong><br>
            <span class="cygnal-user-role" style="font-size:0.82rem">{user.get("role", "unknown").title()} role</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, eyebrow: str = "Cygnal workspace") -> None:
    st.markdown(
        f"""
        <div class="cygnal-hero">
            <div class="cygnal-eyebrow">{eyebrow}</div>
            <div class="cygnal-title">{title}</div>
            <p class="cygnal-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
