from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories import assets_repository as asset_repo

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
