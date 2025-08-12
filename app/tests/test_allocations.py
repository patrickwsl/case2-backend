import uuid
import pytest
from datetime import date

pytestmark = pytest.mark.asyncio

@pytest.fixture(autouse=True)
def mock_get_asset_price(mocker):
    mocker.patch("app.repositories.allocations_repository.get_asset_price", return_value=100.0)
@pytest.fixture
async def setup_client(db_session):
    from app.models.client import Client
    unique_email = f"client_{uuid.uuid4().hex[:8]}@test.com"
    client = Client(name="Client Test", email=unique_email, status="active")
    db_session.add(client)
    await db_session.commit()
    await db_session.refresh(client)
    return client

@pytest.fixture
async def setup_asset(db_session):
    from app.models.asset import Asset
    asset = Asset(
        ticker="TEST",
        name="Test Asset"
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)
    return asset

@pytest.fixture
async def setup_allocation(client, setup_client, setup_asset):
    payload = {
        "client_id": setup_client.id,
        "asset_id": setup_asset.id,
        "quantity": 10.0,
        "buy_price": 100.0,
        "buy_date": str(date.today())
    }
    response = await client.post("/allocations/", json=payload)
    return response.json()

async def test_create_allocation(client, setup_client, setup_asset):
    payload = {
        "client_id": setup_client.id,
        "asset_id": setup_asset.id,
        "quantity": 5.5,
        "buy_price": None,
        "buy_date": str(date.today())
    }
    response = await client.post("/allocations/", json=payload)
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["client_id"] == payload["client_id"]
    assert data["asset_id"] == payload["asset_id"]
    assert data["quantity"] == payload["quantity"]
    assert "id" in data
    assert data["is_active"] is True

async def test_list_allocations(client, setup_allocation):
    response = await client.get("/allocations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(alloc["id"] == setup_allocation["id"] for alloc in data)

async def test_get_allocation(client, setup_allocation):
    allocation_id = setup_allocation["id"]
    response = await client.get(f"/allocations/{allocation_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == allocation_id

async def test_update_allocation(client, setup_allocation):
    allocation_id = setup_allocation["id"]
    update_payload = {
        "quantity": 20.0,
        "buy_price": 150.0
    }
    response = await client.put(f"/allocations/{allocation_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == update_payload["quantity"]
    assert data["buy_price"] == update_payload["buy_price"]

async def test_delete_allocation(client, setup_allocation):
    allocation_id = setup_allocation["id"]
    response = await client.delete(f"/allocations/{allocation_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Allocation marked as inactive successfully"

    response = await client.get(f"/allocations/{allocation_id}")
    data = response.json()
    assert data["is_active"] is False
