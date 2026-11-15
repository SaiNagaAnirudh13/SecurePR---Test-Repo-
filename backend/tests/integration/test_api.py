from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Customer, InventoryItem, Product


def test_authentication_and_protected_catalog(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert client.get("/api/v1/auth/me", headers=auth_headers).status_code == 200
    assert client.get("/api/v1/products").status_code == 401
    assert client.get("/health").json() == {"status": "ok"}


def test_order_api_creates_order_and_audit_event(
    client: TestClient, db: Session, auth_headers: dict[str, str]
) -> None:
    customer = Customer(
        account_number="ACCT-2001",
        company_name="Contoso Retail",
        contact_name="Jamie Park",
        email="procurement@example.com",
        billing_address="10 Main Street, Seattle, WA",
        shipping_address="20 Pine Street, Seattle, WA",
    )
    product = Product(
        sku="CON-MON-27",
        name="27-inch Monitor",
        category="Displays",
        unit_price=Decimal("299.99"),
    )
    db.add_all([customer, product])
    db.flush()
    db.add(
        InventoryItem(
            product_id=product.id,
            warehouse_code="SEA-01",
            quantity_on_hand=1,
            quantity_reserved=0,
            reorder_point=1,
        )
    )
    db.add(
        InventoryItem(
            product_id=product.id,
            warehouse_code="PDX-01",
            quantity_on_hand=1,
            quantity_reserved=0,
            reorder_point=1,
        )
    )
    db.commit()

    response = client.post(
        "/api/v1/orders",
        headers=auth_headers,
        json={
            "customer_id": str(customer.id),
            "items": [{"product_id": str(product.id), "quantity": 2}],
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "confirmed"
    assert response.json()["total_amount"] == "649.48"
    assert {item["warehouse_code"]: item["quantity"] for item in response.json()["items"]} == {
        "PDX-01": 1,
        "SEA-01": 1,
    }
