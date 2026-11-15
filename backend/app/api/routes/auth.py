from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.core.security import create_access_token, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.common import UserSummary

router = APIRouter()


@router.post("/token", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if (
        user is None
        or not user.is_active
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user.id, user.role.name)
    return TokenResponse(
        access_token=token,
        user=UserSummary(
            id=user.id, email=user.email, full_name=user.full_name, role=user.role.name
        ),
    )


@router.get("/me", response_model=UserSummary)
def get_me(user: CurrentUser) -> UserSummary:
    return UserSummary(id=user.id, email=user.email, full_name=user.full_name, role=user.role.name)
