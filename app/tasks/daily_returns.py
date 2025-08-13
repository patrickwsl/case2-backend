from celery import Celery
from datetime import date, timedelta
import yfinance as yf
from app.models.daily_return import DailyReturn
from app.database import SessionLocal
from app.repositories import assets as assets_repo

async_session_maker= SessionLocal
celery_app = Celery("tasks", broker="redis://redis:6379/0")

@celery_app.task
def fetch_and_store_daily_returns():
    """Consulta preços de fechamento de ontem e salva no banco."""
    yesterday = date.today() - timedelta(days=1)

    async def _run():
        async with async_session_maker() as session:
            assets = await assets_repo.list_assets_from_db(session)
            for asset in assets:
                data = yf.Ticker(asset.ticker).history(start=yesterday, end=date.today())
                if not data.empty:
                    close_price = data["Close"].iloc[0]
                    dr = DailyReturn(asset_id=asset.id, date=yesterday, close_price=close_price)
                    session.add(dr)
            await session.commit()

    import asyncio
    asyncio.run(_run())
