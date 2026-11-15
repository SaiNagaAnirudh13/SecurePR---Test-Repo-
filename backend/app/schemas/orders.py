from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class OrderLineCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0, le=10000)


class OrderCreate(BaseModel):
    customer_id: UUID
    items: list[OrderLineCreate] = Field(min_length=1, max_length=100)
    notes: str = Field(default="", max_length=2000)


class OrderItemRead(ORMModel):
    id: UUID
    product_id: UUID
    sku: str
    product_name: str
    warehouse_code: str | None
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class ShipmentRead(ORMModel):
    id: UUID
    carrier: str
    tracking_number: str | None
    status: str
    shipped_at: datetime | None
    delivered_at: datetime | None


class OrderRead(ORMModel):
    id: UUID
    order_number: str
    customer_id: UUID
    status: str
    currency: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    notes: str
    created_at: datetime
    items: list[OrderItemRead]
    shipment: ShipmentRead | None


class OrderStatusUpdate(BaseModel):
    status: Literal["processing", "shipped", "delivered", "cancelled"]


class PaymentIntentCreate(BaseModel):
    provider: str = Field(default="manual", min_length=2, max_length=60)


class PaymentRead(ORMModel):
    id: UUID
    provider: str
    provider_reference: str | None
    amount: Decimal
    currency: str
    status: str
    created_at: datetime
