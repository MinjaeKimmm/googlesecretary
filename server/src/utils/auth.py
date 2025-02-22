from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.config.settings import get_settings
from src.config.constants import GOOGLE_OAUTH_TOKEN_URL, GOOGLE_USERINFO_URL
from src.models.user import User
from src.services.database.mongodb import get_user_by_email

settings = get_settings()

async def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify Google OAuth token and return user info"""
    if not token:
        print("No token provided")
        return None
        
    print(f"Verifying token with Google: {token[:20]}...")
    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(GOOGLE_USERINFO_URL, headers=headers)
            print(f"Google response status: {response.status_code}")
            
            if response.status_code == 401:
                print("Token expired or invalid")
                return None
            elif response.status_code != 200:
                print(f"Unexpected response: {response.status_code} - {response.text}")
                return None
                
            user_info = response.json()
            print(f"Google user info: {user_info}")
            return user_info
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        return None

async def refresh_google_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """Refresh Google OAuth token"""
    async with httpx.AsyncClient() as client:
        data = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        response = await client.post(GOOGLE_OAUTH_TOKEN_URL, data=data)
        if response.status_code == 200:
            return response.json()
        return None

def is_token_expired(expiry: datetime) -> bool:
    """Check if token is expired or about to expire in 5 minutes"""
    return datetime.utcnow() + timedelta(minutes=5) >= expiry

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from token"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        # First verify the token with Google
        user_info = await verify_google_token(token)
        if not user_info or "email" not in user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = await get_user_by_email(user_info["email"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        # Check token expiry
        if user.token_expiry and is_token_expired(user.token_expiry):
            if not user.refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired and no refresh token available",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            # Try to refresh the token
            new_tokens = await refresh_google_token(user.refresh_token)
            if not new_tokens:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to refresh token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            # Update user tokens
            from src.services.database.mongodb import update_user_tokens
            await update_user_tokens(
                user.email,
                new_tokens["access_token"],
                refresh_token=new_tokens.get("refresh_token"),
                token_expiry=datetime.utcnow() + timedelta(seconds=new_tokens["expires_in"])
            )
            
            # Get updated user
            user = await get_user_by_email(user_info["email"])
            
        return user
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
