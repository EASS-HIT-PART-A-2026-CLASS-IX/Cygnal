from sqlmodel import SQLModel, Session, create_engine

from backend.core.config import settings


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)


def create_db_and_tables() -> None:
    """Create database tables that do not already exist."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Provide one database session per request."""
    with Session(engine) as session:
        yield session
