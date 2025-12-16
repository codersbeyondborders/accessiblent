# auth.py
import os
import secrets
import datetime
from typing import Optional, Dict, Any

import bcrypt
import jwt
from pydantic import BaseModel, EmailStr
from fastapi import HTTPException, Cookie, Depends
from fastapi.security import HTTPBearer

from db import q

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
VERIFICATION_TOKEN_EXPIRATION_DAYS = 7

# Public email domains list
PUBLIC_EMAIL_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "outlook.com",
    "hotmail.com",
    "aol.com",
    "icloud.com",
    "mail.com",
    "protonmail.com",
    "zoho.com",
    "yandex.com",
    "gmx.com",
    "live.com",
    "msn.com",
    "me.com",
    "mac.com",
}

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    organization_id: int
    email: str
    full_name: str
    is_verified: bool
    created_at: datetime.datetime


# Email domain validation
def is_public_email_domain(email: str) -> bool:
    """
    Check if the email domain is a public email provider.
    Returns True if public, False if organizational.
    """
    if not email or "@" not in email:
        return True  # Invalid email format, treat as public
    
    domain = email.split("@")[-1].lower().strip()
    return domain in PUBLIC_EMAIL_DOMAINS


# Password hashing and verification
def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with cost factor 12.
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against a bcrypt hash.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


# Email verification token generation
def create_verification_token() -> str:
    """
    Generate a cryptographically random verification token (32 bytes).
    """
    return secrets.token_urlsafe(32)


# JWT token generation and validation
def create_jwt_token(user_id: int, organization_id: int) -> str:
    """
    Create a JWT token with 24-hour expiration.
    Includes user_id and organization_id in the payload.
    """
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "organization_id": organization_id,
        "exp": expiration,
        "iat": datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    Returns the payload if valid, raises HTTPException if invalid.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Session management
def get_current_user(access_token: Optional[str] = Cookie(None)) -> Dict[str, Any]:
    """
    Extract and validate the current user from the JWT token in cookies.
    Validates session exists in database and is not expired.
    Returns user info if valid, raises HTTPException if not authenticated.
    
    This is the main authentication dependency for FastAPI routes.
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Verify JWT token structure and signature
    payload = verify_jwt_token(access_token)
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Check if session exists in database and is not expired
    session_rows = q(
        """SELECT id, user_id, expires_at, created_at 
           FROM session 
           WHERE token=%s AND user_id=%s""",
        (access_token, user_id)
    )
    
    if not session_rows:
        raise HTTPException(status_code=401, detail="Session not found or invalid")
    
    session = session_rows[0]
    
    # Check if session has expired (24 hours from creation)
    now = datetime.datetime.utcnow()
    if session["expires_at"] < now:
        # Session expired, delete it
        q("DELETE FROM session WHERE id=%s", (session["id"],))
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    
    # Fetch user from database with organization info
    user_rows = q("""
        SELECT u.*, o.name as organization_name 
        FROM user u 
        JOIN organization o ON u.organization_id = o.id 
        WHERE u.id=%s
    """, (user_id,))
    if not user_rows:
        raise HTTPException(status_code=401, detail="User not found")
    
    user = user_rows[0]
    
    # Check if user is verified
    if not user.get("is_verified"):
        raise HTTPException(status_code=403, detail="Email not verified")
    
    return {
        "id": user["id"],
        "organization_id": user["organization_id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "is_verified": user["is_verified"],
        "organization_name": user.get("organization_name"),
    }


def invalidate_session(token: str) -> bool:
    """
    Invalidate a session by deleting it from the database.
    Returns True if session was found and deleted, False otherwise.
    """
    result = q("DELETE FROM session WHERE token=%s", (token,))
    return result is not None


def cleanup_expired_sessions() -> int:
    """
    Remove all expired sessions from the database.
    Returns the number of sessions deleted.
    """
    now = datetime.datetime.utcnow()
    result = q("DELETE FROM session WHERE expires_at < %s", (now,))
    return result if result else 0


# Optional: Get current user or None (for optional authentication)
def get_current_user_optional(access_token: Optional[str] = Cookie(None)) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, otherwise return None.
    """
    if not access_token:
        return None
    
    try:
        return get_current_user(access_token)
    except HTTPException:
        return None
