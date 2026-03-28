from fastapi import APIRouter

from database import db
from models.transaction import Transaction
from services.analytics import total_spending, category_breakdown, daily_average
from services.ai_engine import generate_insights
from services.budget import suggest_budget
from services.phase_detector import detect_phase
from services.prediction import predict_category_spending


router = APIRouter()


@router.post("/transactions")
def add_transaction(transaction: Transaction):
	payload = transaction.model_dump()
	db.transactions.insert_one(payload)
	return {"message": "Transaction added", "transaction": payload}


@router.get("/transactions/{user_id}")
def get_transactions(user_id: str):
	transactions = list(db.transactions.find({"user_id": user_id}, {"_id": 0}))
	return {"transactions": transactions}


@router.get("/analysis/{user_id}")
def get_analysis(user_id: str, total_budget: float = None):
	transactions = list(db.transactions.find({"user_id": user_id}, {"_id": 0}))

	if not transactions:
		return {"message": "No data available"}

	phase = detect_phase(transactions)

	total = total_spending(transactions)
	categories = category_breakdown(transactions)
	avg = daily_average(transactions)

	prediction_total = None
	prediction_category = None
	budget_recommendation = None
	insights = None

	if phase != "cold_start":
		prediction_category = predict_category_spending(transactions, days_ahead=10)
		prediction_total = sum(prediction_category.values())
		budget_recommendation = suggest_budget(prediction_category, total_budget)
		insights = generate_insights(transactions, prediction_category, phase)

	return {
		"phase": phase,
		"total_spent": total,
		"daily_avg": avg,
		"category_breakdown": categories,
		"prediction_total": prediction_total,
		"prediction_category": prediction_category,
		"budget_recommendation": budget_recommendation,
		"insights": insights,
	}
