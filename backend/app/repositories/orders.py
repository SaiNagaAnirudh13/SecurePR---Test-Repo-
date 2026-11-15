from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Order


def list_orders(db: Session, *, offset: int = 0, limit: int = 50) -> list[Order]:
    return list(
        db.scalars(
            select(Order)
            .options(joinedload(Order.items), joinedload(Order.shipment))
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        .unique()
        .all()
    )
