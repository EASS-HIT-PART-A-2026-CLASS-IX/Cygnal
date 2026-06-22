from frontend.components.indicator_table import SEVERITY_STYLES
from frontend.styles import SEVERITY_COLORS, get_theme_css


def test_theme_css_preserves_streamlit_theme_behavior():
    css = get_theme_css()

    assert "var(--primary-color, #0284c7)" in css
    assert "currentColor" in css
    assert "color:inherit" in css


def test_theme_css_does_not_interfere_with_sidebar_navigation():
    css = get_theme_css()

    assert "data-testid" not in css
    assert "stSidebarNav" not in css
    assert "pointer-events" not in css
    assert "z-index" not in css
    compact_css = css.replace(" ", "")
    assert "position:absolute" not in compact_css
    assert "position:fixed" not in compact_css
    assert 'button[kind="primary"]' not in css


def test_severity_palette_is_consistent_and_low_is_blue():
    assert SEVERITY_COLORS == {
        "critical": "#ef4444",
        "high": "#f97316",
        "medium": "#eab308",
        "low": "#3b82f6",
    }
    assert set(SEVERITY_STYLES) == {"Critical", "High", "Medium", "Low"}
