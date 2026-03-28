"""
Background AI Scheduler

Automatically runs AI predictions, budget analysis, and alerts for all users
at regular intervals without requiring user action. Uses APScheduler with asyncio.
"""

import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.db import db
from app.ai.prediction import predict_spending, calculate_confidence
from app.ai.budget import generate_budget
from app.ai.alerts import generate_alerts
from app.ai.ai_engine import generate_insights
from app.ai.cache import cache_ai_results
from app.firebase_service import send_notification

scheduler = AsyncIOScheduler()

transactions_collection = db['transactions']
users_collection = db['users']
ai_results_collection = db['ai_results']


async def run_ai_for_all_users():
    """
    Background job that runs AI analysis for all users.
    Fetches transactions, generates predictions, budgets, alerts,
    and sends notifications to users.
    """
    try:
        print(f"[{datetime.utcnow()}] Starting background AI job...")
        
        # Fetch all users
        users = list(users_collection.find())
        
        print(f"Found {len(users)} users to process")
        
        for user in users:
            user_id = user.get("user_id") or user.get("email")
            user_email = user.get("email")
            fcm_token = user.get("fcm_token")
            
            # Fetch user's transactions
            transactions = list(transactions_collection.find({"user_id": user_id}))
            
            if not transactions:
                print(f"  ℹ️ User {user_id}: No transactions found, skipping")
                continue
            
            print(f"  🔄 Processing user {user_id} with {len(transactions)} transactions...")
            
            try:
                # Run AI processing
                predictions = predict_spending(transactions)
                budget = generate_budget(predictions)
                insights = generate_insights(predictions)
                alerts = generate_alerts(transactions, predictions, budget)
                confidence = calculate_confidence(transactions)
                
                # Optimization: Skip if alerts haven't changed
                old_data = ai_results_collection.find_one({"user_id": user_id})
                if old_data and old_data.get("alerts") == alerts:
                    print(f"  ✓ User {user_id}: Alerts unchanged, skipping notification")
                    continue
                
                # Cache results
                cache_ai_results(
                    user_id=user_id,
                    user_email=user_email,
                    predictions=predictions,
                    budget=budget,
                    insights=insights,
                    alerts=alerts,
                    confidence=confidence
                )
                print(f"  ✓ User {user_id}: AI results cached")
                
                # Send notifications for each alert
                if fcm_token and alerts:
                    for alert in alerts:
                        try:
                            message_id = send_notification(
                                token=fcm_token,
                                title="Planfinity Alert 🚨",
                                body=alert
                            )
                            print(f"  📲 User {user_id}: Alert sent - {alert[:50]}... (msg_id: {message_id})")
                        except Exception as e:
                            print(f"  ⚠️ User {user_id}: Failed to send notification - {str(e)}")
                elif not fcm_token:
                    print(f"  ⚠️ User {user_id}: No FCM token, skipping notification")
                elif not alerts:
                    print(f"  ℹ️ User {user_id}: No alerts generated")
                    
            except Exception as e:
                print(f"  ❌ User {user_id}: Error during AI processing - {str(e)}")
                continue
        
        print(f"[{datetime.utcnow()}] Background AI job completed ✓\n")
        
    except Exception as e:
        print(f"[{datetime.utcnow()}] ❌ Background AI job failed: {str(e)}")


def start_scheduler():
    """
    Initialize and start the APScheduler.
    Schedules background AI job to run at regular intervals.
    
    Currently set to run every 30 minutes in production.
    Change to 1 minute for testing: minutes=1
    """
    print("Scheduler started")
    if not scheduler.running:
        # Schedule job to run every 30 minutes (production) or 1 minute (testing)
        scheduler.add_job(
            run_ai_for_all_users,
            "interval",
            minutes=30,  # Change to 1 for testing
            id="background_ai_job",
            replace_existing=True
        )
        scheduler.start()
        print("✓ Background AI scheduler started (interval: 30 minutes)")
    else:
        print("⚠️ Scheduler already running")


def stop_scheduler():
    """Stop the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        print("✓ Scheduler stopped")


if __name__ == "__main__":
    start_scheduler()
