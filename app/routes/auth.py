from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from pymongo.errors import PyMongoError
from app.core.db import db
from app.services.security import ALGORITHM, SECRET_KEY, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
users_collection = db["users"]
security = HTTPBearer()


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.get("/health")
def auth_health():
    return {"message": "Auth route is healthy"}


@router.post("/signup")
def signup(payload: SignupRequest):
    try:
        existing_user = users_collection.find_one({"email": payload.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        result = users_collection.insert_one(
            {
                "name": payload.name,
                "email": payload.email,
                "password": payload.password,
            }
        )

        return {
            "message": "User created successfully",
            "user_id": str(result.inserted_id),
        }
    except PyMongoError as exc:
        raise HTTPException(status_code=503, detail=f"Database error: {exc}") from exc


@router.post("/login")
def login(payload: LoginRequest):
    try:
        user = users_collection.find_one({"email": payload.email})
        if not user or user.get("password") != payload.password:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token({"email": payload.email})
        return {
            "access_token": token,
            "token_type": "bearer",
        }
    except PyMongoError as exc:
        raise HTTPException(status_code=503, detail=f"Database error: {exc}") from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {"user": user}
