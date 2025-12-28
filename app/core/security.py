"""
Security utilities for password hashing and JWT tokens
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Configure password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# BCRYPT tem limite de 72 bytes
MAX_PASSWORD_LENGTH = 72

def hash_password(password: str) -> str:
    """
    Hash a password with bcrypt
    Trunca automaticamente para 72 bytes (limite do bcrypt)
    """
    # Truncar senha para evitar erro de tamanho
    password_truncated = password[:MAX_PASSWORD_LENGTH]
    return pwd_context.hash(password_truncated)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    Trunca automaticamente para 72 bytes (limite do bcrypt)
    """
    # Truncar senha para evitar erro de tamanho
    password_truncated = plain_password[:MAX_PASSWORD_LENGTH]
    
    try:
        return pwd_context.verify(password_truncated, hashed_password)
    except ValueError as e:
        # Log do erro mas retorna False ao invés de crash
        print(f"Password verification error: {e}")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """
    Verify a JWT token and return the email if valid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        return email
    except JWTError:
        return None
