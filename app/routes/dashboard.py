from fastapi import APIRouter, Depends

from app.routes.auth import get_current_user
from app.services.analytics import get_dashboard_data

router = APIRouter(tags=['dashboard'])


@router.get('/dashboard')
def dashboard(user=Depends(get_current_user)):
    user_id = user.get('email') or user.get('id')
    return get_dashboard_data(user_id)
