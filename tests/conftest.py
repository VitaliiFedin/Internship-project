from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def test_health() -> Generator[TestClient, None, None]:
    yield TestClient(app)
