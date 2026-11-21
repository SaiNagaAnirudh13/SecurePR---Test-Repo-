from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.orders import OrderCreate


def test_order_create_accepts_maximum_total_quantity() -> None:
    payload = OrderCreate(
        customer_id=uuid4(),
        items=[
            {"product_id": uuid4(), "quantity": 6000},
            {"product_id": uuid4(), "quantity": 4000},
        ],
    )

    assert sum(item.quantity for item in payload.items) == 10000


def test_order_create_rejects_excessive_total_quantity() -> None:
    with pytest.raises(ValidationError, match="total order quantity must not exceed 10000"):
        OrderCreate(
            customer_id=uuid4(),
            items=[
                {"product_id": uuid4(), "quantity": 6000},
                {"product_id": uuid4(), "quantity": 4001},
            ],
        )
