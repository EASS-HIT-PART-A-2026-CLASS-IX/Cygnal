from frontend.components.indicator_table import SEVERITY_STYLES
from frontend.styles import SEVERITY_COLORS, get_theme_css


def test_theme_css_follows_streamlit_live_variables():
    css = get_theme_css()

    assert ".stApp {" in css
    assert "--cy-bg: var(--background-color, #071019)" in css
    assert "--cy-sidebar: var(--secondary-background-color, #0b1c29)" in css
    assert "--cy-text: var(--text-color, #f1f5f9)" in css
    assert "--cy-accent: var(--primary-color, #38bdf8)" in css


def test_severity_palette_is_consistent_and_low_is_blue():
    assert SEVERITY_COLORS == {
        "critical": "#ef4444",
        "high": "#f97316",
        "medium": "#eab308",
        "low": "#3b82f6",
    }
    assert set(SEVERITY_STYLES) == {"Critical", "High", "Medium", "Low"}
