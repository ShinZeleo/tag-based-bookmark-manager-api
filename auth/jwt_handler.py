from datetime import datetime, timedelta
from typing import Optional
import os

from jose import JWTError, jwt
import bcrypt

# ========================
# CONFIGURATION
# ========================
# SECRET_KEY: Used to sign and verify JWT tokens. In production, use a secure random string.
# ALGORITHM: HS256 is a standard symmetric signing algorithm for JWT.
# ACCESS_TOKEN_EXPIRE_MINUTES: Token validity duration (30 minutes).
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ========================
# PASSWORD HASHING (bcrypt)
# ========================
# Using bcrypt directly for hashing and verification.
# This avoids the known incompatibility between passlib and bcrypt>=4.1.

def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt. NEVER store passwords in plain text."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plain-text password against its bcrypt hash. Returns True if they match."""
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ========================
# JWT TOKEN LOGIC
# ========================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary payload to encode (e.g., {"sub": "1"}).
        expires_delta: Optional custom expiration time.
    
    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: The JWT string from the Authorization header.
    
    Returns:
        The subject (user_id) from the token payload, or None if invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str = payload.get("sub")
        if sub is None:
            return None
        return str(sub)
    except JWTError:
        return None
