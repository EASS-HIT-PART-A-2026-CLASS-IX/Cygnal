import os
import subprocess
import tempfile
from pathlib import Path


TEMP_ROOT = Path(tempfile.gettempdir()) / "cygnal-release"
API_URL = os.getenv("CYGNAL_API_URL", "http://127.0.0.1:8000").rstrip("/")
COMMANDS = [
    ["uv", "sync", "--frozen", "--no-install-project"],
    ["uvx", "ruff", "check", ".", "--no-cache"],
    ["uvx", "ruff", "format", "--check", ".", "--no-cache"],
    [
        "uvx",
        "--from",
        "mypy==1.19.1",
        "mypy",
        "backend",
        "frontend",
        "ai_analyst",
        "worker",
        "scripts",
        "--ignore-missing-imports",
        "--check-untyped-defs",
    ],
    [
        "uv",
        "run",
        "--no-sync",
        "--with",
        "pytest-cov",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "--cov=backend",
        "--cov=frontend",
        "--cov=ai_analyst",
        "--cov=worker",
        "--cov=scripts",
        "--cov-report=term-missing",
    ],
    [
        "uvx",
        "schemathesis",
        "run",
        f"{API_URL}/openapi.json",
        "--checks",
        "status_code_conformance,response_schema_conformance",
        "--include-method",
        "GET",
        "--exclude-path",
        "/auth/me",
        "--phases",
        "coverage,fuzzing",
        "--max-examples",
        "5",
        "--generation-database",
        ":memory:",
    ],
    ["uvx", "--from", "mkdocs-material", "mkdocs", "build", "--strict", "--site-dir", str(TEMP_ROOT / "mkdocs")],
    ["uv", "run", "--no-sync", "--with", "pdoc", "pdoc", "backend", "-o", str(TEMP_ROOT / "pdoc")],
    [
        "uv",
        "run",
        "--no-sync",
        "--with",
        "mcp[cli]>=1.1.0",
        "python",
        "-m",
        "scripts.mcp_probe",
    ],
]


def main() -> None:
    environment = {
        **os.environ,
        "COVERAGE_FILE": str(TEMP_ROOT / ".coverage"),
        "PYTHONUTF8": "1",
        "RUFF_CACHE_DIR": str(TEMP_ROOT / "ruff-cache"),
        "UV_PROJECT_ENVIRONMENT": str(TEMP_ROOT / ".venv"),
    }
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    for command in COMMANDS:
        print(f"\n$ {' '.join(command)}")
        completed = subprocess.run(command, check=False, env=environment)
        if completed.returncode:
            raise SystemExit(completed.returncode)
    print("\nRelease checks passed.")


if __name__ == "__main__":
    main()
