from fastapi import APIRouter, Depends

from app.core.db import db
from app.routes.auth import get_current_user

router = APIRouter(prefix='/budget', tags=['budget'])

budget_collection = db['budgets']
transactions_collection = db['transactions']


@router.post('/set')
def set_budget(data: dict, user=Depends(get_current_user)):
    user_email = user['email']

    category = data.get('category')
    limit = data.get('limit')

    budget_collection.update_one(
        {'user_email': user_email, 'category': category},
        {'$set': {'limit': limit}},
        upsert=True,
    )

    return {'message': 'Budget set successfully'}


@router.get('/')
def get_budget(user=Depends(get_current_user)):
    user_email = user['email']

    budgets = list(budget_collection.find({'user_email': user_email}, {'_id': 0}))
    transactions = list(transactions_collection.find({'user_email': user_email}))

    result = []
    alerts = []

    for b in budgets:
        category = b['category']
        limit = b['limit']

        spent = sum(
            t.get('amount', 0) for t in transactions if t.get('category') == category
        )

        percentage = (spent / limit) * 100 if limit > 0 else 0

        if percentage >= 100:
            alerts.append(f'⚠️ You exceeded your {category} budget!')
        elif percentage >= 80:
            alerts.append(f'⚠️ You are close to your {category} budget')

        result.append(
            {
                'category': category,
                'limit': limit,
                'spent': spent,
                'remaining': limit - spent,
                'percentage': percentage,
            }
        )

    return {'budgets': result, 'alerts': alerts}
