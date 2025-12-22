from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId

class User(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    username: str
    email: EmailStr
    passwordHash: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    followers: list[str] = []
    following: list[str] = []
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }

# Request Models (for API input)
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscore allowed)')
        return v.lower()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    followersCount: int = 0
    followingCount: int = 0
    createdAt: datetime

class UserUpdate(BaseModel):
    bio: Optional[str] = Field(None, max_length=200)
    avatar: Optional[str] = None