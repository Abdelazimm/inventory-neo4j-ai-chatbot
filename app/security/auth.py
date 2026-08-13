from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Built-in secure users repository for application RBAC
APP_USERS = {
    "admin": {
        "user_id": 1,
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin",
        "full_name": "System Admin",
        "is_active": True
    },
    "manager": {
        "user_id": 2,
        "username": "manager",
        "hashed_password": pwd_context.hash("manager123"),
        "role": "manager",
        "full_name": "Inventory Manager",
        "is_active": True
    },
    "viewer": {
        "user_id": 3,
        "username": "viewer",
        "hashed_password": pwd_context.hash("viewer123"),
        "role": "viewer",
        "full_name": "Graph Viewer",
        "is_active": True
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    return APP_USERS.get(username)
