from fastapi import APIRouter

from app.ai.ai_engine import generate_insights
from app.ai.budget import generate_budget
from app.ai.prediction import predict_spending, calculate_confidence
from app.ai.alerts import generate_alerts
from app.ai.cache import get_cached_ai_results, cache_ai_results
from app.core.db import db
from app.firebase_service import send_notification

router = APIRouter(prefix='/ai', tags=['AI'])

transactions_collection = db['transactions']
budgets_collection = db['budgets']
users_collection = db['users']


@router.get('/results/{user_id}')
def get_results(user_id: str):
    """Return precomputed AI results without recomputing."""
    cached = get_cached_ai_results(user_id)
    if not cached:
        return {'message': 'No AI data yet'}

    return {
        'predictions': cached.get('predictions', {}),
        'budget': cached.get('budget', {}),
        'insights': cached.get('insights', ''),
        'alerts': cached.get('alerts', []),
        'confidence': cached.get('confidence', {}),
        'last_updated': cached.get('last_updated'),
        'from_cache': True,
    }


@router.get('/analyze/{user_id}')
def analyze(user_id: str):
    """
    Get AI analysis with predictions, confidence scores, and alerts.
    Results are cached for up to 1 hour to improve performance.
    """
    # Try to get cached results first
    cached = get_cached_ai_results(user_id)
    if cached:
        return {
            'predictions': cached['predictions'],
            'budget': cached['budget'],
            'insights': cached['insights'],
            'alerts': cached['alerts'],
            'confidence': cached['confidence'],
            'from_cache': True,
        }
    
    # Get user transactions
    transactions = list(transactions_collection.find({'user_id': user_id}))
    if not transactions:
        transactions = list(transactions_collection.find({'user_email': user_id}))

    # Generate predictions with confidence
    predictions = predict_spending(transactions)
    confidence = calculate_confidence(transactions)
    
    # Generate budget recommendations
    budget = generate_budget(predictions)
    
    # Get user's budget limits from database
    budget_doc = budgets_collection.find_one({'user_id': user_id})
    if not budget_doc:
        budget_doc = budgets_collection.find_one({'user_email': user_id})
    
    budget_limits = {}
    if budget_doc and 'budgets' in budget_doc:
        budget_limits = {k.lower(): v for k, v in budget_doc['budgets'].items()}
    
    # Generate insights and alerts
    insights = generate_insights(transactions, predictions)
    alerts = generate_alerts(transactions, predictions, budget_limits)

    # Send push notifications for generated alerts when user has an FCM token
    user_doc = users_collection.find_one(
        {'$or': [{'user_id': user_id}, {'email': user_id}]}
    )
    token = (user_doc or {}).get('fcm_token')
    if token:
        for alert in alerts:
            try:
                send_notification(token, 'Planfinity Alert', alert)
            except Exception:
                # Keep AI response reliable even if push provider is unavailable.
                pass

    # Cache the results
    if transactions:  # Only cache if we have data
        user_email = None
        if transactions:
            user_email = transactions[0].get('user_email')
        cache_ai_results(user_id, user_email or user_id, predictions, budget, 
                        insights, alerts, confidence)

    return {
        'predictions': predictions,
        'budget': budget,
        'insights': insights,
        'alerts': alerts,
        'confidence': confidence,
        'from_cache': False,
    }
