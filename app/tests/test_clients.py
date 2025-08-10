import pytest

pytestmark = pytest.mark.asyncio

async def test_create_client(client):
    payload = {
        "name": "Test Client",
        "email": "testclient@example.com",
        "status": "active"
    }
    response = await client.post("/clients/", json=payload)
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data["status"] == payload["status"]
    assert "id" in data

async def test_list_clients(client):
    response = await client.get("/clients/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "name" in data[0]
        assert "email" in data[0]

async def test_update_client(client):
    create_payload = {
        "name": "Client To Update",
        "email": "update@example.com",
        "status": "active"
    }
    create_resp = await client.post("/clients/", json=create_payload)
    client_id = create_resp.json()["id"]

    update_payload = {
        "name": "Client Updated",
        "status": "inactive"
    }
    response = await client.put(f"/clients/{client_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_payload["name"]
    assert data["status"] == update_payload["status"]

async def test_delete_client(client):
    create_payload = {
        "name": "Client To Delete",
        "email": "delete@example.com",
        "status": "active"
    }
    create_resp = await client.post("/clients/", json=create_payload)
    client_id = create_resp.json()["id"]

    response = await client.delete(f"/clients/{client_id}")
    assert response.status_code == 200
    assert response.json()["detail"] == "Client deleted"
