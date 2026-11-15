from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.entities import (  # noqa: E402
    AuditLog,
    Customer,
    InventoryItem,
    Notification,
    Order,
    OrderItem,
    Payment,
    Product,
    Role,
    Shipment,
    User,
)

__all__ = [
    "AuditLog",
    "Base",
    "Customer",
    "InventoryItem",
    "Notification",
    "Order",
    "OrderItem",
    "Payment",
    "Product",
    "Role",
    "Shipment",
    "User",
]
