from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models import Customer, InventoryItem, Product, Role, User


def test_authentication_and_protected_catalog(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    assert client.get("/api/v1/auth/me", headers=auth_headers).status_code == 200
    assert client.get("/api/v1/products").status_code == 401
    assert client.get("/health").json() == {"status": "ok"}


def test_login_preserves_bearer_response_contract(client: TestClient, admin_user: User) -> None:
    response = client.post(
        "/api/v1/auth/token",
        json={"email": admin_user.email, "password": "Correct-Horse-42!"},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["token_type"] == "bearer"
    assert result["user"] == {
        "id": str(admin_user.id),
        "email": admin_user.email,
        "full_name": admin_user.full_name,
        "role": "admin",
    }
    assert (
        client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {result['access_token']}"},
        ).status_code
        == 200
    )


def test_login_rejects_invalid_credentials(client: TestClient, admin_user: User) -> None:
    response = client.post(
        "/api/v1/auth/token",
        json={"email": admin_user.email, "password": "Wrong-password"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


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
            quantity_on_hand=5,
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


def test_order_reads_require_reporting_role(
    client: TestClient,
    db: Session,
    auth_headers: dict[str, str],
) -> None:
    role = Role(name="viewer", description="Non-reporting user")
    db.add(role)
    db.flush()
    viewer = User(
        email="viewer@example.com",
        full_name="Read-only Viewer",
        password_hash="unused",
        role_id=role.id,
    )
    db.add(viewer)
    db.commit()
    viewer_headers = {"Authorization": f"Bearer {create_access_token(viewer.id, role.name)}"}

    assert client.get("/api/v1/orders", headers=auth_headers).status_code == 200
    assert client.get("/api/v1/orders", headers=viewer_headers).status_code == 403
    assert client.get(f"/api/v1/orders/{uuid4()}", headers=viewer_headers).status_code == 403
