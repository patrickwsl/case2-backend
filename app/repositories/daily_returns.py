from datetime import date, datetime, timedelta
import logging
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.allocation import Allocation
from app.models.daily_return import DailyReturn
import yfinance as yf

from app.repositories.assets import list_assets_by_client

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


async def get_latest_by_asset(db: AsyncSession, asset_id: int):
    """
    Pega o último DailyReturn pelo isset_id.

    Args:
        db (AsyncSession): Sessão assíncrona do banco.
        asset_id (int): ID do ativo.

    Returns:
        DailyReturn: Último registro criado.
    """
    stmt = (
        select(DailyReturn)
        .where(DailyReturn.asset_id == asset_id)
        .order_by(DailyReturn.date.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_captured_by_period(
    session: AsyncSession,
    client_id: int,
    period: str,
    year: int,
    month: int = None
) -> dict:
    """
    Calcula o valor captado por cliente em um período específico
    e compara com o valor atual no Yahoo Finance para calcular a rentabilidade.

    Args:
        session (AsyncSession)
        client_id (int)
        period (str): 'anual', 'semestral', 'mensal' ou 'semanal'
        year (int)
        month (int, optional)

    Returns:
        dict: {
            "captado": valor no BD,
            "atual": valor atual no Yahoo,
            "rentabilidade": percentual de variação
        }
    """
    today = datetime.utcnow().date()

    if period == "anual":
        start_date = datetime(year - 1, 1, 1).date()
        end_date = today
    elif period == "semestral":
        if not month:
            raise ValueError("Mês é obrigatório para cálculo semestral.")
        semester = 1 if month <= 6 else 2
        start_date = datetime(year, 1, 1).date() if semester == 1 else datetime(year, 7, 1).date()
        end_date = today
    elif period == "mensal":
        if not month:
            raise ValueError("Mês é obrigatório para cálculo mensal.")
        first_day_this_month = datetime(year, month, 1).date()
        start_date = (first_day_this_month - timedelta(days=1)).replace(day=1)
        end_date = today
    elif period == "semanal":
        if not month:
            raise ValueError("Mês é obrigatório para cálculo semanal.")
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    else:
        raise ValueError(f"Período inválido: {period}")

    query = (
        select(func.sum(DailyReturn.close_price * Allocation.quantity))
        .join(Allocation, Allocation.asset_id == DailyReturn.asset_id)
        .where(Allocation.client_id == client_id)
        .where(Allocation.is_active == True)
        .where(DailyReturn.date >= start_date)
        .where(DailyReturn.date <= end_date)
        .where(Allocation.buy_date <= end_date)
    )

    result = await session.execute(query)
    total_captured = float(result.scalar() or 0.0)

    assets = await list_assets_by_client(db=session, client_id=client_id)

    current_total_value = 0.0
    for ticker, qty in assets:
        try:
            price = yf.Ticker(ticker).fast_info.last_price
            current_total_value += price * qty
        except Exception as e:
            logging.warning(f"Erro ao buscar preço de {ticker}: {e}")

    profitability = ((current_total_value - total_captured) / total_captured * 100) if total_captured else 0.0

    return {
        "captado": total_captured,
        "atual": current_total_value,
        "rentabilidade": profitability
    }