from typing import get_type_hints
from uuid import UUID

from sqlalchemy.orm import Mapped

from app.models import Role, User


def test_models_retain_sqlalchemy_native_mapped_annotations() -> None:
    assert get_type_hints(User)["id"] == Mapped[UUID]
    assert get_type_hints(User)["role"] == Mapped[Role]
    assert get_type_hints(Role)["users"] == Mapped[list[User]]
