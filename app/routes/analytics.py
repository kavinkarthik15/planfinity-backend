from fastapi import APIRouter, Depends

from app.core.db import db
from app.routes.auth import get_current_user

router = APIRouter(prefix='/analytics', tags=['analytics'])

transactions_collection = db['transactions']


@router.get('/summary')
def get_summary(user=Depends(get_current_user)):
    user_email = user['email']

    transactions = list(transactions_collection.find({'user_email': user_email}))

    total_spent = 0
    category_data = {}

    for t in transactions:
        amount = t.get('amount', 0)
        category = t.get('category', 'Other')

        total_spent += amount

        if category not in category_data:
            category_data[category] = 0

        category_data[category] += amount

    return {'total_spent': total_spent, 'category_data': category_data}
