from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import ai, auth, analytics, budget, insights, transactions, notifications, dashboard
from app.services.scheduler import start_scheduler, stop_scheduler
from app.core.config import CORS_ORIGINS

app = FastAPI()

# ✅ Fix CORS properly
allowed_origins = [origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()]

# If nothing set → allow all (important for Render)
if not allowed_origins or allowed_origins == [""]:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include all routes
app.include_router(ai.router)
app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(budget.router)
app.include_router(insights.router)
app.include_router(transactions.router)
app.include_router(notifications.router)
app.include_router(dashboard.router)

# ✅ Startup event
@app.on_event("startup")
async def startup_event():
    start_scheduler()

# ✅ Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()

# ✅ Root endpoint
@app.get("/")
def home():
    return {"message": "Planfinity API running"}