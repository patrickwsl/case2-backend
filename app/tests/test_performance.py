import pytest
from unittest.mock import AsyncMock, patch
from datetime import date

from app.repositories.finance import calculate_client_performance


class FakeAsset:
    def __init__(self, ticker):
        self.ticker = ticker


class FakeAllocation:
    def __init__(self, asset_id, ticker, buy_price, quantity, buy_date):
        self.asset_id = asset_id
        self.asset = FakeAsset(ticker)
        self.buy_price = buy_price
        self.quantity = quantity
        self.buy_date = buy_date


class FakeDailyReturn:
    def __init__(self, date, close_price):
        self.date = date
        self.close_price = close_price


@pytest.mark.asyncio
async def test_calculate_client_performance_basic():
    # Dados fake
    allocations = [
        FakeAllocation(asset_id=1, ticker="AAPL", buy_price=100, quantity=10, buy_date=date(2023, 1, 1)),
        FakeAllocation(asset_id=1, ticker="AAPL", buy_price=110, quantity=5, buy_date=date(2023, 1, 3)),
    ]
    daily_returns = [
        FakeDailyReturn(date(2023, 1, 1), 100),
        FakeDailyReturn(date(2023, 1, 2), 105),
        FakeDailyReturn(date(2023, 1, 3), 108),
        FakeDailyReturn(date(2023, 1, 4), 115),
    ]

    with patch("app.repositories.finance.allocations_repo.get_by_client", new=AsyncMock(return_value=allocations)):
        with patch("app.repositories.finance.dr_repo.get_by_asset", new=AsyncMock(return_value=daily_returns)):
            db_session = AsyncMock()
            result = await calculate_client_performance(db_session, client_id=123)

    # Verificações básicas
    assert len(result) == 1
    perf = result[0]
    assert perf["ticker"] == "AAPL"
    assert perf["total_invested"] == 100 * 10 + 110 * 5
    assert "performance_curve" in perf
    assert perf["start_date"] == "2023-01-01"
    assert perf["end_date"] == "2023-01-04"
    assert all("accumulated_return_pct" in p for p in perf["performance_curve"])
