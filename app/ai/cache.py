"""
AI Results Caching Module

Stores and retrieves cached AI predictions to avoid recalculation
and improve performance. Cache is invalidated on new transactions.
"""

from datetime import datetime
from app.core.db import db

ai_results_collection = db['ai_results']


def get_cached_ai_results(user_id: str, user_email: str = None):
    """
    Retrieve cached AI results if they exist and are fresh (< 1 hour old).
    
    Args:
        user_id: User identifier
        user_email: User email (fallback lookup)
    
    Returns:
        Cached AI results dict or None if not found/stale
    """
    # Try to find by user_id first
    cached = ai_results_collection.find_one({'user_id': user_id})
    
    # Fallback to email lookup
    if not cached and user_email:
        cached = ai_results_collection.find_one({'user_email': user_email})
    
    if not cached:
        return None
    
    # Check if cache is still fresh (less than 1 hour old)
    if 'last_updated' in cached:
        age_seconds = (datetime.utcnow() - cached['last_updated']).total_seconds()
        if age_seconds > 3600:  # 1 hour
            return None  # Cache is stale
    
    # Remove MongoDB _id before returning
    cached.pop('_id', None)
    return cached


def cache_ai_results(user_id: str, user_email: str, predictions: dict, 
                     budget: dict, insights: str, alerts: list, 
                     confidence: dict):
    """
    Store AI results in cache with timestamp.
    
    Args:
        user_id: User identifier
        user_email: User email
        predictions: Dict of category -> predicted amount
        budget: Dict of category -> budget recommendation
        insights: Text insight string
        alerts: List of alert strings
        confidence: Dict of category -> confidence score (0.0-1.0)
    """
    ai_doc = {
        'user_id': user_id,
        'user_email': user_email,
        'predictions': predictions,
        'budget': budget,
        'insights': insights,
        'alerts': alerts,
        'confidence': confidence,
        'last_updated': datetime.utcnow(),
    }
    
    # Update if exists, insert if not
    ai_results_collection.update_one(
        {'user_id': user_id},
        {'$set': ai_doc},
        upsert=True
    )


def invalidate_cache(user_id: str, user_email: str = None):
    """
    Invalidate cache for a user (called on new transaction).
    
    Args:
        user_id: User identifier
        user_email: User email (fallback)
    """
    ai_results_collection.delete_one({'user_id': user_id})
    if user_email:
        ai_results_collection.delete_one({'user_email': user_email})
