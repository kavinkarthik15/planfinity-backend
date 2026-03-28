from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.ai.ai_engine import generate_insights
from app.ai.budget import generate_budget
from app.ai.prediction import predict_spending, calculate_confidence
from app.ai.alerts import generate_alerts
from app.ai.cache import cache_ai_results
from app.core.db import db
from app.firebase_service import send_notification
from app.routes.auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])

transactions_collection = db["transactions"]
budgets_collection = db["budgets"]
users_collection = db["users"]


@router.post("/add")
def add_transaction(data: dict, user=Depends(get_current_user)):
    user_id = data.get("user_id") or user["email"]

    transaction = {
        "user_email": user["email"],
        "user_id": user_id,
        "amount": data.get("amount"),
        "category": data.get("category"),
        "type": data.get("type", "expense"),
        "note": data.get("note", ""),
        "date": datetime.utcnow(),
    }

    transactions_collection.insert_one(transaction)

    user_transactions = list(transactions_collection.find({"user_id": user_id}))
    if not user_transactions:
        user_transactions = list(
            transactions_collection.find({"user_email": user["email"]})
        )

    predictions = predict_spending(user_transactions)
    confidence = calculate_confidence(user_transactions)
    budget = generate_budget(predictions)
    insights = generate_insights(user_transactions, predictions)
    
    # Get user's budget limits
    budget_doc = budgets_collection.find_one({"user_email": user["email"]})
    budget_limits = {}
    if budget_doc and "budgets" in budget_doc:
        budget_limits = {k.lower(): v for k, v in budget_doc["budgets"].items()}
    
    alerts = generate_alerts(user_transactions, predictions, budget_limits)
    print("ALERTS:", alerts)

    # Save precomputed AI results so /ai/results is instant.
    cache_ai_results(
        user_id=user_id,
        user_email=user["email"],
        predictions=predictions,
        budget=budget,
        insights=insights,
        alerts=alerts,
        confidence=confidence,
    )

    # Proactive push notifications on new transaction alerts
    user_doc = users_collection.find_one({"email": user["email"]}) or {}
    token = user_doc.get("fcm_token")
    print("USER TOKEN:", token)
    if token:
        for alert in alerts:
            try:
                message_id = send_notification(token, "Planfinity Alert", alert)
                print("Message sent successfully:", message_id)
            except Exception as exc:
                print(f"Push notification skipped: {exc}")

    return {
        "message": "Transaction added",
        "predictions": predictions,
        "budget": budget,
        "insights": insights,
        "alerts": alerts,
        "confidence": confidence,
    }


@router.get("/")
def get_transactions(user=Depends(get_current_user)):
    transactions = list(
        transactions_collection.find({"user_email": user["email"]}, {"_id": 0})
    )

    return {"transactions": transactions}
