from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from auth.jwt_handler import verify_token

# ========================
# OAuth2 SCHEME
# ========================
# This tells FastAPI to look for a Bearer token in the Authorization header.
# tokenUrl="auth/login" points Swagger UI to the correct login endpoint.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency for protected routes.
    
    Flow:
    1. Extract the Bearer token from the request header.
    2. Decode and verify the token using verify_token().
    3. Look up the user in the database by user_id.
    4. If anything fails, raise 401 Unauthorized.
    
    Returns:
        The authenticated User ORM object.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Step 1: Verify the token and extract the user_id
    user_id_str = verify_token(token)
    if user_id_str is None:
        raise credentials_exception
    
    # Step 2: Find the user in the database
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user
