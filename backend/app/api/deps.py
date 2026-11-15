from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import token_subject
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)
DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    user_id: UUID | None = token_subject(credentials.credentials)
    user = db.get(User, user_id) if user_id else None
    if user is None or not user.is_active:
        raise unauthorized
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
_current_user_dependency = Depends(get_current_user)


def require_roles(*roles: str) -> Callable[..., User]:
    def check_role(user: User = _current_user_dependency) -> User:
        if user.role.name not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return check_role


AdminUser = Annotated[User, Depends(require_roles("admin"))]
AdminOperationsUser = Annotated[User, Depends(require_roles("admin", "operations"))]
ReportingUser = Annotated[User, Depends(require_roles("admin", "analyst", "operations"))]
