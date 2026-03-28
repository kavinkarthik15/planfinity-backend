from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import ai
from app.routes import auth
from app.routes import analytics
from app.routes import budget
from app.routes import insights
from app.routes import transactions
from app.routes import notifications
from app.routes import dashboard
from app.services.scheduler import start_scheduler, stop_scheduler
from app.core.config import CORS_ORIGINS

app = FastAPI()

allowed_origins = [origin.strip() for origin in CORS_ORIGINS.split(',') if origin.strip()]
if not allowed_origins:
    allowed_origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(ai.router)
app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(budget.router)
app.include_router(insights.router)
app.include_router(transactions.router)
app.include_router(notifications.router)
app.include_router(dashboard.router)


@app.on_event("startup")
async def startup_event():
    """Start background AI scheduler on app startup."""
    start_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background AI scheduler on app shutdown."""
    stop_scheduler()


@app.get("/")
def home():
    return {"message": "Planfinity API running"}
