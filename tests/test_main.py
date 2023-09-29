import pytest
from fastapi.testclient import TestClient

from app.db.models import User
from app.main import app
from tests.conftest import Localsession

client = TestClient(app)

def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'status_code': 200, 'detail': 'ok', 'result': 'working'}


@pytest.mark.asyncio
def test_create_user():
    with Localsession() as session:
        try:
            user_data = {
                "email": "testemail@gmail.com",
                "firstname": "John",
                "lastname": "Doe",
                "hashed_password": "hashed_password_here",
                "city": "Some City",
                "phone": 38085432345
            }
            response = client.post("/users/add", json=user_data)
            assert response.status_code == 200
            created_user = response.json()
            assert created_user["email"] == "testemail@gmail.com"
        finally:
            session.query(User).filter(User.email == "testemail@gmail.com").delete(synchronize_session=False)
            session.commit()


@pytest.mark.asyncio
def test_delete_user():
    with Localsession() as session:
        try:
            user_data = {
                "email": "testemail@gmail.com",
                "firstname": "John",
                "lastname": "Doe",
                "hashed_password": "hashed_password_here",
                "city": "Some City",
                "phone": 38085432345
            }
            user = User(**user_data)
            session.add(user)
            session.commit()

            user_id = user.id

            response = client.delete(f"/users/{user_id}/delete")
            assert response.status_code == 200
        finally:
            session.rollback()
            session.close()


@pytest.mark.asyncio
async def test_get_all_users():
    response = client.get("/users")
    assert response.status_code == 200


@pytest.mark.asyncio
def test_get_user():
    # Create a user in the test database
    with Localsession() as session:
        try:
            user_data = {
                "email": "testemail@gmail.com",
                "firstname": "John",
                "lastname": "Doe",
                "hashed_password": "hashed_password_here",
                "city": "Some City",
                "phone": 38085432345
            }
            user = User(**user_data)
            session.add(user)
            session.commit()

            user_id = user.id

            response = client.get(f"/users/{user_id}/get")

            assert response.status_code == 200
        finally:
            session.query(User).filter(User.email == "testemail@gmail.com").delete(synchronize_session=False)
            session.commit()


@pytest.mark.asyncio
def test_update_user():
    # Create a user in the test database
    with Localsession() as session:
        try:
            user_data = {
                "email": "testemail@gmail.com",
                "firstname": "John",
                "lastname": "Doe",
                "hashed_password": "hashed_password_here",
                "city": "Some City",
                "phone": 38085432345
            }
            user = User(**user_data)
            session.add(user)
            session.commit()

            user_id = user.id

            update_data = {
                "email": "newemail@example.com"
            }
            response = client.patch(f"/users/{user_id}/update", json=update_data)

            assert response.status_code == 200

        finally:
            session.query(User).filter(User.email == "testemail@gmail.com").delete(synchronize_session=False)
            session.commit()


@pytest.mark.asyncio
def test_get_user():
    user_id = 1000
    response = client.get(f"/users/{user_id}/get")
    assert response.status_code == 404
