from decimal import Decimal

import pytest

from app.core.errors import DomainError
from app.core.security import hash_password
from app.models import Customer, InventoryItem, Product, Role, User
from app.services.orders import create_order, transition_order


@pytest.fixture
def order_context(db):
    role = Role(name="operations")
    db.add(role)
    db.flush()
    user = User(
        email="ops@example.com",
        full_name="Operations User",
        password_hash=hash_password("Correct-Horse-42!"),
        role_id=role.id,
    )
    customer = Customer(
        account_number="ACCT-1001",
        company_name="Northwind Distribution",
        contact_name="Morgan Lee",
        email="buyer@example.com",
        billing_address="100 Market Street, Boston, MA",
        shipping_address="200 Harbor Road, Boston, MA",
    )
    product = Product(
        sku="NW-DOCK-01",
        name="USB-C Dock",
        category="Peripherals",
        unit_price=Decimal("125.00"),
    )
    db.add_all([user, customer, product])
    db.flush()
    inventory = InventoryItem(
        product_id=product.id,
        warehouse_code="BOS-01",
        quantity_on_hand=10,
        quantity_reserved=0,
        reorder_point=2,
    )
    db.add(inventory)
    db.commit()
    return user, customer, product, inventory


def test_order_reserves_inventory_and_computes_tax(db, order_context):
    user, customer, product, inventory = order_context

    order = create_order(
        db,
        customer_id=customer.id,
        user_id=user.id,
        lines=[(product.id, 2)],
        notes="Deliver before close",
    )

    db.refresh(inventory)
    assert order.status == "confirmed"
    assert order.subtotal == Decimal("250.00")
    assert order.tax_amount == Decimal("20.63")
    assert order.total_amount == Decimal("270.63")
    assert inventory.quantity_reserved == 2
    assert order.items[0].line_total == Decimal("250.00")


def test_order_fails_without_sufficient_inventory(db, order_context):
    user, customer, product, _inventory = order_context

    with pytest.raises(DomainError, match="Insufficient inventory"):
        create_order(
            db,
            customer_id=customer.id,
            user_id=user.id,
            lines=[(product.id, 11)],
            notes="",
        )


def test_cancellation_releases_reserved_inventory(db, order_context):
    user, customer, product, inventory = order_context
    order = create_order(
        db,
        customer_id=customer.id,
        user_id=user.id,
        lines=[(product.id, 3)],
        notes="",
    )

    cancelled = transition_order(db, order=order, new_status="cancelled", actor_id=user.id)

    db.refresh(inventory)
    assert cancelled.status == "cancelled"
    assert inventory.quantity_reserved == 0


def test_shipment_dispatch_consumes_reserved_stock(db, order_context):
    user, customer, product, inventory = order_context
    order = create_order(
        db,
        customer_id=customer.id,
        user_id=user.id,
        lines=[(product.id, 3)],
        notes="",
    )
    transition_order(db, order=order, new_status="processing", actor_id=user.id)

    shipped = transition_order(db, order=order, new_status="shipped", actor_id=user.id)

    db.refresh(inventory)
    assert shipped.status == "shipped"
    assert shipped.shipment is not None
    assert shipped.shipment.shipped_at is not None
    assert inventory.quantity_on_hand == 7
    assert inventory.quantity_reserved == 0


def test_order_allocates_across_warehouses_and_cancellation_releases_each_reservation(
    db, order_context
):
    user, customer, product, first_inventory = order_context
    second_inventory = InventoryItem(
        product_id=product.id,
        warehouse_code="NYC-01",
        quantity_on_hand=5,
        quantity_reserved=0,
        reorder_point=1,
    )
    db.add(second_inventory)
    db.commit()

    order = create_order(
        db,
        customer_id=customer.id,
        user_id=user.id,
        lines=[(product.id, 12)],
        notes="",
    )

    allocations = {item.warehouse_code: item.quantity for item in order.items}
    db.refresh(first_inventory)
    db.refresh(second_inventory)
    assert allocations == {"BOS-01": 10, "NYC-01": 2}
    assert first_inventory.quantity_reserved == 10
    assert second_inventory.quantity_reserved == 2

    cancelled = transition_order(db, order=order, new_status="cancelled", actor_id=user.id)

    db.refresh(first_inventory)
    db.refresh(second_inventory)
    assert cancelled.status == "cancelled"
    assert first_inventory.quantity_reserved == 0
    assert second_inventory.quantity_reserved == 0


def test_order_rejects_when_aggregate_warehouse_stock_is_insufficient(db, order_context):
    user, customer, product, first_inventory = order_context
    second_inventory = InventoryItem(
        product_id=product.id,
        warehouse_code="NYC-01",
        quantity_on_hand=5,
        quantity_reserved=0,
        reorder_point=1,
    )
    db.add(second_inventory)
    db.commit()

    with pytest.raises(DomainError, match="Insufficient inventory"):
        create_order(
            db,
            customer_id=customer.id,
            user_id=user.id,
            lines=[(product.id, 16)],
            notes="",
        )

    db.refresh(first_inventory)
    db.refresh(second_inventory)
    assert first_inventory.quantity_reserved == 0
    assert second_inventory.quantity_reserved == 0


def test_shipment_consumes_stock_from_each_allocated_warehouse(db, order_context):
    user, customer, product, first_inventory = order_context
    second_inventory = InventoryItem(
        product_id=product.id,
        warehouse_code="NYC-01",
        quantity_on_hand=5,
        quantity_reserved=0,
        reorder_point=1,
    )
    db.add(second_inventory)
    db.commit()
    order = create_order(
        db,
        customer_id=customer.id,
        user_id=user.id,
        lines=[(product.id, 12)],
        notes="",
    )
    transition_order(db, order=order, new_status="processing", actor_id=user.id)

    shipped = transition_order(db, order=order, new_status="shipped", actor_id=user.id)

    db.refresh(first_inventory)
    db.refresh(second_inventory)
    assert shipped.status == "shipped"
    assert first_inventory.quantity_on_hand == 0
    assert second_inventory.quantity_on_hand == 3
    assert first_inventory.quantity_reserved == 0
    assert second_inventory.quantity_reserved == 0


def test_invalid_status_transition_is_rejected(db, order_context):
    user, customer, product, _inventory = order_context
    order = create_order(
        db,
        customer_id=customer.id,
        user_id=user.id,
        lines=[(product.id, 1)],
        notes="",
    )

    with pytest.raises(DomainError, match="Cannot transition"):
        transition_order(db, order=order, new_status="delivered", actor_id=user.id)
