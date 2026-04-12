import pytest
from fastapi.testclient import TestClient
from cygnal.app.main import app
from cygnal.app.repository import repo


@pytest.fixture(autouse=True)
def clear_repository():
    repo.clear()
    yield
    repo.clear()


@pytest.fixture
def client():
    return TestClient(app)