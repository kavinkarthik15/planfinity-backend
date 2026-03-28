from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not MONGO_URL:
    raise ValueError("MONGO_URL is not set in environment variables")

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_key.json")
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY", "")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
