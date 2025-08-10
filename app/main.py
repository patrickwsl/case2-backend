from fastapi import FastAPI

from app.routers import auth, clients

app = FastAPI()

app.include_router(auth.router)
app.include_router(clients.router)
