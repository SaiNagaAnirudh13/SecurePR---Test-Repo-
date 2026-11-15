from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import AdminOperationsUser, CurrentUser, DbSession
from app.core.errors import DomainError
from app.models import Order, Payment
from app.repositories.orders import list_orders
from app.schemas.orders import (
    OrderCreate,
    OrderRead,
    OrderStatusUpdate,
    PaymentIntentCreate,
    PaymentRead,
)
from app.services.orders import create_order, create_payment_intent, get_order, transition_order

router = APIRouter()


def _domain_error(error: DomainError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.get("", response_model=list[OrderRead])
def get_orders(
    db: DbSession,
    user: CurrentUser,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    status: Literal["confirmed", "processing", "shipped", "delivered", "cancelled"] | None = None,
    customer_id: UUID | None = None,
) -> list[Order]:
    return list_orders(
        db,
        offset=offset,
        limit=limit,
        status=status,
        customer_id=customer_id,
    )


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def post_order(payload: OrderCreate, db: DbSession, user: CurrentUser) -> Order:
    try:
        return create_order(
            db,
            customer_id=payload.customer_id,
            user_id=user.id,
            lines=[(item.product_id, item.quantity) for item in payload.items],
            notes=payload.notes,
        )
    except DomainError as error:
        db.rollback()
        raise _domain_error(error) from error


@router.get("/{order_id}", response_model=OrderRead)
def get_order_detail(order_id: UUID, db: DbSession, user: CurrentUser) -> Order:
    try:
        return get_order(db, order_id)
    except DomainError as error:
        raise _domain_error(error) from error


@router.patch("/{order_id}/status", response_model=OrderRead)
def patch_order_status(
    order_id: UUID,
    payload: OrderStatusUpdate,
    db: DbSession,
    user: AdminOperationsUser,
) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order was not found")
    try:
        return transition_order(db, order=order, new_status=payload.status, actor_id=user.id)
    except DomainError as error:
        db.rollback()
        raise _domain_error(error) from error


@router.post(
    "/{order_id}/payments", response_model=PaymentRead, status_code=status.HTTP_201_CREATED
)
def post_payment_intent(
    order_id: UUID,
    payload: PaymentIntentCreate,
    db: DbSession,
    user: AdminOperationsUser,
) -> Payment:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order was not found")
    try:
        return create_payment_intent(db, order=order, provider=payload.provider, actor_id=user.id)
    except DomainError as error:
        db.rollback()
        raise _domain_error(error) from error
