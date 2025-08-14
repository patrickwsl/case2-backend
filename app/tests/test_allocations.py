import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import date

from app.main import app

client = TestClient(app)


# -------------------- Mocks --------------------

@pytest.fixture(autouse=True)
def mock_get_asset_price():
    with patch("app.repositories.allocations.assets_repo.get_asset_price", return_value=100.0):
        yield


@pytest.fixture
def fake_client():
    return {
        "id": 1,
        "name": "Client Test",
        "email": "client@test.com",
        "is_active": True
    }


@pytest.fixture
def fake_asset():
    return {
        "id": 1,
        "ticker": "TEST",
        "name": "Test Asset"
    }


@pytest.fixture
def fake_allocation(fake_client, fake_asset):
    return {
        "id": 1,
        "client_id": fake_client["id"],
        "asset_id": fake_asset["id"],
        "quantity": 10.0,
        "buy_price": 100.0,
        "buy_date": str(date.today()),
        "is_active": True,
        "client": fake_client,
        "asset": fake_asset
    }


# -------------------- Testes --------------------

def test_create_allocation(fake_client, fake_asset, fake_allocation):
    payload = {
        "client_id": fake_client["id"],
        "asset_symbol": fake_asset["ticker"],
        "asset_name": fake_asset["name"],
        "quantity": 5.5,
        "buy_price": None,
        "buy_date": str(date.today())
    }

    allocation_return = fake_allocation.copy()
    allocation_return.update({
        "quantity": payload["quantity"],
        "buy_price": 100.0
    })

    with patch("app.repositories.allocations.create_allocation_by_symbol", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = allocation_return
        response = client.post("/allocations/", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["client_id"] == payload["client_id"]
    assert data["asset_id"] == fake_asset["id"]
    assert data["quantity"] == payload["quantity"]
    assert "id" in data
    assert data["is_active"] is True
    assert "client" in data
    assert "asset" in data


def test_list_allocations(fake_allocation):
    with patch("app.repositories.allocations.get_all_allocations", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = [fake_allocation]
        response = client.get("/allocations/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(alloc["id"] == fake_allocation["id"] for alloc in data)


def test_get_allocation(fake_allocation):
    with patch("app.repositories.allocations.get_allocation_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = fake_allocation
        response = client.get(f"/allocations/{fake_allocation['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == fake_allocation["id"]


def test_update_allocation(fake_allocation):
    update_payload = {"quantity": 20.0, "buy_price": 150.0}
    updated_allocation = fake_allocation.copy()
    updated_allocation.update(update_payload)

    with patch("app.repositories.allocations.update_allocation", new_callable=AsyncMock) as mock_update:
        mock_update.return_value = updated_allocation
        response = client.put(f"/allocations/{fake_allocation['id']}", json=update_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == update_payload["quantity"]
    assert data["buy_price"] == update_payload["buy_price"]


def test_delete_allocation(fake_allocation):
    with patch("app.repositories.allocations.delete_allocation", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = {"message": "Allocation marked as inactive successfully"}
        response = client.delete(f"/allocations/{fake_allocation['id']}")

    assert response.status_code == 200
    assert response.json()["message"] == "Allocation marked as inactive successfully"
