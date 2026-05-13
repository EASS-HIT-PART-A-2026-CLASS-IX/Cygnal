import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.repository import repo


@pytest.fixture(autouse=True)
def clear_repository():
    repo.clear()
    yield
    repo.clear()


@pytest.fixture
def client():
    return TestClient(app)