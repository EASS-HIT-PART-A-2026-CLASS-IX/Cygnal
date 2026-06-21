from __future__ import annotations

import ast
from pathlib import Path


DASHBOARD_PATH = Path("frontend/dashboard.py")


def _extract_streamlit_pages() -> list[dict[str, str]]:
    tree = ast.parse(DASHBOARD_PATH.read_text(encoding="utf-8"))

    pages: list[dict[str, str]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and func.attr == "Page"
            and isinstance(func.value, ast.Name)
            and func.value.id == "st"
        ):
            continue

        page: dict[str, str] = {}

        for keyword in node.keywords:
            if keyword.arg in {"title", "url_path", "icon"} and isinstance(keyword.value, ast.Constant):
                page[keyword.arg] = str(keyword.value.value)

        pages.append(page)

    return pages


def test_authenticated_navigation_has_unique_pages():
    pages = _extract_streamlit_pages()

    assert pages

    titles = [page["title"] for page in pages]
    url_paths = [page["url_path"] for page in pages]

    assert len(titles) == len(set(titles))
    assert len(url_paths) == len(set(url_paths))

    assert set(url_paths) == {
        "dashboard",
        "add-indicator",
        "indicators",
        "search",
        "enrichment",
        "reports",
        "administration",
        "settings",
    }