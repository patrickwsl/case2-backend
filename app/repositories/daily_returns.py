from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.daily_return import DailyReturn

async def get_by_asset(db: AsyncSession, asset_id: int):
    """
    Retorna todos os registros de daily_returns para um ativo específico, ordenados por data.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        asset_id (int): ID do ativo.

    Returns:
        list[DailyReturn]: Lista de registros ordenados por data crescente.
    """
    result = await db.execute(
        select(DailyReturn)
        .where(DailyReturn.asset_id == asset_id)
        .order_by(DailyReturn.date.asc())
    )
    return result.scalars().all()

async def create_daily_return(db: AsyncSession, asset_id: int, date: date, close_price: float):
    """
    Cria um registro de retorno diário para um ativo.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        asset_id (int): ID do ativo.
        date (date): Data do fechamento.
        close_price (float): Preço de fechamento.

    Returns:
        DailyReturn: Registro criado.
    """
    daily_return = DailyReturn(
        asset_id=asset_id,
        date=date,
        close_price=close_price
    )
    db.add(daily_return)
    await db.commit()
    await db.refresh(daily_return)
    return daily_return
