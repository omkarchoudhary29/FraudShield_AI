from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.models.schemas import UserLogin, Token, User
from app.utils.auth import verify_password, create_access_token, get_current_user
from app.database import get_database
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Authenticate user and return JWT token"""
    db = get_database()
    user = await db.users.find_one({"email": credentials.email})
    
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    
    user["_id"] = str(user["_id"])
    user_obj = User(**user)
    
    return Token(access_token=access_token, user=user_obj)

@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user

@router.post("/logout")
async def logout():
    """Logout user (client should remove token)"""
    return {"message": "Successfully logged out"}
