from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator

from app.schemas.common import ORMModel

Code = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=50)]


class CustomerCreate(BaseModel):
    account_number: Code
    company_name: str = Field(min_length=2, max_length=180)
    contact_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=40)
    billing_address: str = Field(min_length=5, max_length=2000)
    shipping_address: str = Field(min_length=5, max_length=2000)


class CustomerRead(ORMModel):
    id: UUID
    account_number: str
    company_name: str
    contact_name: str
    email: str
    phone: str | None
    billing_address: str
    shipping_address: str
    is_active: bool


class ProductCreate(BaseModel):
    sku: Code
    name: str = Field(min_length=2, max_length=180)
    description: str = Field(default="", max_length=4000)
    category: str = Field(min_length=2, max_length=80)
    unit_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")


class ProductRead(ORMModel):
    id: UUID
    sku: str
    name: str
    description: str
    category: str
    unit_price: Decimal
    currency: str
    is_active: bool


class InventoryAdjustment(BaseModel):
    product_id: UUID
    warehouse_code: Code
    quantity_delta: int = Field(ge=-100000, le=100000)
    reorder_point: int = Field(default=0, ge=0, le=100000)

    @field_validator("quantity_delta")
    @classmethod
    def reject_zero_adjustment(cls, value: int) -> int:
        if value == 0:
            raise ValueError("quantity_delta must not be zero")
        return value


class InventoryRead(BaseModel):
    id: UUID
    product_id: UUID
    sku: str
    product_name: str
    warehouse_code: str
    quantity_on_hand: int
    quantity_reserved: int
    available_quantity: int
    reorder_point: int
