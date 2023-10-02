from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import settings

SQLALCHEMY_DATABASE_URL_SYNC = settings.database_url_for_test

engine = create_engine(SQLALCHEMY_DATABASE_URL_SYNC, echo=True)

Localsession = sessionmaker(engine, expire_on_commit=False)


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    yield TestClient(app)

