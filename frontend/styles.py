import streamlit as st


INDICATOR_TYPES = ["All", "IP", "Domain", "URL", "Hash", "Email"]
SEVERITY_LEVELS = ["All", "critical", "high", "medium", "low"]
SEVERITY_COLORS = {"critical": "#ef4444", "high": "#f97316", "medium": "#eab308", "low": "#3b82f6"}
CHART_COLORS = {
    **SEVERITY_COLORS,
    "IP": "#38bdf8",
    "Domain": "#2dd4bf",
    "URL": "#fb7185",
    "Hash": "#818cf8",
    "Email": "#c084fc",
}


def get_theme_css() -> str:
    """Style Cygnal-owned elements while preserving Streamlit theme behavior."""
    return """
        <style>
            .cygnal-brand { padding: .4rem .35rem .8rem; }
            .cygnal-brand-name { color:inherit; font-size:1.35rem; font-weight:750; letter-spacing:.04em; }
            .cygnal-brand-tagline, .cygnal-eyebrow {
                color:var(--primary-color, #0284c7); font-size:.72rem; font-weight:700;
                letter-spacing:.14em; text-transform:uppercase;
            }
            .cygnal-user-card, .cygnal-hero, .login-brand {
                color:inherit;
                background:color-mix(in srgb,currentColor 4%,transparent);
                border:1px solid color-mix(in srgb,currentColor 20%,transparent);
                border-radius:12px;
                box-shadow:0 12px 30px color-mix(in srgb,currentColor 12%,transparent);
            }
            .cygnal-user-card { padding:.8rem .9rem; margin-bottom:.7rem; }
            .cygnal-user-role, .cygnal-subtitle, .login-brand p { color:inherit; opacity:.72; }
            .cygnal-hero { padding:1.35rem 1.5rem; margin-bottom:1.25rem; }
            .cygnal-title, .login-brand h1 { color:inherit; }
            .cygnal-title { font-size:2rem; font-weight:760; margin:.25rem 0 .2rem; }
            .cygnal-subtitle { margin:0; }
        </style>
    """


def apply_global_styles() -> None:
    st.markdown(get_theme_css(), unsafe_allow_html=True)
