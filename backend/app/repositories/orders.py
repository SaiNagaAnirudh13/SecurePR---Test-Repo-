from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Order


def list_orders(
    db: Session,
    *,
    offset: int = 0,
    limit: int = 50,
    status: str | None = None,
    customer_id: UUID | None = None,
) -> list[Order]:
    query = select(Order).options(joinedload(Order.items), joinedload(Order.shipment))
    if status is not None:
        query = query.where(Order.status == status)
    if customer_id is not None:
        query = query.where(Order.customer_id == customer_id)
    return list(
        db.scalars(query.order_by(Order.created_at.desc()).offset(offset).limit(limit))
        .unique()
        .all()
    )
