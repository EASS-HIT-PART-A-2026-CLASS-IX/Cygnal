from mcp.server.fastmcp import FastMCP
from sqlmodel import Session

from backend.db.session import engine
from backend.repositories.indicators import repo


mcp = FastMCP("Cygnal")


def get_active_indicators(limit: int = 20) -> list[dict]:
    with Session(engine) as session:
        indicators = repo.get_all(session, limit=limit, is_active=True)
        return [indicator.model_dump(mode="json") for indicator in indicators]


@mcp.tool()
def list_active_indicators(limit: int = 20) -> list[dict]:
    """List active threat indicators using the same repository as the REST API."""
    return get_active_indicators(limit)


if __name__ == "__main__":
    mcp.run()
