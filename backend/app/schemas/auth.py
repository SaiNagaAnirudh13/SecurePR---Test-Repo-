from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.schemas.common import UserSummary

EmailAddress = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
]


class LoginRequest(BaseModel):
    email: EmailAddress
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSummary
