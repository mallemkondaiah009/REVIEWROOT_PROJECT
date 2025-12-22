from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from reviewroot import config
from reviewroot.database import users_collection

pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')
security = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        'sub': user_id,
        'exp': expire,
        'type': 'refresh'
    }
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

async def get_current_user(request: Request):
    
        token = request.cookies.get('access_token')
        if not token:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
        try: 
            payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
            
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
            
            if not user:
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
            
            user["_id"] = str(user["_id"])
            return user
        
        except JWTError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
