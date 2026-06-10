from frontend.styles import get_theme_css


def test_theme_css_follows_streamlit_live_variables():
    css = get_theme_css()

    assert ".stApp {" in css
    assert "--cy-bg: var(--background-color, #071019)" in css
    assert "--cy-sidebar: var(--secondary-background-color, #0b1c29)" in css
    assert "--cy-text: var(--text-color, #f1f5f9)" in css
    assert "--cy-accent: var(--primary-color, #38bdf8)" in css
