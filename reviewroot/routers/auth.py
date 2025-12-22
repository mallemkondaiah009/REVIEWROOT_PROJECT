from fastapi import APIRouter, HTTPException, Depends, status, Response
from datetime import datetime
from bson import ObjectId
from reviewroot.models.user import UserRegister, UserLogin, UserResponse, UserUpdate
from reviewroot.database import users_collection
from reviewroot.utils.auth_utils import hash_password, verify_password, create_access_token, create_refresh_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    # Check if email exists
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(400, "Email already registered")
    
    # Check if username exists
    if await users_collection.find_one({"username": user.username}):
        raise HTTPException(400, "Username already taken")
    
    # Create user document
    user_doc = {
        "username": user.username,
        "email": user.email,
        "passwordHash": hash_password(user.password),
        "avatar": None,
        "bio": None,
        "followers": [],
        "following": [],
        "createdAt": datetime.utcnow()
    }
    
    result = await users_collection.insert_one(user_doc)
    
    return {
        "message": "User registered successfully",
        "userId": str(result.inserted_id)
    }

@router.post("/login")
async def login(credentials: UserLogin, response: Response):
    user = await users_collection.find_one({"email": credentials.email})
    
    if not user or not verify_password(credentials.password, user["passwordHash"]):
        raise HTTPException(401, "Invalid email or password")
    
    access_token = create_access_token(str(user["_id"]))
    refresh_token = create_refresh_token(str(user['_id']))

    response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=24 * 60 * 60
        )
    response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=7 * 24 * 60 * 60
        )
    
    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "userId": str(user["_id"])
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["_id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "avatar": current_user.get("avatar"),
        "bio": current_user.get("bio"),
        "followersCount": len(current_user.get("followers", [])),
        "followingCount": len(current_user.get("following", [])),
        "createdAt": current_user["createdAt"]
    }

@router.put("/me", response_model=UserResponse)
async def update_me(update: UserUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {}
    
    if update.bio is not None:
        update_data["bio"] = update.bio
    
    if update.avatar is not None:
        update_data["avatar"] = update.avatar
    
    if update_data:
        await users_collection.update_one(
            {"_id": ObjectId(current_user["_id"])},
            {"$set": update_data}
        )
    
    # Get updated user
    user = await users_collection.find_one({"_id": ObjectId(current_user["_id"])})
    
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "avatar": user.get("avatar"),
        "bio": user.get("bio"),
        "followersCount": len(user.get("followers", [])),
        "followingCount": len(user.get("following", [])),
        "createdAt": user["createdAt"]
    }

@router.get("/users/{username}", response_model=UserResponse)
async def get_user(username: str):
    user = await users_collection.find_one({"username": username})
    
    if not user:
        raise HTTPException(404, "User not found")
    
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "avatar": user.get("avatar"),
        "bio": user.get("bio"),
        "followersCount": len(user.get("followers", [])),
        "followingCount": len(user.get("following", [])),
        "createdAt": user["createdAt"]
    }

# @router.post("/refresh")
# async def refresh_access_token(refresh_token: str = Body(..., embed=True)):
#     """
#     Get new access token using refresh token
    
#     Body: {"refresh_token": "your_refresh_token_here"}
#     """
#     user_id = verify_refresh_token(refresh_token)
    
#     # Check if user still exists
#     user = await users_collection.find_one({"_id": ObjectId(user_id)})
#     if not user:
#         raise HTTPException(404, "User not found")
    
#     # Create new access token
#     new_access_token = create_token(user_id)
    
#     return {
#         "message": "Token refreshed successfully",
#         "accessToken": new_access_token
#     }