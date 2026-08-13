from fastapi import APIRouter, Depends, HTTPException, status
from app.api.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.api.deps import get_current_user
from app.security.auth import get_user_by_username, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    user = get_user_by_username(request.username)
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
        
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"], "user_id": user["user_id"]}
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        username=user["username"],
        role=user["role"],
        user_id=user["user_id"]
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        user_id=current_user["user_id"],
        username=current_user["username"],
        role=current_user["role"],
        full_name=current_user.get("full_name")
    )
