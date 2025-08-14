import pytest

pytestmark = pytest.mark.asyncio

async def test_create_asset(client):
    params = {
        "ticker": "TEST",
        "name": "Test Asset"
    }
    response = await client.post("/assets/create", params=params)
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["ticker"] == params["ticker"]
    assert data["name"] == params["name"]
    assert "id" in data

async def test_list_assets_yahoo(client):
    response = await client.get("/assets/list-yahoo")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    assert isinstance(data["items"], list)

    if data["items"]:
        first_item = data["items"][0]
        assert "symbol" in first_item
        assert "price" in first_item

@pytest.mark.asyncio
async def test_list_assets_db(client):
    response = await client.get("/assets/list")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    if data:
        first = data[0]
        assert "ticker" in first
        assert "id" in first
        assert "name" in first
        assert isinstance(first["ticker"], str)
        assert isinstance(first["id"], int)
        assert isinstance(first["name"], str)
