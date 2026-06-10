import streamlit as st


INDICATOR_TYPES = ["All", "IP", "Domain", "URL", "Hash", "Email"]
SEVERITY_LEVELS = ["All", "critical", "high", "medium", "low"]
SEVERITY_COLORS = {"critical": "#ef4444", "high": "#f97316", "medium": "#eab308", "low": "#22c55e"}
CHART_COLORS = {
    **SEVERITY_COLORS,
    "IP": "#38bdf8",
    "Domain": "#2dd4bf",
    "URL": "#fb7185",
    "Hash": "#818cf8",
    "Email": "#c084fc",
}

def get_theme_css() -> str:
    """Return CSS that follows Streamlit's live System, Light, or Dark theme."""
    return f"""{""}
        <style>
            .stApp {{
                --cy-bg: var(--background-color, #071019);
                --cy-sidebar: var(--secondary-background-color, #0b1c29);
                --cy-surface: color-mix(in srgb, var(--secondary-background-color, #0b1c29) 88%, var(--background-color, #071019));
                --cy-surface-alt: var(--secondary-background-color, #0b1c29);
                --cy-surface-soft: color-mix(in srgb, var(--secondary-background-color, #0b1c29) 72%, transparent);
                --cy-border: color-mix(in srgb, var(--text-color, #f1f5f9) 20%, transparent);
                --cy-text: var(--text-color, #f1f5f9);
                --cy-muted: color-mix(in srgb, var(--text-color, #f1f5f9) 65%, transparent);
                --cy-accent: var(--primary-color, #38bdf8);
                --cy-accent-soft: color-mix(in srgb, var(--primary-color, #38bdf8) 14%, transparent);
                --cy-shadow: color-mix(in srgb, var(--text-color, #f1f5f9) 14%, transparent);
            }}
            .stApp {{
                background: radial-gradient(circle at 85% -10%, var(--cy-accent-soft), transparent 32%), var(--cy-bg);
                color: var(--cy-text);
            }}
            [data-testid="stSidebar"] {{
                background: var(--cy-sidebar);
                border-right: 1px solid var(--cy-border);
            }}
            [data-testid="stSidebarNav"] {{ padding-top: .5rem; }}
            [data-testid="stSidebarNav"] a {{ border-radius: 8px; margin: 2px 8px; }}
            [data-testid="stSidebarNav"] a:hover {{ background: var(--cy-accent-soft); }}
            .cygnal-brand {{ padding: .4rem .35rem .8rem; }}
            .cygnal-brand-name {{ color:var(--cy-text); font-size:1.35rem; font-weight:750; letter-spacing:.04em; }}
            .cygnal-brand-tagline, .cygnal-eyebrow {{
                color:var(--cy-accent); font-size:.72rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase;
            }}
            .cygnal-user-card, .cygnal-hero, .login-brand {{
                background:linear-gradient(145deg,var(--cy-surface),var(--cy-surface-alt));
                border:1px solid var(--cy-border); border-radius:12px; box-shadow:0 12px 30px var(--cy-shadow);
            }}
            .cygnal-user-card {{ padding:.8rem .9rem; margin-bottom:.7rem; }}
            .cygnal-user-role, .cygnal-subtitle, .login-brand p {{ color:var(--cy-muted); }}
            .cygnal-hero {{ padding:1.35rem 1.5rem; margin-bottom:1.25rem; }}
            .cygnal-title, .login-brand h1 {{ color:var(--cy-text); }}
            .cygnal-title {{ font-size:2rem; font-weight:760; margin:.25rem 0 .2rem; }}
            .cygnal-subtitle {{ margin:0; }}
            [data-testid="stMetric"] {{
                background:linear-gradient(145deg,var(--cy-surface),var(--cy-surface-alt));
                border:1px solid var(--cy-border); border-radius:10px; padding:.8rem 1rem;
            }}
            [data-testid="stDataFrame"] {{ border:1px solid var(--cy-border); border-radius:10px; overflow:hidden; }}
            .stTabs [data-baseweb="tab-list"] {{ gap:.4rem; }}
            .stTabs [data-baseweb="tab"] {{ background:var(--cy-surface-alt); border-radius:8px; padding:.55rem .9rem; }}
            div[data-testid="stForm"], div[data-testid="stExpander"] {{
                border:1px solid var(--cy-border); border-radius:10px; background:var(--cy-surface-soft);
            }}
            button[kind="primary"] {{
                background:linear-gradient(135deg,#0284c7,#0891b2)!important;
                border-color:#38bdf8!important; color:#f8fafc!important;
            }}
            button[kind="primary"]:hover {{
                background:linear-gradient(135deg,#0369a1,#0e7490)!important; border-color:#7dd3fc!important;
            }}
        </style>
    """


def apply_global_styles() -> None:
    st.markdown(
        get_theme_css(),
        unsafe_allow_html=True,
    )
