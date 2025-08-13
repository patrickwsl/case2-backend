from collections import defaultdict
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.daily_return import DailyReturn
from app.repositories import allocations_repository, daily_returns as dr_repo

async def calculate_client_performance(db: AsyncSession, client_id: int):
    allocations = await allocations_repository.get_by_client(db, client_id)
    if not allocations:
        return []

    # Agrupar alocações por ticker
    allocations_by_ticker = defaultdict(list)
    for alloc in allocations:
        allocations_by_ticker[alloc.asset.ticker].append(alloc)

    result = []

    for ticker, allocs in allocations_by_ticker.items():
        # Para cada ticker, coletar todos os daily_returns do asset
        asset_id = allocs[0].asset_id
        daily_returns = await dr_repo.get_by_asset(db, asset_id)
        if not daily_returns:
            continue

        daily_returns.sort(key=lambda x: x.date)

        # Agregar métricas por ticker considerando todas as alocações
        total_invested = 0
        current_value = 0
        profit_loss = 0

        # Para rentabilidade acumulada diária agregada ponderada
        daily_acc_returns = defaultdict(float)  # valor acumulado ponderado
        daily_weights = defaultdict(float)      # soma dos investimentos para ponderação

        for alloc in allocs:
            buy_price = alloc.buy_price
            quantity = alloc.quantity
            total_invested += buy_price * quantity

            # Filtrar daily_returns a partir da data da compra
            filtered_returns = [dr for dr in daily_returns if dr.date >= alloc.buy_date]

            for dr in filtered_returns:
                value = dr.close_price * quantity
                current_value += value if dr.date == filtered_returns[-1].date else 0  # só pega o último para current_value

                acc_return = ((dr.close_price - buy_price) / buy_price) * 100
                daily_acc_returns[dr.date] += acc_return * (buy_price * quantity)
                daily_weights[dr.date] += buy_price * quantity

        profit_loss = current_value - total_invested
        percentage_change = (profit_loss / total_invested) * 100 if total_invested else 0

        # Calcular avg_daily_return (simples média das variações diárias)
        daily_changes = []
        for i in range(1, len(daily_returns)):
            prev = daily_returns[i - 1].close_price
            curr = daily_returns[i].close_price
            daily_changes.append((curr - prev) / prev if prev else 0)
        avg_daily_return = sum(daily_changes) / len(daily_changes) if daily_changes else 0

        # Curva de rentabilidade acumulada diária ponderada
        performance_curve = []
        for dt in sorted(daily_acc_returns.keys()):
            weighted_return = daily_acc_returns[dt]
            weight = daily_weights[dt] if daily_weights[dt] else 1
            acc_return_pct = weighted_return / weight
            performance_curve.append({
                "date": dt.isoformat(),
                "accumulated_return_pct": round(acc_return_pct, 2),
                "ticker": ticker,
            })

        result.append({
            "ticker": ticker,
            "buy_price": allocs[0].buy_price,
            "quantity": sum(a.quantity for a in allocs),
            "total_invested": round(total_invested, 2),
            "current_value": round(current_value, 2),
            "profit_loss": round(profit_loss, 2),
            "percentage_change": round(percentage_change, 2),
            "avg_daily_return": round(avg_daily_return * 100, 2),
            "start_date": daily_returns[0].date.isoformat(),
            "end_date": daily_returns[-1].date.isoformat(),
            "performance_curve": performance_curve,
        })

    return result

async def get_asset_metrics(
    db: AsyncSession,
    asset_id: int,
    buy_price: float,
    quantity: float,
    buy_date: date = None
):
    stmt = select(DailyReturn).where(DailyReturn.asset_id == asset_id)
    if buy_date:
        stmt = stmt.where(DailyReturn.date >= buy_date)
    stmt = stmt.order_by(DailyReturn.date)
    result = await db.execute(stmt)
    daily_returns = result.scalars().all()

    if not daily_returns:
        return None

    initial_price = daily_returns[0].close_price
    latest_price = daily_returns[-1].close_price

    total_invested = buy_price * quantity
    current_value = latest_price * quantity
    profit_loss = current_value - total_invested
    percentage_change = ((latest_price - buy_price) / buy_price) * 100

    # variação diária média simples
    daily_changes = []
    for i in range(1, len(daily_returns)):
        prev_close = daily_returns[i-1].close_price
        curr_close = daily_returns[i].close_price
        daily_changes.append((curr_close - prev_close) / prev_close)
    avg_daily_return = sum(daily_changes) / len(daily_changes) if daily_changes else 0

    return {
        "total_invested": total_invested,
        "current_value": current_value,
        "profit_loss": profit_loss,
        "percentage_change": percentage_change,
        "avg_daily_return": avg_daily_return,
        "start_date": daily_returns[0].date,
        "end_date": daily_returns[-1].date,
    }