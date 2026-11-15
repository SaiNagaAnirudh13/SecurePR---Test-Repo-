import argparse
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parents[2] / "backend"
if backend_path.exists():
    sys.path.insert(0, str(backend_path))

from sqlalchemy import select

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models import Role, User


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update the initial EOMP administrator.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    if len(args.password) < 12:
        parser.error("Administrator passwords must contain at least 12 characters")

    with SessionLocal() as db:
        role = db.scalar(select(Role).where(Role.name == "admin"))
        if role is None:
            role = Role(name="admin", description="Full platform administration")
            db.add(role)
            db.flush()
        existing = db.scalar(select(User).where(User.email == args.email))
        if existing:
            parser.error("A user with that email already exists")
        db.add(
            User(
                email=args.email,
                full_name=args.name,
                password_hash=hash_password(args.password),
                role_id=role.id,
            )
        )
        db.commit()
    print(f"Administrator {args.email} created.")


if __name__ == "__main__":
    main()
