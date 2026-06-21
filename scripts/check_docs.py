import subprocess
import tempfile
from pathlib import Path


def main() -> None:
    site_dir = Path(tempfile.gettempdir()) / "cygnal-mkdocs"
    command = [
        "uvx",
        "--from",
        "mkdocs-material",
        "mkdocs",
        "build",
        "--strict",
        "--site-dir",
        str(site_dir),
    ]
    raise SystemExit(subprocess.run(command, check=False).returncode)


if __name__ == "__main__":
    main()
