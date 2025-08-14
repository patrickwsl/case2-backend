import pandas as pd
from unittest.mock import AsyncMock, MagicMock
from app.tasks.daily_returns import fetch_and_store_daily_returns

def test_fetch_and_store_daily_returns(monkeypatch):
    df = pd.DataFrame({"Close": [150.0]})
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = df
    monkeypatch.setattr("app.tasks.daily_returns.yf.Ticker", lambda symbol: mock_ticker)

    fake_asset = MagicMock()
    fake_asset.id = 1
    fake_asset.ticker = "AAPL"
    monkeypatch.setattr(
        "app.tasks.daily_returns.assets_repo.list_assets_from_db",
        AsyncMock(return_value=[fake_asset])
    )

    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None
    monkeypatch.setattr("app.tasks.daily_returns.async_session_maker", lambda: mock_session)

    fetch_and_store_daily_returns()

    mock_ticker.history.assert_called_once()
    assert mock_session.add.call_count == 1
    assert mock_session.commit.call_count == 1
