import json

from scripts.indicators_mcp import get_active_indicators


def main() -> None:
    result = get_active_indicators(limit=3)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
