from fastapi import FastAPI
from app.routes import auth, dashboard, transactions

app = FastAPI()

app.include_router(auth.router, prefix="/auth")
app.include_router(dashboard.router, prefix="/dashboard")
app.include_router(transactions.router, prefix="/transactions")
