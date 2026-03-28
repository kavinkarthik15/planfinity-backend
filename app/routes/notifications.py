"""
Notification endpoints for device token registration and management.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from app.core.db import db
from app.routes.auth import get_current_user

router = APIRouter(prefix='/notifications', tags=['Notifications'])

device_tokens_collection = db['device_tokens']
users_collection = db['users']


@router.post('/token')
def register_device_token(data: dict, user=Depends(get_current_user)):
    """
    Register a device token for receiving push notifications.
    
    Args:
        data: {"device_token": "fcm_token_string"}
    
    Returns:
        {"message": "Device token registered"}
    """
    user_id = data.get('user_id') or user.get('email')
    fcm_token = data.get('fcm_token') or data.get('device_token')

    if not user_id:
        raise HTTPException(status_code=400, detail='user_id required')
    if not fcm_token:
        raise HTTPException(status_code=400, detail='fcm_token required')

    # Update token in users schema as requested
    user_result = users_collection.update_one(
        {'email': user.get('email')},
        {
            '$set': {
                'user_id': user_id,
                'fcm_token': fcm_token,
                'updated_at': datetime.utcnow(),
            }
        },
        upsert=False,
    )
    
    # Store or update device token
    device_tokens_collection.update_one(
        {'user_email': user['email']},
        {
            '$set': {
                'user_email': user['email'],
                'user_id': user_id,
                'device_token': fcm_token,
            },
            '$setOnInsert': {
                'created_at': datetime.utcnow(),
            }
        },
        upsert=True
    )
    
    return {
        'message': 'Device token registered successfully',
        'user_updated': user_result.modified_count > 0,
    }


@router.get('/tokens/{user_email}')
def get_device_tokens(user_email: str, user=Depends(get_current_user)):
    """
    Get all device tokens for a user (for sending notifications).
    Internal use only.
    """
    tokens = list(device_tokens_collection.find(
        {'user_email': user_email},
        {'_id': 0}
    ))
    
    return {'tokens': [t['device_token'] for t in tokens if 'device_token' in t]}
