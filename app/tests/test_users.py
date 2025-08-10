import pytest

pytestmark = pytest.mark.asyncio

async def test_register_and_login(client):
    register_payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "role": "read"
    }

    response = await client.post("/auth/register", json=register_payload)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["username"] == register_payload["username"]
    assert user_data["email"] == register_payload["email"]
    assert user_data["role"] == register_payload["role"]

    login_payload = {
        "username": register_payload["username"],
        "password": register_payload["password"]
    }
    response = await client.post("/auth/login", data=login_payload)
    assert response.status_code == 200
    login_data = response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
