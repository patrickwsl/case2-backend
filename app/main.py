from fastapi import FastAPI

from app.routers import auth, clients, allocations, assets

app = FastAPI()

app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(allocations.router)
app.include_router(assets.router)
