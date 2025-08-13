import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.database import SessionLocal
from app.repositories import daily_returns as dr_repo
from app.repositories.client import get_clients
from app.routers import auth, clients, allocations, assets, prices

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/captado")
async def websocket_prices(websocket: WebSocket, month: int, year: int):
    await websocket.accept()
    try:
        async with SessionLocal() as session:
            while True:
                clients = await get_clients(session, skip=0, limit=999)
                data_to_send = []
                for client in clients:
                    data_to_send.append({
                        "client_name": client.name,
                        "anual": await dr_repo.get_captured_by_period(session, client.id, "anual", year),
                        "semestral": await dr_repo.get_captured_by_period(session, client.id, "semestral", year, month),
                        "mensal": await dr_repo.get_captured_by_period(session, client.id, "mensal", year, month),
                        "semanal": await dr_repo.get_captured_by_period(session, client.id, "semanal", year, month),
                    })

                await websocket.send_text(json.dumps(data_to_send, ensure_ascii=False))
                await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(allocations.router)
app.include_router(assets.router)
app.include_router(prices.router)