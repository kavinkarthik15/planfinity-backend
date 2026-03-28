from datetime import datetime, timedelta

from fastapi import APIRouter, Depends

from app.core.db import db
from app.routes.auth import get_current_user

router = APIRouter(prefix='/insights', tags=['insights'])

transactions_collection = db['transactions']


@router.get('/')
def get_insights(user=Depends(get_current_user)):
    user_email = user['email']

    transactions = list(transactions_collection.find({'user_email': user_email}))

    insights = []

    total_spent = 0
    category_data = {}

    # Calculate totals
    for t in transactions:
        amount = t.get('amount', 0)
        category = t.get('category', 'Other')

        total_spent += amount

        if category not in category_data:
            category_data[category] = 0

        category_data[category] += amount

    # Insight 1: High spending category
    if category_data:
        max_category = max(category_data, key=category_data.get)
        max_value = category_data[max_category]

        if max_value > total_spent * 0.4:
            insights.append(
                f'You are spending a lot on {max_category} (₹{max_value})'
            )

    # Insight 2: Weekly increase
    now = datetime.utcnow()
    last_week = now - timedelta(days=7)

    recent_spending = sum(t['amount'] for t in transactions if t['date'] >= last_week)

    if recent_spending > total_spent * 0.5:
        insights.append('Your spending is high this week 📈')

    # Insight 3: Saving suggestion
    if total_spent > 5000:
        savings = int(total_spent * 0.2)
        insights.append(f'You can save around ₹{savings} next month 💡')

    return {'insights': insights}
