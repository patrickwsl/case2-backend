from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import SessionLocal, get_db
from app.models.asset import Asset
from app.models.daily_return import DailyReturn
from app.repositories import assets as asset_repo
import yfinance as yf

router = APIRouter(prefix="/assets", tags=["Assets"])

@router.post("/create")
async def create_asset(ticker: str, name: str, db: AsyncSession = Depends(get_db)):
    """
    Cria um novo ativo financeiro (asset) com ticker e nome.

    Args:
        ticker (str): Código identificador do ativo.
        name (str): Nome descritivo do ativo.
        db (AsyncSession): Sessão assíncrona do banco de dados.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    return await asset_repo.create_asset(db, ticker, name)

@router.get("/price")
async def get_asset_price(symbol: str):
    """
    Obtém o preço atual de mercado do ativo pelo seu símbolo.

    Args:
        symbol (str): Símbolo/ticker do ativo.

    Returns:
        dict: Contém o símbolo e o preço atual do ativo.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    return {"symbol": symbol, "price": await asset_repo.get_asset_price(symbol)}

@router.get("/list-yahoo")
async def list_assets():
    """
    Lista os ativos disponíveis obtidos da fonte Yahoo Finance.

    Returns:
        list: Lista com informações básicas dos ativos.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    return await asset_repo.list_assets_from_yahoo()


@router.get("/list")
async def list_assets(db: AsyncSession = Depends(get_db)):
    """
    Lista os ativos disponíveis obtidos da fonte Yahoo Finance.

    Returns:
        list: Lista com informações básicas dos ativos.

    Author: Patrick Lima (patrickwsl)
    Date: 10th August 2025
    """
    return await asset_repo.list_assets_from_db(db=db)

@router.get("/script")
async def populate_daily_returns():
    """Script para preencher dados no banco para testar"""
    async with SessionLocal() as session:
        tickers = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA']
        start = date(2025, 1, 1)
        end = date.today()

        for t in tickers:
            data = yf.download(t, start=start, end=end)
            asset_id = await session.execute(
                select(Asset.id).where(Asset.ticker == t)
            )
            asset_id = asset_id.scalar_one()

            for d, row in data.iterrows():
                dr = DailyReturn(
                    asset_id=asset_id,
                    date=d.date(),
                    close_price=row['Close']
                )
                session.add(dr)

        await session.commit()
