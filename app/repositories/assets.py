import yfinance as yf
import redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.asset import Asset
from app.core.config import REDIS_HOST, REDIS_PORT

cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

async def create_asset(db: AsyncSession, ticker: str, name: str):
    """
    Cria um novo ativo no banco de dados.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        ticker (str): Código identificador do ativo.
        name (str): Nome do ativo.

    Returns:
        dict: Dados básicos do ativo criado.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    new_asset = Asset(ticker=ticker, name=name)
    db.add(new_asset)
    await db.commit()
    await db.refresh(new_asset)
    return {"id": new_asset.id, "ticker": new_asset.ticker, "name": new_asset.name}

async def list_assets_from_yahoo():
    """
    Obtém uma lista de ativos e seus preços atuais da fonte Yahoo Finance.

    Returns:
        list: Lista de ativos com símbolo e preço.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    tickers = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"]
    data = []
    for ticker in tickers:
        info = await get_asset_price(ticker)
        data.append({"symbol": ticker, "price": info})
    return data

async def get_asset_price(symbol: str):
    """
    Obtém o preço atual de um ativo pelo seu símbolo, utilizando cache Redis.

    Args:
        symbol (str): Símbolo do ativo.

    Returns:
        float: Preço atual do ativo.

    Raises:
        ValueError: Se não encontrar dados de preço para o símbolo.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    cache_key = f"asset_price:{symbol}"
    cached_price = cache.get(cache_key)
    if cached_price:
        try:
            return float(cached_price)
        except ValueError:
            cache.delete(cache_key)

    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d")
    if hist.empty:
        raise ValueError(f"No price data found for {symbol}")

    price = float(hist["Close"].iloc[-1])
    cache.setex(cache_key, 3600, price)
    return price

async def list_assets_from_db(db: AsyncSession):
    """
    Lista todos os ativos cadastrados no banco de dados.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.

    Returns:
        list: Lista de objetos Asset.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    result = await db.execute(select(Asset))
    return result.scalars().all()
