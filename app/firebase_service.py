import json
import os

import firebase_admin
from firebase_admin import credentials, messaging
from app.core.config import FIREBASE_API_KEY, FIREBASE_CREDENTIALS_PATH

API_KEY = FIREBASE_API_KEY

firebase_enabled = False

if not firebase_admin._apps:
    firebase_json = os.getenv("FIREBASE_CREDENTIALS")
    try:
        if firebase_json:
            cred_dict = json.loads(firebase_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            firebase_enabled = True
            print("Firebase initialized using FIREBASE_CREDENTIALS env var")
        elif os.path.exists(FIREBASE_CREDENTIALS_PATH):
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            firebase_enabled = True
            print(f"Firebase initialized using file path: {FIREBASE_CREDENTIALS_PATH}")
        else:
            print("Firebase credentials not found; notifications disabled")
    except Exception as e:
        print(f"Firebase initialization failed; notifications disabled: {e}")
else:
    firebase_enabled = True


def send_notification(token: str, title: str, body: str) -> str:
    if not firebase_enabled:
        return "firebase_disabled"

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(
                channel_id='planfinity_alerts',
                sound='default',
            ),
        ),
        apns=messaging.APNSConfig(
            headers={'apns-priority': '10'},
            payload=messaging.APNSPayload(
                aps=messaging.Aps(sound='default')
            ),
        ),
        token=token,
    )

    return messaging.send(message)
