import io
from curl_cffi import AsyncSession
from fastapi import APIRouter, Depends, Query

from fastapi.responses import StreamingResponse
import pandas as pd

from app.database import get_db
from app.repositories.allocations import get_by_client
from app.repositories.finance import get_asset_metrics

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("/export")
async def export_data(client_id: int ,format: str = Query("csv", enum=["csv", "excel"]), db: AsyncSession = Depends(get_db)):
    allocations = await get_by_client(db, client_id)
    data = []
    for alloc in allocations:
        metrics = await get_asset_metrics(
            db,
            asset_id=alloc.asset_id,
            buy_price=alloc.buy_price,
            quantity=alloc.quantity
        )
        data.append({
            "client_id": alloc.client_id,
            "ticker": alloc.asset.ticker,
            "quantity": alloc.quantity,
            "buy_price": alloc.buy_price,
            "total_invested": metrics["total_invested"],
            "current_value": metrics["current_value"],
            "profit_loss": metrics["profit_loss"],
            "percentage_change": metrics["percentage_change"],
            "avg_daily_return": metrics["avg_daily_return"],
        })

    df = pd.DataFrame(data)

    if format == "csv":
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        response = StreamingResponse(iter([stream.getvalue()]),
                                     media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=export.csv"
        return response
    else:
        stream = io.BytesIO()
        with pd.ExcelWriter(stream, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        stream.seek(0)
        response = StreamingResponse(stream,
                                     media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response.headers["Content-Disposition"] = "attachment; filename=export.xlsx"
        return response