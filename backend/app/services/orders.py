from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload

from app.core.errors import DomainError
from app.models import (
    Customer,
    InventoryItem,
    Notification,
    Order,
    OrderItem,
    Payment,
    Product,
    Shipment,
)
from app.models.entities import utc_now
from app.services.audit import record_audit

CENT = Decimal("0.01")
TAX_RATE = Decimal("0.0825")
ALLOWED_TRANSITIONS = {
    "confirmed": {"processing", "cancelled"},
    "processing": {"shipped", "cancelled"},
    "shipped": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}


def create_order(
    db: Session, *, customer_id: UUID, user_id: UUID, lines: list[tuple[UUID, int]], notes: str
) -> Order:
    customer = db.get(Customer, customer_id)
    if customer is None or not customer.is_active:
        raise DomainError("Active customer was not found", 404)

    normalized: dict[UUID, int] = {}
    for product_id, quantity in lines:
        normalized[product_id] = normalized.get(product_id, 0) + quantity

    products: dict[UUID, Product] = {}
    stock: dict[UUID, InventoryItem] = {}
    for product_id, quantity in normalized.items():
        product = db.scalar(
            select(Product).where(Product.id == product_id, Product.is_active.is_(True))
        )
        if product is None:
            raise DomainError(f"Active product {product_id} was not found", 404)
        inventory = db.scalar(
            select(InventoryItem)
            .where(InventoryItem.product_id == product_id)
            .order_by(InventoryItem.warehouse_code)
            .with_for_update()
        )
        if inventory is None or inventory.available_quantity < quantity:
            raise DomainError(f"Insufficient inventory for SKU {product.sku}", 409)
        products[product_id] = product
        stock[product_id] = inventory

    subtotal = sum(
        (products[product_id].unit_price * quantity for product_id, quantity in normalized.items()),
        start=Decimal("0"),
    ).quantize(CENT, rounding=ROUND_HALF_UP)
    currencies = {product.currency for product in products.values()}
    if len(currencies) != 1:
        raise DomainError("All products in an order must use the same currency", 409)
    tax_amount = (subtotal * TAX_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
    order = Order(
        order_number=f"EO-{uuid4().hex[:12].upper()}",
        customer_id=customer_id,
        created_by_id=user_id,
        status="confirmed",
        currency=next(iter(products.values())).currency,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=subtotal + tax_amount,
        notes=notes,
    )
    db.add(order)
    db.flush()

    for product_id, quantity in normalized.items():
        product = products[product_id]
        inventory = stock[product_id]
        reserved_id = db.execute(
            update(InventoryItem)
            .where(
                InventoryItem.id == inventory.id,
                InventoryItem.quantity_on_hand - InventoryItem.quantity_reserved >= quantity,
            )
            .values(quantity_reserved=InventoryItem.quantity_reserved + quantity)
            .returning(InventoryItem.id)
        ).scalar_one_or_none()
        if reserved_id is None:
            raise DomainError(f"Inventory changed while reserving SKU {product.sku}", 409)
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                sku=product.sku,
                product_name=product.name,
                quantity=quantity,
                unit_price=product.unit_price,
                line_total=product.unit_price * quantity,
            )
        )

    db.add(
        Notification(
            recipient=customer.email,
            event_type="order.confirmed",
            payload={"order_number": order.order_number, "total": str(order.total_amount)},
        )
    )
    record_audit(
        db,
        actor_id=user_id,
        action="order.created",
        resource_type="order",
        resource_id=str(order.id),
        details={"order_number": order.order_number, "item_count": len(normalized)},
    )
    db.commit()
    return get_order(db, order.id)


def get_order(db: Session, order_id: UUID) -> Order:
    order = db.scalar(
        select(Order)
        .options(joinedload(Order.items), joinedload(Order.shipment))
        .where(Order.id == order_id)
    )
    if order is None:
        raise DomainError("Order was not found", 404)
    return order


def transition_order(db: Session, *, order: Order, new_status: str, actor_id: UUID) -> Order:
    if new_status not in ALLOWED_TRANSITIONS.get(order.status, set()):
        raise DomainError(f"Cannot transition order from {order.status} to {new_status}", 409)
    previous_status = order.status
    if new_status == "cancelled":
        for item in order.items:
            inventory = db.scalar(
                select(InventoryItem)
                .where(InventoryItem.product_id == item.product_id)
                .order_by(InventoryItem.warehouse_code)
                .with_for_update()
            )
            if inventory is None or inventory.quantity_reserved < item.quantity:
                raise DomainError(f"Reserved inventory is inconsistent for SKU {item.sku}", 409)
            inventory.quantity_reserved -= item.quantity
    elif new_status == "shipped":
        for item in order.items:
            inventory = db.scalar(
                select(InventoryItem)
                .where(InventoryItem.product_id == item.product_id)
                .order_by(InventoryItem.warehouse_code)
                .with_for_update()
            )
            if (
                inventory is None
                or inventory.quantity_reserved < item.quantity
                or inventory.quantity_on_hand < item.quantity
            ):
                raise DomainError(f"Reserved inventory is inconsistent for SKU {item.sku}", 409)
            inventory.quantity_reserved -= item.quantity
            inventory.quantity_on_hand -= item.quantity
    order.status = new_status
    if new_status == "shipped":
        order.shipment = Shipment(status="shipped", shipped_at=utc_now())
    elif new_status == "delivered" and order.shipment is not None:
        order.shipment.status = "delivered"
        order.shipment.delivered_at = utc_now()
    record_audit(
        db,
        actor_id=actor_id,
        action="order.status_changed",
        resource_type="order",
        resource_id=str(order.id),
        details={"from": previous_status, "to": new_status},
    )
    db.commit()
    return get_order(db, order.id)


def create_payment_intent(db: Session, *, order: Order, provider: str, actor_id: UUID) -> Payment:
    if order.status == "cancelled":
        raise DomainError("Cannot create payment for a cancelled order", 409)
    payment = Payment(
        order_id=order.id,
        provider=provider,
        amount=order.total_amount,
        currency=order.currency,
        status="pending",
    )
    db.add(payment)
    record_audit(
        db,
        actor_id=actor_id,
        action="payment.intent_created",
        resource_type="order",
        resource_id=str(order.id),
        details={"provider": provider, "amount": str(order.total_amount)},
    )
    db.commit()
    db.refresh(payment)
    return payment
