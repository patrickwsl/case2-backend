import asyncio
from typing import Dict
import pandas as pd
import yfinance as yf
import redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.allocation import Allocation
from app.models.asset import Asset
from app.core.config import REDIS_HOST, REDIS_PORT

cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

NASDAQ_URL = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
OTHER_URL  = "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"

EXCHANGE_MAP = {
    "Q": "NASDAQ", "G": "NASDAQ", "S": "NASDAQ",
    "N": "NYSE", "A": "AMEX", "P": "NYSE Arca", "Z": "Cboe BZX", "V": "IEX"
}

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

def _fetch_all_tickers_df() -> pd.DataFrame:
    """Baixa e combina NASDAQ + outras bolsas (NYSE/AMEX/ARCA/BATS)."""
    # NASDAQ
    nasdaq = pd.read_csv(NASDAQ_URL, sep="|")
    nasdaq = nasdaq[~nasdaq["Symbol"].astype(str).str.contains("File Creation Time", na=False)]
    nasdaq = nasdaq.rename(columns={"Symbol": "symbol", "Security Name": "name", "ETF": "etf", "Market Category": "market_cat"})
    nasdaq["exchange"] = nasdaq["market_cat"].map(EXCHANGE_MAP).fillna("NASDAQ")
    nasdaq["is_etf"] = nasdaq["etf"].eq("Y")
    nasdaq = nasdaq[["symbol", "name", "exchange", "is_etf"]]

    # NYSE/AMEX/ARCA/BATS/etc.
    other = pd.read_csv(OTHER_URL, sep="|")
    other = other[~other["ACT Symbol"].astype(str).str.contains("File Creation Time", na=False)]
    other = other.rename(columns={"ACT Symbol": "symbol", "Security Name": "name", "Exchange": "ex", "ETF": "etf"})
    other["exchange"] = other["ex"].map(EXCHANGE_MAP).fillna(other["ex"])
    other["is_etf"] = other["etf"].eq("Y")
    other = other[["symbol", "name", "exchange", "is_etf"]]

    # Combina e remove duplicados por símbolo
    all_df = pd.concat([nasdaq, other], ignore_index=True)
    all_df = all_df.drop_duplicates(subset=["symbol"]).reset_index(drop=True)
    return all_df

def _get_all_tickers_cached(ttl_seconds: int = 6 * 3600) -> pd.DataFrame:
    """Cacheia a lista completa de tickers em Redis (como CSV compactado em bytes)."""
    cache_key = "all_tickers_df_v1"
    blob = cache.get(cache_key)
    if blob:
        try:
            from io import BytesIO
            return pd.read_parquet(BytesIO(blob))
        except Exception:
            cache.delete(cache_key)

    df = _fetch_all_tickers_df()
    try:
        from io import BytesIO
        buf = BytesIO()
        df.to_parquet(buf, index=False)
        cache.setex(cache_key, ttl_seconds, buf.getvalue())
    except Exception:
        # Se der ruim ao salvar, seguimos sem cachear
        pass
    return df

async def list_assets_from_yahoo(
    page: int = 1,
    per_page: int = 100,
    with_price: bool = True
) -> Dict:
    """
    Retorna lista paginada de ativos (símbolo, nome, exchange, is_etf) e, opcionalmente, preço.
    """
    df = _get_all_tickers_cached()
    total = int(df.shape[0])
    if per_page <= 0:
        per_page = 100
    if page <= 0:
        page = 1

    start = (page - 1) * per_page
    end = start + per_page
    page_df = df.iloc[start:end].copy()

    items = page_df.to_dict(orient="records")

    if not with_price or not items:
        return {
            "items": items,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }

    sem = asyncio.Semaphore(10)

    async def enrich(item):
        symbol = item["symbol"]
        try:
            async with sem:
                price = await get_asset_price(symbol)
            item["price"] = price
            def _fast():
                t = yf.Ticker(symbol)
                fi = getattr(t, "fast_info", None)
                if isinstance(fi, dict):
                    return fi.get("currency")
                return None
            item["currency"] = await asyncio.to_thread(_fast)
        except Exception:
            item["price"] = None
            item["currency"] = None
        return item

    items = await asyncio.gather(*(enrich(it) for it in items))

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": (total + per_page - 1) // per_page
    }


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


async def list_assets_by_client(db: AsyncSession, client_id: int):
    """
    Lista todos os ativos por cliente.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        client_id: ID do cliente.

    Returns:
        list: Lista de objetos Asset.

    Author: Patrick Lima (patrickwsl)
    Date: 13th August 2025
    """
    query = (
        select(Asset.ticker, Allocation.quantity)
        .join(Allocation, Allocation.asset_id == Asset.id)
        .where(Allocation.client_id == client_id)
    )
    result = await db.execute(query)
    return result.all()
