from typing import Generator
import pytest
from fastapi import requests
from pytest import fixture
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def test_health() -> Generator[TestClient, None, None]:
    client = TestClient(app)
    yield client
