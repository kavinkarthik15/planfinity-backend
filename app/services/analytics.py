from datetime import datetime, timedelta

from app.ai.cache import get_cached_ai_results
from app.core.db import db

transactions_collection = db['transactions']


def _weekly_change(transactions: list[dict]) -> float:
    now = datetime.utcnow()
    week_start = now - timedelta(days=7)
    prev_week_start = now - timedelta(days=14)

    this_week = 0.0
    prev_week = 0.0

    for tx in transactions:
        amount = float(tx.get('amount', 0) or 0)
        raw_date = tx.get('created_at') or tx.get('date') or tx.get('timestamp')

        dt = None
        if isinstance(raw_date, datetime):
            dt = raw_date
        elif isinstance(raw_date, str):
            try:
                dt = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
            except ValueError:
                dt = None

        if dt is None:
            continue

        if dt > week_start:
            this_week += amount
        elif dt > prev_week_start:
            prev_week += amount

    if prev_week <= 0:
        return 100.0 if this_week > 0 else 0.0

    return ((this_week - prev_week) / prev_week) * 100


def get_dashboard_data(user_id: str) -> dict:
    transactions = list(
        transactions_collection.find(
            {'$or': [{'user_email': user_id}, {'user_id': user_id}]}
        )
    )

    total_spending = 0.0
    categories: dict[str, float] = {}

    for tx in transactions:
        amount = float(tx.get('amount', 0) or 0)
        category = str(tx.get('category', 'Other'))
        total_spending += amount
        categories[category] = categories.get(category, 0) + amount

    cached_ai = get_cached_ai_results(user_id) or {}
    predictions = cached_ai.get('predictions', {}) or {}

    category_rows = []
    for name, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        predicted = float(predictions.get(name, amount) or amount)
        change = 0.0 if amount <= 0 else ((predicted - amount) / amount) * 100
        category_rows.append(
            {
                'name': name,
                'amount': round(amount, 2),
                'change': round(change, 1),
            }
        )

    insight = cached_ai.get('insights')
    if not insight:
        delta = sum(float(v or 0) for v in predictions.values()) - total_spending
        if delta > 0:
            insight = f'You may exceed your budget by Rs {delta:.0f}'
        elif delta < 0:
            insight = f'You may stay under budget by Rs {abs(delta):.0f}'
        else:
            insight = 'Spending is currently stable.'

    return {
        'total_spending': round(total_spending, 2),
        'change': round(_weekly_change(transactions), 1),
        'categories': category_rows,
        'insight': insight,
        'alerts': cached_ai.get('alerts', []),
    }
