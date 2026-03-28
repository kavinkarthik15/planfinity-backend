import certifi
from pymongo import MongoClient
from app.core.config import MONGO_URL

if not MONGO_URL:
    raise RuntimeError('MONGO_URL is not configured. Set it in backend/.env or environment variables.')

client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())

db = client["planfinity"]
