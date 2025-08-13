import asyncio
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.database import SessionLocal
from app.repositories.assets_repository import list_assets_from_db
from app.repositories.daily_returns import get_latest_by_asset
from app.routers import auth, clients, allocations, assets, prices

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    await websocket.accept()
    
    try:
        async with SessionLocal() as session:
            while True:
                try:
                    assets = await list_assets_from_db(session)
                    prices = []
                    
                    for asset in assets:
                        latest = await get_latest_by_asset(session, asset.id)
                        if latest:
                            prices.append({
                                "ticker": asset.ticker, 
                                "price": float(latest.close_price)
                            })

                    if websocket.client_state.name != "DISCONNECTED":
                        await websocket.send_text(json.dumps(prices))
                    
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    logging.error(f"Erro ao processar dados: {e}")
                    try:
                        await websocket.send_text(json.dumps({"error": str(e)}))
                    except:
                        break
                        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass
        
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(allocations.router)
app.include_router(assets.router)
app.include_router(prices.router)